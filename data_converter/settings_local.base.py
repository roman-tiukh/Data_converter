import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '89di$5_t-fo8f*z0!kvbli20gcz^6f)8&2!e1g3o4pbe7v(h^q'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'ipa.dataocean.us',
    'localhost',
    '127.0.0.1',
]

DATABASES = {
    'default': {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "data_oceanv2",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "127.0.0.01",
        "PORT": "5432",
        'CONN_MAX_AGE': 60 * 10,  # 10 minutes
    },
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # }
}

# CORS settings
# https://github.com/adamchainz/django-cors-headers

CORS_ORIGIN_WHITELIST = [
    'https://dataocean.us',
    'http://127.0.0.1:8000',
    'http://127.0.0.1:3000',
    'http://localhost:3000',
]

CSRF_TRUSTED_ORIGINS = [
    'dataocean.us',
    'localhost',
    '127.0.0.1',
]

LOCAL_FILE_NAME_KOATUU = ''
LOCAL_FOLDER = ''
FILE_URL_KVED = ''
LOCAL_FILE_NAME_KVED = ''
LOCAL_FILE_NAME_UO_ADDRESS = ''
LOCAL_FILE_NAME_UO_SIGNER = ''

CACHES = {
    'default': {
        # REDIS cache configs
        # 'BACKEND': 'django_redis.cache.RedisCache',
        # 'LOCATION': 'redis://127.0.0.1:6379/',
        # 'OPTIONS': {
        #     "IGNORE_EXCEPTIONS": True,
        #     # 'PASSWORD': 'XXXXXXXXX',
        #     'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        # },

        # Dummy Cache for developing
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',  # use this cashe for developing
    },
}

LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'

# business_register/converter/uo.py
UO_CHUNK_SIZE = 100

