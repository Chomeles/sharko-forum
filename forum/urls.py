from django.urls import path

from . import views

app_name = "forum"

urlpatterns = [
    path("", views.index, name="index"),
    path("signup/", views.signup, name="signup"),
    path("search/", views.search, name="search"),
    path("notifications/", views.notifications, name="notifications"),
    path("shoutbox/", views.shoutbox_feed, name="shoutbox"),
    path("shoutbox/post/", views.shout_post, name="shout_post"),
    path("c/<slug:slug>/", views.category_detail, name="category"),
    path("c/<slug:slug>/new/", views.new_thread, name="new_thread"),
    path("t/<int:pk>/", views.thread_detail, name="thread"),
    path("t/<int:pk>/reply/", views.reply, name="reply"),
    path("p/<int:pk>/edit/", views.edit_post, name="edit_post"),
    path("p/<int:pk>/like/", views.toggle_like, name="toggle_like"),
]
