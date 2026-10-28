from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from chat.models import Message
from courses.models import Course
from enrollments.models import Enrollment
from payments.models import Payment, Scholarship

from .models import Notification
from .tasks import create_notification_async


# ============================================================
# CHAT — nuevo mensaje
# ============================================================

@receiver(post_save, sender=Message)
def notify_new_message(sender, instance, created, **kwargs):
    if not created:
        return

    conversation = instance.conversation

    for participant in conversation.participants.exclude(user=instance.sender):
        create_notification_async.delay(
            user_id=participant.user_id,
            notification_type=Notification.Type.NEW_MESSAGE,
            title="Nuevo mensaje de chat",
            message=f"{instance.sender.username}: {instance.text[:80]}",
            url=f"/chat/{conversation.pk}/",
        )


# ============================================================
# ENROLLMENT — cambios de estado
# ============================================================

@receiver(pre_save, sender=Enrollment)
def enrollment_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            previous = Enrollment.objects.get(pk=instance.pk)
            instance._old_status = previous.status
        except Enrollment.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Enrollment)
def enrollment_post_save(sender, instance, created, **kwargs):
    academy_user_id = instance.convocatoria.course.academy.owner_id

    if created:
        create_notification_async.delay(
            user_id=academy_user_id,
            notification_type=Notification.Type.ENROLLMENT_RECEIVED,
            title="Nueva solicitud de inscripción",
            message=(
                f"{instance.student.username} ha solicitado plaza en "
                f"{instance.convocatoria.course.title}."
            ),
            url=f"/enrollments/{instance.pk}/",
        )
        return

    old = getattr(instance, "_old_status", None)

    if old is None or old == instance.status:
        return

    if instance.status == "approved":
        create_notification_async.delay(
            user_id=instance.student_id,
            notification_type=Notification.Type.ENROLLMENT_APPROVED,
            title="Inscripción aprobada",
            message=(
                f"Tu inscripción en {instance.convocatoria.course.title} "
                f"ha sido aprobada."
            ),
            url=f"/enrollments/{instance.pk}/",
        )
    elif instance.status == "rejected":
        create_notification_async.delay(
            user_id=instance.student_id,
            notification_type=Notification.Type.ENROLLMENT_REJECTED,
            title="Inscripción rechazada",
            message=(
                f"Tu inscripción en {instance.convocatoria.course.title} "
                f"ha sido rechazada."
            ),
            url=f"/enrollments/{instance.pk}/",
        )


# ============================================================
# SCHOLARSHIP — cambios de estado
# ============================================================

@receiver(pre_save, sender=Scholarship)
def scholarship_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            previous = Scholarship.objects.get(pk=instance.pk)
            instance._old_status = previous.status
        except Scholarship.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Scholarship)
def scholarship_post_save(sender, instance, created, **kwargs):
    if created:
        return

    old = getattr(instance, "_old_status", None)
    if old is None or old == instance.status:
        return

    if instance.status == "approved":
        create_notification_async.delay(
            user_id=instance.student_id,
            notification_type=Notification.Type.SCHOLARSHIP_APPROVED,
            title="Beca aprobada",
            message="Tu solicitud de beca ha sido aprobada.",
            url=f"/payments/scholarships/",
        )
    elif instance.status == "rejected":
        create_notification_async.delay(
            user_id=instance.student_id,
            notification_type=Notification.Type.SCHOLARSHIP_REJECTED,
            title="Beca rechazada",
            message="Tu solicitud de beca ha sido rechazada.",
            url=f"/payments/scholarships/",
        )


# ============================================================
# COURSE — cambio a published
# ============================================================

@receiver(pre_save, sender=Course)
def course_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            previous = Course.objects.get(pk=instance.pk)
            instance._old_status = previous.status
        except Course.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Course)
def course_post_save(sender, instance, created, **kwargs):
    if created:
        return

    old = getattr(instance, "_old_status", None)
    if old == instance.status:
        return

    if instance.status == "published":
        # Notificar a los usuarios que tienen la academia como favorita
        from academies.models import AcademyFavorite
        favorites = AcademyFavorite.objects.filter(academy=instance.academy)
        for favorite in favorites:
            create_notification_async.delay(
                user_id=favorite.user_id,
                notification_type=Notification.Type.COURSE_PUBLISHED,
                title="Nuevo curso publicado",
                message=(
                    f"{instance.academy.name} ha publicado "
                    f"'{instance.title}'."
                ),
                url=f"/courses/{instance.pk}/{instance.slug}/",
            )


# ============================================================
# PAYMENT — pago confirmado
# ============================================================

@receiver(pre_save, sender=Payment)
def payment_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            previous = Payment.objects.get(pk=instance.pk)
            instance._old_status = previous.status
        except Payment.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Payment)
def payment_post_save(sender, instance, created, **kwargs):
    old = getattr(instance, "_old_status", None)
    if old is None or old == instance.status:
        return

    if instance.status == "paid":
        create_notification_async.delay(
            user_id=instance.enrollment.student_id,
            notification_type=Notification.Type.SUCCESS,
            title="Pago confirmado",
            message=(
                f"Hemos recibido tu pago de {instance.amount} €."
            ),
            url=f"/payments/",
        )
