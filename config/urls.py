from django.contrib import admin
from django.urls import include, path

# Mounted at the domain root by default. To serve under a sub-path (e.g. /forum),
# strip the prefix at the proxy and set FORCE_SCRIPT_NAME — URLs still reverse right.
urlpatterns = [
    path("admin/", admin.site.urls),
    # login/logout/password_change/password_reset
    path("", include("django.contrib.auth.urls")),
    path("", include("forum.urls")),
]
