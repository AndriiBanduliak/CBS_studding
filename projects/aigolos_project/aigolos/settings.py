"""
Django settings for AIGolos project.
"""

import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-this-in-production-!@#$%^&*()')

# SECURITY WARNING: don't run with debug turned on in production!
# Default to True for development convenience
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    'accounts',
    'core',
    'asr',
    'llm',
    'tts',
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
    'aigolos.middleware.LoggingMiddleware',
    'aigolos.middleware.SecurityHeadersMiddleware',
    'aigolos.middleware.CompressionMiddleware',
]

# Security Headers
# SECURE_SSL_REDIRECT: Disabled by default, enable only in production with reverse proxy
# In DEBUG mode, always disable SSL redirect (dev server doesn't support HTTPS)
if DEBUG:
    SECURE_SSL_REDIRECT = False
else:
    # In production, can be enabled via environment variable
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False').lower() == 'true'

if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Content Security Policy (CSP)
CSP_DEFAULT_SRC = os.getenv('CSP_DEFAULT_SRC', "'self'")
CSP_SCRIPT_SRC = os.getenv('CSP_SCRIPT_SRC', "'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com")
CSP_STYLE_SRC = os.getenv('CSP_STYLE_SRC', "'self' 'unsafe-inline' https://cdnjs.cloudflare.com")
CSP_IMG_SRC = os.getenv('CSP_IMG_SRC', "'self' data: https:")
CSP_FONT_SRC = os.getenv('CSP_FONT_SRC', "'self' https://cdnjs.cloudflare.com")
CSP_CONNECT_SRC = os.getenv('CSP_CONNECT_SRC', "'self'")

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,  # 5 minutes default
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# Redis cache for production (optional)
REDIS_URL = os.getenv('REDIS_URL', '')
if REDIS_URL and not DEBUG:
    CACHES['default'] = {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'aigolos',
        'TIMEOUT': 300,
    }

# WhiteNoise for static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

ROOT_URLCONF = 'aigolos.urls'

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

WSGI_APPLICATION = 'aigolos.wsgi.application'

# Database
DATABASE_URL = os.getenv('DATABASE_URL', '')
if DATABASE_URL:
    # Parse DATABASE_URL (postgresql://user:password@host:port/dbname)
    import re
    match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', DATABASE_URL)
    if match:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': match.group(5),
                'USER': match.group(1),
                'PASSWORD': match.group(2),
                'HOST': match.group(3),
                'PORT': match.group(4),
            }
        }
    else:
        # Fallback to SQLite
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
else:
    # Use SQLite by default
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

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
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Login URLs
LOGIN_URL = '/api/auth/login/'
LOGIN_REDIRECT_URL = '/app/'
LOGOUT_REDIRECT_URL = '/api/auth/login/'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    # Rate limiting/throttling
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',  # Anonymous users: 100 requests per hour
        'user': '1000/hour',  # Authenticated users: 1000 requests per hour
        'asr': '20/hour',  # ASR endpoint: 20 requests per hour (resource-intensive)
        'llm': '100/hour',  # LLM endpoint: 100 requests per hour
        'tts': '50/hour',  # TTS endpoint: 50 requests per hour
    },
    # Filtering and search
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    # API Documentation
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# CORS Settings
CORS_ALLOWED_ORIGINS = os.getenv(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:8000,http://127.0.0.1:8000'
).split(',')

# Only allow all origins in DEBUG mode
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOW_ALL_ORIGINS = False
    # Additional security settings for production
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
    CORS_ALLOW_HEADERS = [
        'accept',
        'accept-encoding',
        'authorization',
        'content-type',
        'dnt',
        'origin',
        'user-agent',
        'x-csrftoken',
        'x-requested-with',
    ]

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d %(funcName)s %(correlation_id)s',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'ignore_encoding_errors': {
            '()': 'aigolos.logging_filters.IgnoreEncodingErrorsFilter',
        },
        'django_server_filter': {
            '()': 'aigolos.logging_filters.DjangoServerFilter',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'aigolos.logging_config.SafeStreamHandler',
            'formatter': 'verbose',
            'filters': ['ignore_encoding_errors'],
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'errors.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'json' if not DEBUG else 'verbose',
        },
        'file_json': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'app.json.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'json',
        },
        'file_info': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'info.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file_info'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['console'],  # Показываем сообщения сервера
            'level': 'INFO',
            # Временно убираем фильтр, чтобы увидеть все сообщения
            # 'filters': ['django_server_filter'],
            'propagate': False,
        },
        # Отключаем логирование basehttp для предотвращения ошибок кодировки
        'django.core.servers.basehttp': {
            'handlers': [],
            'level': 'CRITICAL',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'aigolos': {
            'handlers': ['console', 'file_info'] + (['file_json'] if not DEBUG else []),
            'level': 'INFO',
            'propagate': False,
        },
        'security': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'accounts': {
            'handlers': ['console', 'file_info'],
            'level': 'INFO',
            'propagate': False,
        },
        'core': {
            'handlers': ['console', 'file_info'],
            'level': 'INFO',
            'propagate': False,
        },
        'asr': {
            'handlers': ['console', 'file_info'],
            'level': 'INFO',
            'propagate': False,
        },
        'llm': {
            'handlers': ['console', 'file_info'],
            'level': 'INFO',
            'propagate': False,
        },
        'tts': {
            'handlers': ['console', 'file_info'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Application-specific settings
ASR_MODEL_NAME = os.getenv('ASR_MODEL_NAME', 'large-v3')
ASR_DEVICE = os.getenv('ASR_DEVICE', 'cpu')
ASR_COMPUTE_TYPE = os.getenv('ASR_COMPUTE_TYPE', 'int8')

LLM_BACKEND = os.getenv('LLM_BACKEND', 'ollama')
LLM_MODEL_NAME = os.getenv('LLM_MODEL_NAME', 'qwen2.5:7b')
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
LLM_MAX_TOKENS = int(os.getenv('LLM_MAX_TOKENS', '256'))
LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', '0.7'))

TTS_VOICE_NAME = os.getenv('TTS_VOICE_NAME', 'de_DE/thorsten/medium')
TTS_MODEL_PATH = os.getenv('TTS_MODEL_PATH', '')

SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', '3600'))
MAX_AUDIO_SIZE = int(os.getenv('MAX_AUDIO_SIZE', '10485760'))  # 10MB

# Create logs directory if it doesn't exist
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# Email Configuration (for password reset)
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@aigolos.com')

# API Documentation (drf-spectacular)
SPECTACULAR_SETTINGS = {
    'TITLE': 'AIGolos API',
    'DESCRIPTION': 'AI-powered speech recognition, language model, and text-to-speech API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/v1/',
    'COMPONENT_SPLIT_REQUEST': True,
    'TAGS': [
        {'name': 'Authentication', 'description': 'User authentication and registration'},
        {'name': 'ASR', 'description': 'Automatic Speech Recognition'},
        {'name': 'LLM', 'description': 'Large Language Model chat'},
        {'name': 'TTS', 'description': 'Text-to-Speech synthesis'},
        {'name': 'Core', 'description': 'Core API endpoints'},
    ],
}

