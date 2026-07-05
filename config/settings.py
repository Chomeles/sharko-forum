import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def env_list(name, default=""):
    return [x.strip() for x in os.environ.get(name, default).split(",") if x.strip()]


DEBUG = os.environ.get("DJANGO_DEBUG", "") == "1"

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    if not DEBUG:
        raise RuntimeError("DJANGO_SECRET_KEY must be set (see .env.example)")
    from django.core.management.utils import get_random_secret_key

    SECRET_KEY = "insecure-dev-" + get_random_secret_key()

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "forum",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise serves static files straight from gunicorn — no separate static
    # server needed for the Docker/one-command deploy.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

# Set to a prefix (e.g. "/forum") when the app is proxied under a sub-path and the
# proxy strips that prefix; keeps URL reversing correct. Empty = served at root.
FORCE_SCRIPT_NAME = os.environ.get("FORCE_SCRIPT_NAME") or None

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "forum"),
        "USER": os.environ.get("POSTGRES_USER", "forum"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        "CONN_MAX_AGE": 60,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = os.environ.get("TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True

STATIC_URL = os.environ.get("DJANGO_STATIC_URL", "/static/")
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    # Compresses + content-hashes filenames → safe long-lived caching.
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "forum:index"
LOGOUT_REDIRECT_URL = "forum:index"

# Honour the proxy's X-Forwarded-Proto so Django knows the request was HTTPS.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
# Default "/"; set to the sub-path when co-hosting so cookies don't leak to siblings.
SESSION_COOKIE_PATH = os.environ.get("SESSION_COOKIE_PATH", "/")
CSRF_COOKIE_PATH = os.environ.get("CSRF_COOKIE_PATH", "/")

EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "25"))
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "forum@localhost")
# With no SMTP host, print password-reset links to the log instead of 500-ing on
# a box with no mail server (e.g. the Docker deploy). Set EMAIL_HOST for real mail.
EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND") or (
    "django.core.mail.backends.smtp.EmailBackend"
    if EMAIL_HOST
    else "django.core.mail.backends.console.EmailBackend"
)

# Errors and security warnings → stderr → the process manager's logs.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "WARNING"},
}
