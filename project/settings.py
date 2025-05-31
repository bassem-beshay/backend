from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-sy1fyb%pe69u60c__()_8pazzvgvb1hxj-6nwcqryl&*f9@n0o"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'users',
    'orders',
    'vendors',
    'products',
    'cart',
    'payment',
    'core',
]

MIDDLEWARE = [
    # CORS Middleware  FIRST
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    
]

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "project.wsgi.application"


# Database

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "ecommerce-db",
        "USER": "neondb_owner",
        "PASSWORD": "npg_ODXQBC1hnpK7",
        "HOST": "ep-spring-rice-a88kkroe-pooler.eastus2.azure.neon.tech",
        "PORT": "5432",
        "OPTIONS": {
            "sslmode": "require",
        },
        # 'HOST': 'postgresql://neondb_owner:npg_ODXQBC1hnpK7@ep-spring-rice-a88kkroe-pooler.eastus2.azure.neon.tech/ecommerce-db?sslmode=require',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom User Model
AUTH_USER_MODEL = "users.User"

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.JSONParser',
    ],
}


# JWT Settings

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
}

# Allow to access API from frontend
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:5173",
   
# ]

CORS_ALLOW_ALL_ORIGINS = True


# Email settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "abdo01143617687@gmail.com"
EMAIL_HOST_PASSWORD = "xxijdhyyqghjkcdq"
DEFAULT_FROM_EMAIL = "abdo@abdostore.com"


FRONTEND_URL = "http://localhost:5173"
BACKEND_URL = "http://localhost:8000"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# below allows up to 10 MB uploads
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB

# for DRF config:
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024 



 #  For development only

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True



#Payment Settings
PAYMOB_API_KEY = 'ZXlKaGJHY2lPaUpJVXpVeE1pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SmpiR0Z6Y3lJNklrMWxjbU5vWVc1MElpd2ljSEp2Wm1sc1pWOXdheUk2TVRBME16RTNNeXdpYm1GdFpTSTZJakUzTkRjMU56TXlNek11TlRjeE1EWWlmUS5IWjRaU0VPVFY2QjFWVDBCbWp3Q1VmT1hJQmxBVlhXQVNCVHYzN2FqRTBVNzFZN0xycGw0M2FfUUdZVHRPVXdHMFNtNkhuVkFCWVBnQllIenZUazRoUQ=='
PAYMOB_INTEGRATION_ID = '5085520'
PAYMOB_IFRAME_ID = '920499'
PAYMOB_HMAC_SECRET = 'D7EEF0BF7EFE5BFDDFA190FAE5019976'
PAYMOB_INTEGRATION_ID_VODAFONE ='5089329'


 #  For development only
ALLOWED_HOSTS = ['*']


# Site settings
SITE_NAME = 'VendorHub'

# solution for CORS issue
from corsheaders.defaults import default_headers

CORS_ALLOW_HEADERS = list(default_headers) + [
    'Authorization',
]


#  Redis setup
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',  
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
