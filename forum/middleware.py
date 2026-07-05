from django.utils import timezone

from .models import Presence


class PresenceMiddleware:
    """Stamp last-seen for the online-users list. ponytail: throttled to one write per
    minute per user via the session; drop the throttle for a cache backend if it grows."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            now = timezone.now()
            if now.timestamp() - request.session.get("_seen", 0) > 60:
                request.session["_seen"] = now.timestamp()
                Presence.objects.update_or_create(user=user, defaults={"seen": now})
        return self.get_response(request)
