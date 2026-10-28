import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from .models import Conversation, Message, Participant, ParticipantRole

User = get_user_model()
logger = logging.getLogger(__name__)


def _role_for_user(user):
    if user.is_staff:
        return ParticipantRole.ACADEMY
    if user.is_academy:
        return ParticipantRole.ACADEMY
    if user.is_student:
        return ParticipantRole.STUDENT
    return ParticipantRole.STUDENT


@transaction.atomic
def create_direct_conversation(user_a, user_b, course=None):
    """
    Crea (o recupera) una conversación directa entre dos usuarios.
    Reglas:
    - No se puede crear consigo mismo.
    - Si ya existe una conversación directa con el mismo par y curso, se devuelve.
    """
    if user_a == user_b:
        raise ValidationError("No puedes abrir un chat contigo mismo.")

    if course is not None and course.academy.owner == user_b:
        pass  # es academia del curso, ok

    # Buscar conversación directa existente con los mismos participantes
    existing = (
        Conversation.objects
        .filter(is_group=False)
        .filter(participants__user=user_a)
        .filter(participants__user=user_b)
        .distinct()
    )

    if course is not None:
        existing = existing.filter(course=course)

    existing = existing.first()
    if existing:
        return existing

    conversation = Conversation.objects.create(
        created_by=user_a,
        is_group=False,
        course=course,
    )
    Participant.objects.create(
        conversation=conversation,
        user=user_a,
        role=_role_for_user(user_a),
    )
    Participant.objects.create(
        conversation=conversation,
        user=user_b,
        role=_role_for_user(user_b),
    )
    return conversation


@transaction.atomic
def create_group_conversation(creator, title, participant_ids, course=None):
    """
    Crea un grupo.
    Reglas:
    - Solo profesores y academias pueden crear grupos.
    - Un profesor solo puede crear grupos de alumnos.
    - Una academia puede crear grupos de alumnos o de profesores.
    """
    if not creator.is_academy and not creator.is_staff:
        # fallback: si no hay is_teacher, permitimos si es staff
        raise PermissionDenied(
        "Solo academias o staff pueden crear grupos."
    )

    if not title or not title.strip():
        raise ValidationError("El grupo necesita un título.")

    if not participant_ids:
        raise ValidationError("El grupo necesita al menos un participante.")

    participants = list(
        User.objects.filter(pk__in=participant_ids).exclude(pk=creator.pk)
    )

    if len(participants) == 0:
        raise ValidationError("No has seleccionado participantes válidos.")

    conversation = Conversation.objects.create(
        created_by=creator,
        title=title.strip(),
        is_group=True,
        course=course,
    )

    Participant.objects.create(
        conversation=conversation,
        user=creator,
        role=_role_for_user(creator),
    )

    for participant in participants:
        Participant.objects.create(
            conversation=conversation,
            user=participant,
            role=_role_for_user(participant),
        )

    return conversation


@transaction.atomic
def send_message(user, conversation_id, text):
    """
    Guarda el mensaje y emite al Channel Layer para WebSockets.
    Toda la lógica de envío pasa por aquí (REST y WebSocket).
    """
    clean_text = (text or "").strip()
    if not clean_text:
        raise ValidationError("El mensaje no puede estar vacío.")

    if len(clean_text) > 1000:
        raise ValidationError("El mensaje no puede superar los 1000 caracteres.")

    conversation = (
        Conversation.objects
        .select_for_update()
        .get(pk=conversation_id)
    )

    is_participant = Participant.objects.filter(
        conversation=conversation,
        user=user,
    ).exists()

    if not is_participant:
        raise PermissionDenied("No participas en esta conversación.")

    message = Message.objects.create(
        conversation=conversation,
        sender=user,
        text=clean_text,
    )

    conversation.save(update_fields=["updated_at"])

    # Emitir al Channel Layer
    try:
        channel_layer = get_channel_layer()
        if channel_layer is not None:
            async_to_sync(channel_layer.group_send)(
                f"chat_{conversation.pk}",
                {
                    "type": "chat_message",
                    "message_id": message.pk,
                    "sender": message.sender.username,
                    "text": message.text,
                    "created_at": message.created_at.isoformat(),
                },
            )
    except Exception:
        logger.exception(
            "No se pudo emitir al Channel Layer para conversación %s",
            conversation_id,
        )

    return message


@transaction.atomic
def mark_messages_as_read(conversation_id, user):
    conversation = Conversation.objects.get(pk=conversation_id)

    is_participant = Participant.objects.filter(
        conversation=conversation,
        user=user,
    ).exists()

    if not is_participant:
        raise PermissionDenied("No participas en esta conversación.")

    Message.objects.filter(
        conversation=conversation,
        is_read=False,
    ).exclude(sender=user).update(is_read=True)
