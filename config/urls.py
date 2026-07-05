from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("forum/admin/", admin.site.urls),
    # login/logout/password_change/password_reset under /forum/
    path("forum/", include("django.contrib.auth.urls")),
    path("forum/", include("forum.urls")),
]
