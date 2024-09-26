from .base import *

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

# Security
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 1
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}

# django-storages 1.14.2 documentation » Amazon S3
# This backend implements the Django File Storage API for Amazon Web Services’s (AWS) Simple Storage Service (S3).

AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME", "")

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {},
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Email Configuration
EMAIL_BACKEND = "notifications.email_backends.SesEmailBackend"
AWS_SES_REGION_NAME = os.getenv("AWS_SES_REGION_NAME")
AWS_SES_ACCESS_KEY = os.getenv("AWS_SES_ACCESS_KEY")
AWS_SES_SECRET_KEY = os.getenv("AWS_SES_SECRET_KEY")


# Global settings for REST framework API
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework_simplejwt.authentication.JWTAuthentication"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
}

# CORS headers allows resources to be accessed from other domains
CORS_ALLOWED_ORIGINS = ["https://main.d2s0mr17z37dgw.amplifyapp.com"]
CORS_ALLOW_ALL_ORIGINS = True

# A JSON Web Token authentication plugin for the Django REST Framework
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=12),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=5),
    "UPDATE_LAST_LOGIN": True,
}
