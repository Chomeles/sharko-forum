"""Send ONE anonymous install ping so the project can show an install count.

Sends only: a random UUID generated once per install (stored in the DB, not tied
to you or any user) and the app version. No IPs, no user data. Fire-and-forget.
Disable entirely with FORUM_TELEMETRY=off. Point elsewhere with TELEMETRY_URL.
"""
import json
import os
import urllib.request

from django.core.management.base import BaseCommand

from forum import __version__
from forum.models import SiteInstall

DEFAULT_URL = "https://sharko.icu/forum-stats/ping"
DISABLED = {"off", "0", "false", "no", "disabled"}


class Command(BaseCommand):
    help = "Send one anonymous install ping (opt out: FORUM_TELEMETRY=off)."

    def handle(self, *args, **opts):
        if os.environ.get("FORUM_TELEMETRY", "on").strip().lower() in DISABLED:
            self.stdout.write("telemetry disabled — not pinging")
            return
        install, _ = SiteInstall.objects.get_or_create(pk=1)
        url = os.environ.get("TELEMETRY_URL") or DEFAULT_URL
        payload = json.dumps({"id": str(install.instance_id), "version": __version__}).encode()
        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                # Cloudflare blocks the default "Python-urllib" UA; identify honestly.
                "User-Agent": f"sharko-forum/{__version__} (+https://github.com/Chomeles/sharko-forum)",
            },
        )
        try:
            urllib.request.urlopen(req, timeout=5).read()
            self.stdout.write("install ping sent")
        except Exception as exc:  # never let telemetry break a deploy
            self.stderr.write(f"ping failed (ignored): {exc}")
