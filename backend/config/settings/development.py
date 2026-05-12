from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGINS = unique_list(CSRF_TRUSTED_ORIGINS + [
    'http://localhost:3000',
    'http://localhost:5173',
    'http://localhost:8080',
])
