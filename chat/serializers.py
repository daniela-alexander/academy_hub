from rest_framework import serializers

from .models import Conversation, Message, Participant


class ParticipantSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = Participant
        fields = ["id", "user", "username", "role", "role_display", "joined_at"]
        read_only_fields = fields


class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source="sender.username", read_only=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "conversation",
            "sender",
            "sender_username",
            "text",
            "is_read",
            "created_at",
        ]
        read_only_fields = fields


class ConversationSerializer(serializers.ModelSerializer):
    participants = ParticipantSerializer(many=True, read_only=True)
    created_by_username = serializers.CharField(
        source="created_by.username", read_only=True
    )
    course_title = serializers.CharField(source="course.title", read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id",
            "created_by",
            "created_by_username",
            "title",
            "is_group",
            "course",
            "course_title",
            "created_at",
            "updated_at",
            "participants",
            "last_message",
            "unread_count",
        ]
        read_only_fields = fields

    def get_last_message(self, obj):
        last = obj.messages.last()
        return last.text if last else None

    def get_unread_count(self, obj):
        user = self.context["request"].user
        return obj.messages.filter(is_read=False).exclude(sender=user).count()


class SendMessageInputSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=1000, allow_blank=False)


class CreateDirectConversationInputSerializer(serializers.Serializer):
    username = serializers.CharField()
    course = serializers.IntegerField(required=False, allow_null=True)


class CreateGroupConversationInputSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=150)
    participants = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
    )
    course = serializers.IntegerField(required=False, allow_null=True)
