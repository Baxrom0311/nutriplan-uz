import os
from datetime import timedelta
from pathlib import Path

from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

def split_env_list(value: str, strip_trailing_slash: bool = False) -> list[str]:
    items: list[str] = []

    for raw_item in value.split(','):
        item = raw_item.strip()
        if not item:
            continue
        if strip_trailing_slash:
            item = item.rstrip('/')
        items.append(item)

    return items


def unique_list(items: list[str]) -> list[str]:
    deduped: list[str] = []

    for item in items:
        if item not in deduped:
            deduped.append(item)

    return deduped


ALLOWED_HOSTS = unique_list(split_env_list(config('ALLOWED_HOSTS', default='')))

render_external_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '').strip()
if render_external_hostname:
    ALLOWED_HOSTS = unique_list(ALLOWED_HOSTS + [render_external_hostname])

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_yasg',
    
    # Local apps
    'users',
    'food',
    'meals',
    'analytics',
    'nutrition',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'nutriplan-local-cache',
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Custom User Model
AUTH_USER_MODEL = 'users.CustomUser'

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'uz-uz'  # Default language: Uzbek

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# DRF Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'EXCEPTION_HANDLER': 'config.exceptions.custom_exception_handler',
}

# Simple JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS Settings
frontend_url = config('FRONTEND_URL', default='').strip().rstrip('/')

cors_allowed_origins = split_env_list(config('CORS_ALLOWED_ORIGINS', default=''), strip_trailing_slash=True)
if frontend_url:
    cors_allowed_origins.append(frontend_url)

CORS_ALLOWED_ORIGINS = unique_list(cors_allowed_origins)

cors_allowed_origin_regexes = split_env_list(config('CORS_ALLOWED_ORIGIN_REGEXES', default=''))
if config('ALLOW_NETLIFY_DEPLOYS', default=True, cast=bool):
    cors_allowed_origin_regexes.append(r'^https://.*\.netlify\.app$')

CORS_ALLOWED_ORIGIN_REGEXES = unique_list(cors_allowed_origin_regexes)
CORS_ALLOW_CREDENTIALS = False

csrf_trusted_origins = split_env_list(config('CSRF_TRUSTED_ORIGINS', default=''), strip_trailing_slash=True)
if frontend_url:
    csrf_trusted_origins.append(frontend_url)

render_external_url = os.environ.get('RENDER_EXTERNAL_URL', '').strip().rstrip('/')
if render_external_url:
    csrf_trusted_origins.append(render_external_url)

CSRF_TRUSTED_ORIGINS = unique_list(csrf_trusted_origins)

# DeepSeek AI Settings
DEEPSEEK_API_KEY = config('DEEPSEEK_API_KEY', default='')

# Food photo analysis settings
# Provider: 'gemini' (Google Gemini) yoki 'openai' (OpenAI-compatible)
FOOD_VISION_PROVIDER = config('FOOD_VISION_PROVIDER', default='gemini')
FOOD_VISION_API_KEY = config('FOOD_VISION_API_KEY', default=config('GEMINI_API_KEY', default=''))

# Gemini models: gemini-2.0-flash-exp, gemini-2.5-pro-exp, gemini-1.5-flash, gemini-1.5-pro
# OpenAI models: gpt-4o, gpt-4o-mini, gpt-4-turbo
FOOD_VISION_MODEL = config('FOOD_VISION_MODEL', default='gemini-2.0-flash-exp')

# OpenAI-compatible API URL (faqat provider='openai' bo'lsa ishlatiladi)
FOOD_VISION_API_URL = config('FOOD_VISION_API_URL', default='https://api.openai.com/v1/chat/completions')

# --- MONKEY PATCH FOR DJANGO 4.2 + PYTHON 3.14 TEMPLATE CONTEXT BUG ---
# Django 4.2 has a bug in `BaseContext.__copy__` when running on Python 3.14+
# where `copy(super())` returns a `super` object instead of the copied context, 
# causing dicts to be missing in Admin views.
import django.template.context

def _patched_basecontext_copy(self):
    duplicate = type(self).__new__(type(self))
    duplicate.__dict__.update(self.__dict__)
    duplicate.dicts = self.dicts[:]
    return duplicate

django.template.context.BaseContext.__copy__ = _patched_basecontext_copy
