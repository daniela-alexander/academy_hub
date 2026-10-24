import os
from .base import *

DEBUG = os.getenv(
    "DJANGO_DEBUG",
    "True"
).lower() == "true"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "academyhub"),
        "USER": os.getenv("POSTGRES_USER", "academyhub_user"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
        "HOST": os.getenv("POSTGRES_HOST", "localhost"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}