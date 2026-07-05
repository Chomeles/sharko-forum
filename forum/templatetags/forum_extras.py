import hashlib

from django import template

register = template.Library()

# (min_messages, name, css-class). Checked high → low.
RANKS = [
    (1000, "Legendary", "rank-legendary"),
    (200, "Elite", "rank-elite"),
    (50, "Active", "rank-active"),
    (10, "Member", "rank-member"),
    (0, "Newbie", "rank-newbie"),
]


@register.filter
def rank_for(user):
    """{'name', 'cls'} for a user. Staff/admin override the message-count ranks."""
    if getattr(user, "is_superuser", False):
        return {"name": "Administrator", "cls": "rank-staff"}
    if getattr(user, "is_staff", False):
        return {"name": "Staff", "cls": "rank-staff"}
    n = getattr(user, "msg_count", 0) or 0
    for threshold, name, cls in RANKS:
        if n >= threshold:
            return {"name": name, "cls": cls}
    return {"name": "Newbie", "cls": "rank-newbie"}


@register.filter
def avatar_bg(username):
    """Deterministic gradient from the username — a stable identicon with no storage."""
    h = int(hashlib.md5((username or "?").encode()).hexdigest(), 16)
    hue = h % 360
    return f"linear-gradient(135deg, hsl({hue} 60% 48%), hsl({(hue + 45) % 360} 65% 38%))"


@register.filter
def initial(username):
    return (username or "?")[:1].upper()
