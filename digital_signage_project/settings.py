"""
Django settings for Digital Signage project.
Part of The Grid ecosystem.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'signage',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'digital_signage_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'signage.context_processors.app_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'digital_signage_project.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DIGITAL_SIGNAGE_DB_NAME', 'digital_signage'),
        'USER': os.environ.get('DIGITAL_SIGNAGE_DB_USER', 'derekt'),
        'PASSWORD': os.environ.get('DIGITAL_SIGNAGE_DB_PASSWORD', ''),
        'HOST': os.environ.get('DIGITAL_SIGNAGE_DB_HOST', 'localhost'),
        'PORT': os.environ.get('DIGITAL_SIGNAGE_DB_PORT', '5432'),
    },
    'data_connect': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DATA_CONNECT_DB_NAME', 'data_connect'),
        'USER': os.environ.get('DATA_CONNECT_DB_USER', 'derekt'),
        'PASSWORD': os.environ.get('DATA_CONNECT_DB_PASSWORD', ''),
        'HOST': os.environ.get('DATA_CONNECT_DB_HOST', 'localhost'),
        'PORT': os.environ.get('DATA_CONNECT_DB_PORT', '5432'),
    }
}

# Database Routers
DATABASE_ROUTERS = ['signage.db_routers.DataConnectRouter']

# Password validation
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

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Regina'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'signage' / 'static',
]
# Media files (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================================
# Azure AD / Microsoft Entra ID Configuration
# ============================================================================
MS_ENTRA_TENANT_ID = os.environ.get('AZURE_TENANT_ID')
MS_ENTRA_CLIENT_ID = os.environ.get('AZURE_CLIENT_ID')
MS_ENTRA_CLIENT_SECRET = os.environ.get('AZURE_CLIENT_SECRET_VALUE')
# Microsoft Graph scope for user profile
MS_ENTRA_SCOPES = ['User.Read']

# Authentication
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_URL = 'signage:auth_login'
LOGIN_REDIRECT_URL = '/'

# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# HTTPS settings (production)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = not DEBUG

# CSRF settings
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', 'http://localhost:8000').split(',')

# ============================================================================
# Redis Configuration (optional)
# ============================================================================
REDIS_URL = os.environ.get('REDIS_URL')

if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
else:
    # Default to local memory cache for development
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'digital-signage-cache',
        }
    }

# ============================================================================
# Azure Blob Storage (for APK and persistent file storage)
# ============================================================================
AZURE_STORAGE_ACCOUNT_NAME = os.environ.get('AZURE_STORAGE_ACCOUNT_NAME', '')
AZURE_STORAGE_ACCOUNT_KEY = os.environ.get('AZURE_STORAGE_ACCOUNT_KEY', '')
AZURE_STORAGE_CONTAINER = os.environ.get('AZURE_STORAGE_CONTAINER', 'digital-signage')

# Storage backends (Django 4.2+ STORAGES dict)
if AZURE_STORAGE_ACCOUNT_NAME and AZURE_STORAGE_ACCOUNT_KEY:
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.azure_storage.AzureStorage",
            "OPTIONS": {
                "azure_container": AZURE_STORAGE_CONTAINER,
                "account_name": AZURE_STORAGE_ACCOUNT_NAME,
                "account_key": AZURE_STORAGE_ACCOUNT_KEY,
            },
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }

# ============================================================================
# Digital Signage Specific Settings
# ============================================================================

# API key for external integrations (e.g., ScreenCloud)
SIGNAGE_API_KEY = os.environ.get('SIGNAGE_API_KEY', '')
