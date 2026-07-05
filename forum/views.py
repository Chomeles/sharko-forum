import math

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Max
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import PostForm, SignupForm, ThreadForm
from .models import Category, Post, Thread

POSTS_PER_PAGE = 20
THREADS_PER_PAGE = 25


def index(request):
    categories = Category.objects.annotate(
        thread_count=Count("threads", distinct=True),
        last_activity=Max("threads__bumped"),
    )
    return render(request, "forum/index.html", {"categories": categories})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    threads = category.threads.select_related("author").annotate(post_count=Count("posts"))
    page = Paginator(threads, THREADS_PER_PAGE).get_page(request.GET.get("page"))
    return render(request, "forum/category.html", {"category": category, "page": page})


def thread_detail(request, pk):
    thread = get_object_or_404(Thread.objects.select_related("category", "author"), pk=pk)
    posts = thread.posts.select_related("author")
    page = Paginator(posts, POSTS_PER_PAGE).get_page(request.GET.get("page"))
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
def edit_post(request, pk):
    post = get_object_or_404(Post.objects.select_related("thread"), pk=pk)
    if post.author_id != request.user.id and not request.user.is_staff:
        return HttpResponseForbidden("Not your post.")
    form = PostForm(request.POST or None, instance=post)
    if request.method == "POST" and form.is_valid():
        post = form.save(commit=False)
        post.edited = timezone.now()
        post.save()
        return redirect(post.thread)
    return render(request, "forum/post_edit.html", {"form": form, "post": post})


def signup(request):
    if request.user.is_authenticated:
        return redirect("forum:index")
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("forum:index")
    return render(request, "registration/signup.html", {"form": form})
