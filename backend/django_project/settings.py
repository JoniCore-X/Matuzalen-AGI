import os
from pathlib import Path
from urllib.parse import unquote, urlparse

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = 'dev-secret-key-change-me'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'plan_data',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'django_project.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {'context_processors': ['django.template.context_processors.request']},
    }
]

database_url = os.getenv('DATABASE_URL', '')
parsed_database_url = urlparse(database_url.replace('postgresql+psycopg', 'postgresql'))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': parsed_database_url.path.lstrip('/') or 'postgres',
        'USER': unquote(parsed_database_url.username or 'postgres'),
        'PASSWORD': unquote(parsed_database_url.password or ''),
        'HOST': parsed_database_url.hostname or 'localhost',
        'PORT': str(parsed_database_url.port or 5432),
        'OPTIONS': {'sslmode': 'require'} if parsed_database_url.hostname else {},
    }
}

USE_TZ = True
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
STATIC_URL = 'static/'
