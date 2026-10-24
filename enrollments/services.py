#Aquí meteremos servicios que puedan saturar las views y hacerlas poco claras. Por ejemplo
"""
Aceptar solicitud
    ↓
reservar plaza
    ↓
rechazar otras solicitudes
    ↓
crear notificación
    ↓
enviar email
"""

from django.db import transaction

from courses.models import Convocatoria
from enrollments.models import Enrollment, EnrollmentStatus


@transaction.atomic
def reserve_place(student, convocatoria_id):
    convocatoria = (
        Convocatoria.objects
        .select_for_update()
        .get(pk=convocatoria_id)
    )

    if not convocatoria.is_active:
        raise ValueError("La convocatoria no está activa.")

    if convocatoria.is_full:
        raise ValueError("La convocatoria está llena.")

    if Enrollment.objects.filter(
        student=student,
        convocatoria=convocatoria,
    ).exists():
        raise ValueError("Ya tienes una inscripción en esta convocatoria.")

    enrollment = Enrollment.objects.create(
        student=student,
        convocatoria=convocatoria,
        status=EnrollmentStatus.RESERVED,
    )

    convocatoria.reserved_places += 1
    convocatoria.save(update_fields=["reserved_places"])

    return enrollment
