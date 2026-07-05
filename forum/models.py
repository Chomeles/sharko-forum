from django.conf import settings
from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(unique=True)
    description = models.CharField(max_length=200, blank=True)
    # XenForo-style: nodes grouped under a section header on the index.
    section = models.CharField(max_length=60, default="General")
    icon = models.CharField(max_length=8, default="💬", help_text="Emoji shown as the node icon.")
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["section", "position", "name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("forum:category", args=[self.slug])


class Thread(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="threads")
    # PROTECT: ban spammers via is_active, don't delete users — deleting would
    # cascade away other people's replies inside their threads.
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="threads")
    title = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    # ponytail: denormalized last-activity, updated on reply; avoids Max() over posts per listing
    bumped = models.DateTimeField(auto_now_add=True)
    # ponytail: naive counter, no unique-visitor dedup; add a per-session guard if it matters
    views = models.PositiveIntegerField(default=0)
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_pinned", "-bumped"]
        indexes = [models.Index(fields=["category", "is_pinned", "bumped"])]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("forum:thread", args=[self.pk])


class Post(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="posts")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="posts")
    body = models.TextField(max_length=20000)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(null=True, blank=True)
    # Reputation = likes received. A user's rep = count of likers across their posts.
    likers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="liked_posts", blank=True)

    class Meta:
        ordering = ["created", "pk"]

    def __str__(self):
        return f"#{self.pk} by {self.author}"
