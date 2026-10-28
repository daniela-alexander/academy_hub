import logging

from celery import shared_task
from django.contrib.auth import get_user_model

from .models import Notification

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def send_notification_email_async(user_id, subject, body):
    """
    Simula envío de email en segundo plano.
    En producción: usar django.core.mail.send_mail.
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.error("send_notification_email_async: user %s not found", user_id)
        return "user_not_found"

    logger.info(
        "Enviando email a %s | Asunto: %s | Cuerpo: %s",
        user.email,
        subject,
        body[:80],
    )
    return f"email_sent_for_user_{user_id}"


@shared_task
def create_notification_async(user_id, notification_type, title, message, url=""):
    """
    Crea la notificación in-app y dispara el email en otra tarea.
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.error("create_notification_async: user %s not found", user_id)
        return "user_not_found"

    notification = Notification.objects.create(
        user=user,
        type=notification_type,
        title=title,
        message=message,
        url=url,
    )

    send_notification_email_async.delay(
        user_id=user_id,
        subject=title,
        body=message,
    )

    return f"notification_{notification.pk}_created"
