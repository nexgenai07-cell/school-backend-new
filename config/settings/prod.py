from .base import *

DEBUG = True

ALLOWED_HOSTS = [
    ".vercel.app",
    "127.0.0.1",
    "localhost",
]

CSRF_TRUSTED_ORIGINS = [
    "https://*.vercel.app",
]

DATABASES = {
    "default": env.db("DATABASE_URL")
}


# WhiteNoise must be after SecurityMiddleware
MIDDLEWARE.insert(
    1,
    "whitenoise.middleware.WhiteNoiseMiddleware"
)


STATIC_URL = "/static/"

# Vercel deployment ke liye
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
    BASE_DIR / "static"
]

STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)


CORS_ALLOW_ALL_ORIGINS = True