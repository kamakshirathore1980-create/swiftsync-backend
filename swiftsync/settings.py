"""
Django settings for SwiftSync AI project.
"""

from pathlib import Path
from datetime import timedelta

# ─── Base Paths ───────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent


# ─── Security ────────────────────────────────────────────────────────────────
# IMPORTANT: Change this to a long random string before deploying to production!
SECRET_KEY = 'django-insecure-swiftsync-ai-secret-key-change-in-production-2024'

# Set to False in production and set ALLOWED_HOSTS properly
DEBUG = True

ALLOWED_HOSTS = ['*']


# ─── Installed Apps ───────────────────────────────────────────────────────────
INSTALLED_APPS = [
    # Django built-ins
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party packages
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',

    # Our app
    'api.apps.ApiConfig',
]


# ─── Middleware ───────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',      # Must be before CommonMiddleware
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ─── URL Configuration ────────────────────────────────────────────────────────
ROOT_URLCONF = 'swiftsync.urls'


# ─── Templates ───────────────────────────────────────────────────────────────
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


# ─── WSGI ─────────────────────────────────────────────────────────────────────
WSGI_APPLICATION = 'swiftsync.wsgi.application'


# ─── Database ─────────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ─── Password Validation ──────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ─── Localization ─────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ─── Static Files ─────────────────────────────────────────────────────────────
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ─── CORS Configuration ───────────────────────────────────────────────────────
# Allow any frontend to connect during development
CORS_ALLOW_ALL_ORIGINS = True


# ─── Django REST Framework Configuration ─────────────────────────────────────
REST_FRAMEWORK = {
    # Use JWT for all API authentication
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # Require authentication by default (override per-view with AllowAny)
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # Enable filtering support
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    # Pagination: return 10 items per page
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}


# ─── JWT Configuration ────────────────────────────────────────────────────────
SIMPLE_JWT = {
    # Access token valid for 1 day
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    # Refresh token valid for 7 days
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    # Issue a new refresh token each time you refresh
    'ROTATE_REFRESH_TOKENS': True,
    # Algorithm used to sign tokens
    'ALGORITHM': 'HS256',
    # Header prefix: Authorization: Bearer <token>
    'AUTH_HEADER_TYPES': ('Bearer',),
}
