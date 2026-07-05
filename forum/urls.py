from django.urls import path

from . import views

app_name = "forum"

urlpatterns = [
    path("", views.index, name="index"),
    path("signup/", views.signup, name="signup"),
    path("c/<slug:slug>/", views.category_detail, name="category"),
    path("c/<slug:slug>/new/", views.new_thread, name="new_thread"),
    path("t/<int:pk>/", views.thread_detail, name="thread"),
    path("t/<int:pk>/reply/", views.reply, name="reply"),
    path("p/<int:pk>/edit/", views.edit_post, name="edit_post"),
]
