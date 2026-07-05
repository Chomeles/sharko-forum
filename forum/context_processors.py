def notifications(request):
    """Unread notification count for the navbar bell. One COUNT per page when logged in."""
    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        return {"notif_count": user.notifications.filter(is_read=False).count()}
    return {}
