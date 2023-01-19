"""
Django settings for ZOO project.

Generated by 'django-admin startproject' using Django 4.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import os
from dotenv import load_dotenv
from datetime import timedelta
from pathlib import Path
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = False

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split()


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'corsheaders',
    'rest_framework',
    'rest_framework_swagger',
    'django_filters',
    'ckeditor_uploader',
    # 'debug_toolbar',
    'ckeditor',
    'import_export',
    'admin_reorder',
    'imagekit',
    'colorfield',
    'smart_selects',

    'main.apps.MainConfig',
]

USE_DJANGO_JQUERY = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTStatelessUserAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(hours=24),
}
REDIS_HOST = os.getenv('R_HOST')
REDIS_PORT = os.getenv('R_PORT')
REDIS_DB = os.getenv('R_DB')
MIDDLEWARE = [
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'admin_reorder.middleware.ModelAdminReorder',
]
CSRF_TRUSTED_ORIGINS = ['https://territoriyazoo.by']
CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'ZOO.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

ADMIN_REORDER = (
    {
        'app': 'main',
        'label': 'База товаров интернет магазина',
        'models': [
            {'model': 'main.Product', 'label': 'Продукты'},
            {'model': 'main.ProductOptions', 'label': 'Варианты фасовки'},
            {'model': 'main.Brand', 'label': 'Бренды'},
            {'model': 'main.Animal', 'label': 'Животные'},
            {'model': 'main.Category', 'label': 'Категории'},
            {'model': 'main.SubCategory', 'label': 'Подкатегории'},
            {'model': 'main.Units', 'label': 'Единицы измерения фасовки'},
        ]
    },
    {
        'app': 'main',
        'label': 'Заказы Товаров / Покупатели',
        'models': [
            {'model': 'main.Order', 'label': 'Заказы товаров'},
            {'model': 'main.Customer', 'label': 'Покупатели'},
            {'model': 'main.Consultation', 'label': 'Заявки на обратный звонок'},
        ]
    },
    {
        'app': 'main',
        'label': 'Скидки',
        'models': [
            {'model': 'main.DiscountByProductOption', 'label': 'Скидки по варианту фасовки'},
            {'model': 'main.DiscountBySubCategory', 'label': 'Скидка по подкатегории'},
            {'model': 'main.DiscountByDay', 'label': 'Скидка по дням недели'},
            {'model': 'main.WeekDays', 'label': 'Дни недели'},
        ]
    },
    {
        'app': 'main',
        'label': 'Социальное',
        'models': [
            {'model': 'main.InfoShop', 'label': 'Информация о магазине'},
            {'model': 'main.InfoShopBlock', 'label': 'Блок о магазине'},
            {'model': 'main.Article', 'label': 'Полезные статьи'},
            {'model': 'main.Comments', 'label': 'Отзывы о магазине'},
            {'model': 'main.Banner', 'label': 'Рекламные Баннеры'},

        ]
    }
)
WSGI_APPLICATION = 'ZOO.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASS'),
        'HOST': os.getenv('DB_HOST'),
        # 'PORT': os.getenv('DB_PORT'),
    }
}
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "CACHED",
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
CACHE_TTL = 60 * 1

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


LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Minsk'

USE_I18N = True

USE_TZ = True

STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/django_static/'

DATA_UPLOAD_MAX_NUMBER_FIELDS = 3000

MEDIA_URL = '/django_media/'

MEDIA_ROOT = BASE_DIR / 'mediafiles'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field
# REDIS_URL = "redis://redis:6379/1"
# BROKER_URL = REDIS_URL
# CELERY_BROKER_URL = REDIS_URL
# CELERY_RESULT_BACKEND = REDIS_URL
# CELERY_ACCEPT_CONTENT = ['application/json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json' 207320125879

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CKEDITOR_UPLOAD_PATH = ''
CKEDITOR_CONFIGS = {
    'default': {
        'height': 150,
        'width': 900,
        'enterMode': 2,
        'skin': 'moono',
        'toolbar_YourCustomToolbarConfig': [
            {'name': 'paragraph',
             'items': ['NumberedList', 'BulletedList', '-',
                       'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'
                       ]},
        ],
        'toolbar': 'YourCustomToolbarConfig',
    },
    'custom': {
        'height': 400,
        'width': 900,
        'enterMode': 2,
        'skin': 'moono',
        'toolbar_YourCustomToolbarConfig': [
            {'name': 'paragraph',
             'items': ['NumberedList', 'BulletedList', '-',
                       'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-',
                       'Bold', 'FontSize',
                       ]},
        ],
        'toolbar': 'YourCustomToolbarConfig',
    },
    'main_page': {
        'height': 100,
        'width': 400,
        'enterMode': 2,
        'skin': 'moono',
        'toolbar_YourCustomToolbarConfig': [
            {'name': 'paragraph',
             'items': ['Bold']},
        ],
        'toolbar': 'YourCustomToolbarConfig',
    }
}
