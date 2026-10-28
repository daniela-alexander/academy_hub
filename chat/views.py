from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Conversation
from .permissions import IsParticipant
from .serializers import (
    ConversationSerializer,
    CreateDirectConversationInputSerializer,
    CreateGroupConversationInputSerializer,
    MessageSerializer,
    SendMessageInputSerializer,
)
from .services import (
    create_direct_conversation,
    create_group_conversation,
    mark_messages_as_read,
    send_message,
)

User = get_user_model()


class ConversationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipant]

    def get_queryset(self):
        user = self.request.user
        return (
            Conversation.objects
            .filter(Q(participants__user=user))
            .prefetch_related("participants__user", "messages")
            .distinct()
            .order_by("-updated_at")
        )

    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        conversation = self.get_object()
        mark_messages_as_read(conversation.pk, request.user)
        qs = conversation.messages.select_related("sender").order_by("created_at")
        return Response(MessageSerializer(qs, many=True).data)

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        conversation = self.get_object()
        serializer = SendMessageInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            msg = send_message(
                user=request.user,
                conversation_id=conversation.pk,
                text=serializer.validated_data["text"],
            )
            return Response(
                MessageSerializer(msg).data,
                status=status.HTTP_201_CREATED,
            )
        except (ValidationError, PermissionDenied) as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        conversation = self.get_object()
        mark_messages_as_read(conversation.pk, request.user)
        return Response({"status": "ok"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def create_direct(self, request):
        serializer = CreateDirectConversationInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            other = User.objects.get(
                username=serializer.validated_data["username"]
            )
        except User.DoesNotExist:
            return Response(
                {"detail": "Usuario no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            conversation = create_direct_conversation(
                user_a=request.user,
                user_b=other,
            )
            return Response(
                ConversationSerializer(
                    conversation, context={"request": request}
                ).data,
                status=status.HTTP_201_CREATED,
            )
        except (ValidationError, PermissionDenied) as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["post"])
    def create_group(self, request):
        serializer = CreateGroupConversationInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            conversation = create_group_conversation(
                creator=request.user,
                title=serializer.validated_data["title"],
                participant_ids=serializer.validated_data["participants"],
            )
            return Response(
                ConversationSerializer(
                    conversation, context={"request": request}
                ).data,
                status=status.HTTP_201_CREATED,
            )
        except (ValidationError, PermissionDenied) as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
