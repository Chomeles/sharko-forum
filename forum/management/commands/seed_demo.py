"""Seed a fresh install with sample threads and a `demo`/`demo` login so a new
self-hoster sees a living forum (and can try posting/hiding/quoting) instead of empty
categories. Categories themselves come from the 0002/0004 data migrations, so this
reuses one rather than creating its own. Idempotent: does nothing once any thread
exists, so it is safe to run on every boot. Turn off in production with SEED_DEMO=0."""
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from forum.models import Category, Post, Thread

WELCOME = """[b]Welcome to your new forum![/b]

This is seeded demo content — delete it (or set SEED_DEMO=0) once you're set up.
A quick tour of what a post can do:

[quote=sharko]Replies can quote each other. Hit the Quote button on any post.[/quote]

Links work: [url]https://github.com/Chomeles/sharko-forum[/url]

And the signature move — content that only shows after you reply:
[hide]🎉 You unlocked this by replying. This is how "reply to see the link" forums work.[/hide]"""


class Command(BaseCommand):
    help = "Seed demo categories, a demo/demo login and sample posts (idempotent)."

    def handle(self, *args, **opts):
        if Thread.objects.exists():
            self.stdout.write("threads already exist — not seeding")
            return
        if not Category.objects.exists():
            self.stdout.write("no categories yet — run migrate first")
            return
        self._seed()
        self.stdout.write("seeded demo content (login: demo / demo)")

    def _seed(self):
        sharko = User.objects.create_user("sharko")
        sharko.set_unusable_password()  # content author, not a login
        sharko.save()
        demo = User.objects.create_user("demo", password="demo")

        # Reuse a migration-seeded category (prefer "general") rather than making our own.
        general = Category.objects.filter(slug="general").first() or Category.objects.first()

        welcome = Thread.objects.create(category=general, author=sharko,
                                        title="Welcome — try the formatting", is_pinned=True)
        Post.objects.create(thread=welcome, author=sharko, body=WELCOME)
        Post.objects.create(thread=welcome, author=demo,
                            body="Nice, the [hide] block is open for me now that I replied!")

        chat = Thread.objects.create(category=general, author=demo, title="Say hi 👋")
        Post.objects.create(thread=chat, author=demo, body="First! What are you self-hosting this for?")
