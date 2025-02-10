from .base import *

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"


# Email Configuration
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# CORS headers allows resources to be accessed from other domains
CORS_ALLOW_ALL_ORIGINS = True


# Global settings for REST framework API
REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"].append(
    # Additional authentication for development
    "rest_framework.authentication.SessionAuthentication"
)
