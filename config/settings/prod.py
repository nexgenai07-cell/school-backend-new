from .base import *

import os

DEBUG = True

ALLOWED_HOSTS = [
    ".vercel.app",
    "127.0.0.1",
    "localhost",
    # School subdomains (schoola/schoolb/schoolc.nxgenai.pro) resolve their
    # tenant from the Host header, so they must be accepted here.
    ".nxgenai.pro",
]

CSRF_TRUSTED_ORIGINS = [
    "https://*.vercel.app",
]

DATABASES = {
    "default": env.db("DATABASE_URL")
}

# Hybrid sharding: the VPS shard connection is registered ONLY when its URL
# is configured (in .env locally / Vercel env vars in production), so
# deploying before the VPS exists never breaks startup.
if os.environ.get('VPS_SHARD_1_URL'):
    DATABASES['vps_shard_1'] = env.db('VPS_SHARD_1_URL')


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