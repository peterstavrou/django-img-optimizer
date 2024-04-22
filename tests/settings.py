import os

SECRET_KEY = 'django-insecure-ra=u24w+nej0os)il@$u8_t32+0=2lm@g9wben3fszf@09=mt@'

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

INSTALLED_APPS = [
    'django_img_optimizer',
    'django.contrib.auth',
    'django.contrib.contenttypes',
]

ROOT_URLCONF = 'tests.app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_DIR, "app", "templates")],
        'APP_DIRS': True,
    },
]

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, "static"),
]

OPTIMIZE_IMAGE_ROOT = os.path.join(PROJECT_DIR, 'static', 'images')
OPTIMIZE_IMAGE_EXCLUDED_FOLDERS = ['excluded_folder']
