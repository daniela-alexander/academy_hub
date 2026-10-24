from django.db import transaction

from academies.models import Academy


@transaction.atomic
def verify_academy(academy_id, staff_user):
    if not staff_user.is_staff:
        raise ValueError("Solo el staff puede verificar academias.")

    academy = (
        Academy.objects
        .select_for_update()
        .get(pk=academy_id)
    )

    academy.is_verified = True
    academy.save(update_fields=["is_verified"])
    return academy
