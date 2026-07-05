from django.contrib.auth import authenticate
from django.core.management import call_command
from django.test import TestCase

from forum.models import Post, Thread


class SeedDemoTest(TestCase):
    def test_seeds_once_and_is_idempotent(self):
        call_command("seed_demo")
        self.assertTrue(Thread.objects.exists())
        self.assertIsNotNone(authenticate(username="demo", password="demo"))
        welcome = Thread.objects.get(title__startswith="Welcome")
        self.assertTrue(welcome.is_pinned)
        self.assertIn("[hide]", welcome.posts.first().body)

        # second run must not duplicate
        threads, posts = Thread.objects.count(), Post.objects.count()
        call_command("seed_demo")
        self.assertEqual((threads, posts), (Thread.objects.count(), Post.objects.count()))
