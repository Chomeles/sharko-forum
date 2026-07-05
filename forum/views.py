import math

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Exists, F, OuterRef, Q, Subquery
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import PostForm, SignupForm, ThreadForm
from .models import Category, Post, Thread

POSTS_PER_PAGE = 20
THREADS_PER_PAGE = 25


def _author_stats(user, author_ids):
    """{user_id: User annotated with msg_count + rep} for the given ids, in one query."""
    users = User.objects.filter(id__in=author_ids).annotate(
        msg_count=Count("posts", distinct=True),
        rep=Count("posts__likers"),
    )
    return {u.id: u for u in users}


def index(request):
    # "Last post" cell = the most recent POST in the category (its author + time),
    # not the newest thread's starter.
    last_post = Post.objects.filter(thread__category=OuterRef("pk")).order_by("-created", "-pk")
    categories = (
        Category.objects.annotate(
            thread_count=Count("threads", distinct=True),
            post_count=Count("threads__posts"),
            last_post_at=Subquery(last_post.values("created")[:1]),
            last_author=Subquery(last_post.values("author__username")[:1]),
            last_thread_id=Subquery(last_post.values("thread_id")[:1]),
            last_thread_title=Subquery(last_post.values("thread__title")[:1]),
        )
        .order_by("section", "position", "name")
    )
    stats = {
        "members": User.objects.count(),
        "threads": Thread.objects.count(),
        "posts": Post.objects.count(),
        "newest": User.objects.order_by("-date_joined").first(),
    }
    return render(request, "forum/index.html", {"categories": categories, "stats": stats})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    threads = category.threads.select_related("author").annotate(post_count=Count("posts"))
    page = Paginator(threads, THREADS_PER_PAGE).get_page(request.GET.get("page"))
    return render(request, "forum/category.html", {"category": category, "page": page})


def thread_detail(request, pk):
    thread = get_object_or_404(Thread.objects.select_related("category", "author"), pk=pk)
    # ponytail: racy increment, fine for a view counter; no per-visitor dedup
    Thread.objects.filter(pk=pk).update(views=F("views") + 1)
    thread.views += 1

    posts = thread.posts.select_related("author").annotate(like_count=Count("likers"))
    if request.user.is_authenticated:
        liked = Post.likers.through.objects.filter(post_id=OuterRef("pk"), user_id=request.user.id)
        posts = posts.annotate(liked_by_me=Exists(liked))
    page = Paginator(posts, POSTS_PER_PAGE).get_page(request.GET.get("page"))

    stats = _author_stats(request.user, {p.author_id for p in page})
    for post in page:
        post.author_stats = stats.get(post.author_id)

    return render(
        request, "forum/thread.html", {"thread": thread, "page": page, "form": PostForm()}
    )


@login_required
def new_thread(request, slug):
    category = get_object_or_404(Category, slug=slug)
    form = ThreadForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            thread = Thread.objects.create(
                category=category, author=request.user, title=form.cleaned_data["title"]
            )
            Post.objects.create(
                thread=thread, author=request.user, body=form.cleaned_data["body"]
            )
        return redirect(thread)
    return render(request, "forum/thread_form.html", {"category": category, "form": form})


@login_required
@require_POST
def reply(request, pk):
    thread = get_object_or_404(Thread, pk=pk)
    if thread.is_locked:
        return HttpResponseForbidden("Thread is locked.")
    form = PostForm(request.POST)
    if not form.is_valid():
        # ponytail: textarea required+maxlength catch this client-side; server just bounces
        return redirect(thread)
    post = form.save(commit=False)
    post.thread = thread
    post.author = request.user
    post.save()
    Thread.objects.filter(pk=pk).update(bumped=timezone.now())
    last_page = math.ceil(thread.posts.count() / POSTS_PER_PAGE)
    return redirect(f"{thread.get_absolute_url()}?page={last_page}#post-{post.pk}")


@login_required
@require_POST
def toggle_like(request, pk):
    post = get_object_or_404(Post.objects.select_related("thread"), pk=pk)
    if post.author_id == request.user.id:
        return JsonResponse({"error": "You can't rep your own post."}, status=400)
    if post.likers.filter(pk=request.user.id).exists():
        post.likers.remove(request.user)
        liked = False
    else:
        post.likers.add(request.user)
        liked = True
    count = post.likers.count()
    if request.headers.get("x-requested-with") == "fetch":
        return JsonResponse({"liked": liked, "count": count})
    # No-JS fallback: land back on the post's own page, not page 1.
    pos = post.thread.posts.filter(
        Q(created__lt=post.created) | Q(created=post.created, pk__lte=post.pk)
    ).count()
    page = math.ceil(pos / POSTS_PER_PAGE)
    return redirect(f"{post.thread.get_absolute_url()}?page={page}#post-{post.pk}")


@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post.objects.select_related("thread"), pk=pk)
    if post.author_id != request.user.id and not request.user.is_staff:
        return HttpResponseForbidden("Not your post.")
    # Locking freezes content (reply() enforces the same) — staff stay exempt.
    if post.thread.is_locked and not request.user.is_staff:
        return HttpResponseForbidden("Thread is locked.")
    form = PostForm(request.POST or None, instance=post)
    if request.method == "POST" and form.is_valid():
        post = form.save(commit=False)
        post.edited = timezone.now()
        post.save()
        return redirect(post.thread)
    return render(request, "forum/post_edit.html", {"form": form, "post": post})


def search(request):
    q = (request.GET.get("q") or "").strip()
    threads = []
    if q:
        # ponytail: LIKE search; swap for Postgres SearchVector/GIN when volume warrants
        # Two steps on purpose: annotating Count("posts") on the filtered query would
        # reuse the body-match join and undercount, so match first, then count clean.
        match_ids = list(
            Thread.objects.filter(Q(title__icontains=q) | Q(posts__body__icontains=q))
            .values_list("pk", flat=True)
            .distinct()[:50]
        )
        threads = (
            Thread.objects.filter(pk__in=match_ids)
            .select_related("category", "author")
            .annotate(post_count=Count("posts"))
        )
    return render(request, "forum/search.html", {"q": q, "threads": threads})


def signup(request):
    if request.user.is_authenticated:
        return redirect("forum:index")
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("forum:index")
    return render(request, "registration/signup.html", {"form": form})
