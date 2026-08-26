from .base import *

import os

DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': env.db('DATABASE_URL')
}

# Hybrid sharding: the VPS shard connection is registered ONLY when its URL
# is configured, so deploying before the VPS exists never breaks startup.
if os.environ.get('VPS_SHARD_1_URL'):
    DATABASES['vps_shard_1'] = env.db('VPS_SHARD_1_URL')
