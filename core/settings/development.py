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


# Global settings for REST framework API
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
}

# CORS headers allows resources to be accessed from other domains
CORS_ALLOW_ALL_ORIGINS = True

# A JSON Web Token authentication plugin for the Django REST Framework
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=12),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=5),
    # It will work instead of the default serializer(TokenObtainPairSerializer).
    # "TOKEN_OBTAIN_SERIALIZER": "accounts.serializers.CustomTokenObtainPairSerializer",
    "UPDATE_LAST_LOGIN": True,
}
