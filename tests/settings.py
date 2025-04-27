from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent

INSTALLED_APPS = [
    'django_img_optimizer',
    'django.contrib.auth',
    'django.contrib.contenttypes',
]

ROOT_URLCONF = 'tests.app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [PROJECT_DIR / "app" / "templates"],
        'APP_DIRS': True,
    },
]

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    PROJECT_DIR / "static",
]

OPTIMIZE_IMAGE_ROOT = PROJECT_DIR / "static" / "images"
OPTIMIZE_IMAGE_EXCLUDED_FOLDERS = ['excluded_folder']