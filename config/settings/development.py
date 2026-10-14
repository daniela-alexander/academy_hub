import os
from .base import *

DEBUG = os.getenv(
    "DJANGO_DEBUG",
    "True"
).lower() == "true"