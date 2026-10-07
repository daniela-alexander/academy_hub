from django.shortcuts import render
import logging

logger = logging.getLogger(__name__)

def home(request):
    logger.info("Home page requested")
    return render(request, 'core/home.html')

