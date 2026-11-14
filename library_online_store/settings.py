"""
Django settings for library_online_store project.
"""
import os
from pathlib import Path
from datetime import timedelta
import os
import dj_database_url
from dotenv import load_dotenv
load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-gfb5+68hi0cgc38ug1r7^t424*glqmnq@e*3ndw(%!&y7e8=8g'

DEBUG = True

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "10.0.2.2",
    "library-online-api-tehr.onrender.com",
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # ចាំបាច់ត្រូវមានសម្រាប់ dj-rest-auth/allauth
    # Custom Apps
    'booklibrary',
    # Third Party Apps
    'rest_framework',
    'rest_framework.authtoken', # ចាំបាច់សម្រាប់ dj-rest-auth Token Authentication
    # Allauth & Social Apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.github',   
    'allauth.socialaccount.providers.facebook',
    # Rest Auth Apps
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'cloudinary',
    'cloudinary_storage',
    'storages',
]

#  1. SITE_ID (ចាំបាច់បំផុតសម្រាប់ django-allauth)
SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # ចាំបាច់សម្រាប់ allauth ជំនាន់ថ្មី
]

# 2. Authentication Backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ROOT_URLCONF = 'library_online_store.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'library_online_store.wsgi.application'


# # Database
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


DATABASE_URL = os.getenv("DATABASE_URL")


if not DATABASE_URL:

    raise RuntimeError(
        "DATABASE_URL is not configured."
    )


DATABASES = {

    "default": dj_database_url.parse(

        DATABASE_URL,

        # Keep DB connection alive
        conn_max_age=600,

        # Check connection before using it
        conn_health_checks=True,

        # Require SSL
        ssl_require=True,
    ),
}


# # 2. Cloudinary Configuration (យក Credential ពី Cloudinary Dashboard ត្រង់ API Keys)
# CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
# CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
# CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

# cloudinary.config(
#     cloud_name=CLOUDINARY_CLOUD_NAME,
#     api_key=CLOUDINARY_API_KEY,
#     api_secret=CLOUDINARY_API_SECRET,
#     secure=True
# )
# Cloudflare R2 Configuration

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

AWS_STORAGE_BUCKET_NAME = "library-database"

AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")
AWS_S3_REGION_NAME = "auto"

AWS_S3_CUSTOM_DOMAIN = os.getenv("AWS_S3_CUSTOM_DOMAIN")

AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = False
AWS_S3_FILE_OVERWRITE = False

AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}

R2_PUBLIC_URL = (
    "https://pub-6a8d798caf2d433e819b96b0be7a9915.r2.dev"
)

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "access_key": AWS_ACCESS_KEY_ID,
            "secret_key": AWS_SECRET_ACCESS_KEY,
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "endpoint_url": AWS_S3_ENDPOINT_URL,
            "region_name": AWS_S3_REGION_NAME,
            "custom_domain": AWS_S3_CUSTOM_DOMAIN,
            "location": "",
            "default_acl": None,
            "querystring_auth": False,
            "file_overwrite": False,
            "object_parameters": AWS_S3_OBJECT_PARAMETERS,
        },
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'


#  3. Django REST Framework & Social Auth Configurations
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
         'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),

    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ការកំណត់ Email verification និង Login behavior
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'none'  # អាចប្តូរទៅ 'optional' ឬ 'mandatory' ប្រសិនបើមាន Email Server


# មិនបាច់តម្រូវឱ្យវាយ Username ដោយដៃទេ នៅពេល Register តាម Social Account
SOCIALACCOUNT_QUERY_EMAIL = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': '385528301641-53mk9217kuvkflc3ltvki80bihmdhba0.apps.googleusercontent.com', # យកពី Google Cloud Console (Web application)
            'secret': '****tru7',
            'key': ''
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

REDIS_URL = os.getenv("REDIS_URL")

if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
            "TIMEOUT": 900,
        }
    }
else:
    # ពេល dev នៅ local មិនមាន Redis
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# បន្ថែមការកំណត់នេះដើម្បីឱ្យ WhiteNoise រក្សាទុក Static files បានល្អ
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = "smtp.gmail.com"
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
# EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
# DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
