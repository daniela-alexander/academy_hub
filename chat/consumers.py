import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.core.exceptions import PermissionDenied, ValidationError

from .models import Participant
from .services import send_message

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]

        if not await self._is_participant():
            await self.close()
            return

        self.room_group_name = f"chat_{self.conversation_id}"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name,
            )

    async def receive_json(self, content, **kwargs):
        text = content.get("text", "").strip()
        if not text:
            return

        try:
            message = await database_sync_to_async(send_message)(
                self.user,
                self.conversation_id,
                text,
            )
        except (ValidationError, PermissionDenied) as e:
            await self.send_json({"type": "error", "detail": str(e)})
            return

        # El mensaje se emite desde send_message al Channel Layer.
        # Aquí no volvemos a emitir para no duplicar.

    async def chat_message(self, event):
        await self.send_json(
            {
                "type": "message",
                "message_id": event["message_id"],
                "sender": event["sender"],
                "text": event["text"],
                "created_at": event["created_at"],
            }
        )

    @database_sync_to_async
    def _is_participant(self):
        return Participant.objects.filter(
            conversation_id=self.conversation_id,
            user=self.user,
        ).exists()
