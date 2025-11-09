"""
Django settings for law_crm project.
CRM для Адвокатского Объединения
"""

from pathlib import Path
from decouple import config
import os
import sys

# Fix for Windows encoding issues with PostgreSQL
# Prevents psycopg2 from reading configuration files from user directory with non-ASCII characters
# These are also set in manage.py but repeated here for consistency
os.environ.setdefault('PGPASSFILE', 'nul')  # Windows equivalent of /dev/null
os.environ.setdefault('PGSERVICEFILE', 'nul')
os.environ.setdefault('PGSYSCONFDIR', 'nul')
os.environ['PGCLIENTENCODING'] = 'UTF8'

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',  # PostgreSQL-специфичные функции
    
    # Third-party apps
    'django_filters',
    'auditlog',
    'guardian',
    'django_fsm',
    'phonenumber_field',
    # 'django_celery_beat',  # Отключено для локальной версии без Celery
    
    # Local apps
    'core.apps.CoreConfig',
    'case_management.apps.CaseManagementConfig',
    'time_tracking.apps.TimeTrackingConfig',
    'documents.apps.DocumentsConfig',
    'billing.apps.BillingConfig',
    'court_integrations.apps.CourtIntegrationsConfig',
]

if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'auditlog.middleware.AuditlogMiddleware',  # Аудит действий пользователей
]

if DEBUG:
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

ROOT_URLCONF = 'law_crm.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'law_crm.wsgi.application'

# Database
# Используем pg8000 - чистый Python драйвер PostgreSQL БЕЗ libpq!
# Это решает проблему с кодировкой на Windows с кириллицей в пути
import urllib.parse

DB_NAME = config('DB_NAME', default='law_crm_db')
DB_USER = config('DB_USER', default='postgres')  # Временно используем postgres
DB_PASSWORD = config('DB_PASSWORD', default='6049')  # ИЗМЕНИТЕ НА ВАШ ПАРОЛЬ!
DB_HOST = config('DB_HOST', default='127.0.0.1')  # Use IP instead of localhost
DB_PORT = config('DB_PORT', default=5432, cast=int)

# Используем pg8000 вместо psycopg2 - НЕТ ПРОБЛЕМ С КОДИРОВКОЙ!
DATABASES = {
    'default': {
        'ENGINE': 'django_pg8000',  # Используем pg8000 вместо psycopg2
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
    }
}

print(f"[INFO] Using pg8000 (pure Python PostgreSQL driver)")
print(f"[INFO] Database: {DB_HOST}:{DB_PORT}/{DB_NAME} as {DB_USER}")

# Custom User Model
AUTH_USER_MODEL = 'core.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'uk'  # Украинский язык
TIME_ZONE = 'Europe/Kiev'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Celery Configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Email Configuration
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=25, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Security Settings (для production)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Django Guardian - Object-level permissions
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)

# Debug Toolbar Settings
INTERNAL_IPS = [
    '127.0.0.1',
]

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'law_crm.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ЕГРСР Integration
EGRSR_API_URL = config('EGRSR_API_URL', default='https://court.gov.ua/')
EGRSR_API_KEY = config('EGRSR_API_KEY', default='')

# Session timeout (8 часов)
SESSION_COOKIE_AGE = 28800

