from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from chat.models import Conversation, Message, Participant, ParticipantRole
from courses.models import Category, Course

User = get_user_model()


class ConversationModelTests(TestCase):

    def setUp(self):
        self.student = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="TestPassword123!",
            is_student=True,
        )
        self.teacher = User.objects.create_user(
            username="profesor",
            email="profesor@example.com",
            password="TestPassword123!",
            is_academy=True,
        )

    def test_create_direct_conversation(self):
        conv = Conversation.objects.create(
            created_by=self.student,
            is_group=False,
        )
        self.assertFalse(conv.is_group)
        self.assertEqual(conv.created_by, self.student)

    def test_create_group_conversation(self):
        conv = Conversation.objects.create(
            created_by=self.teacher,
            title="Alumnos Inglés",
            is_group=True,
        )
        self.assertTrue(conv.is_group)
        self.assertEqual(conv.title, "Alumnos Inglés")

    def test_participant_unique_per_conversation(self):
        conv = Conversation.objects.create(created_by=self.student)
        Participant.objects.create(conversation=conv, user=self.student)
        with self.assertRaises(IntegrityError):
            Participant.objects.create(conversation=conv, user=self.student)

    def test_participant_role_default(self):
        conv = Conversation.objects.create(created_by=self.student)
        p = Participant.objects.create(conversation=conv, user=self.student)
        self.assertEqual(p.role, ParticipantRole.STUDENT)


class MessageModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="TestPassword123!",
            is_student=True,
        )
        self.conv = Conversation.objects.create(created_by=self.user)
        Participant.objects.create(conversation=self.conv, user=self.user)

    def test_create_message(self):
        msg = Message.objects.create(
            conversation=self.conv,
            sender=self.user,
            text="Hola",
        )
        self.assertEqual(msg.text, "Hola")
        self.assertFalse(msg.is_read)

    def test_message_ordering(self):
        m1 = Message.objects.create(
            conversation=self.conv, sender=self.user, text="Primero"
        )
        m2 = Message.objects.create(
            conversation=self.conv, sender=self.user, text="Segundo"
        )
        msgs = list(Message.objects.all())
        self.assertEqual(msgs[0], m1)
        self.assertEqual(msgs[1], m2)
