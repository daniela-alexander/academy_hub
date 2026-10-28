from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase

from chat.models import Participant
from chat.services import (
    create_direct_conversation,
    create_group_conversation,
    mark_messages_as_read,
    send_message,
)

User = get_user_model()


class DirectConversationServiceTests(TestCase):

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
        conv = create_direct_conversation(self.student, self.teacher)
        self.assertEqual(conv.participants.count(), 2)
        self.assertFalse(conv.is_group)

    def test_create_direct_twice_returns_same(self):
        c1 = create_direct_conversation(self.student, self.teacher)
        c2 = create_direct_conversation(self.student, self.teacher)
        self.assertEqual(c1.pk, c2.pk)

    def test_cannot_create_with_self(self):
        with self.assertRaises(ValidationError):
            create_direct_conversation(self.student, self.student)


class GroupConversationServiceTests(TestCase):

    def setUp(self):
        self.academy = User.objects.create_user(
            username="academia",
            email="academia@example.com",
            password="TestPassword123!",
            is_academy=True,
        )
        self.student1 = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="TestPassword123!",
            is_student=True,
        )
        self.student2 = User.objects.create_user(
            username="carlos",
            email="carlos@example.com",
            password="TestPassword123!",
            is_student=True,
        )

    def test_academy_can_create_group(self):
        conv = create_group_conversation(
            creator=self.academy,
            title="Alumnos",
            participant_ids=[self.student1.pk, self.student2.pk],
        )
        self.assertTrue(conv.is_group)
        self.assertEqual(conv.participants.count(), 3)

    def test_student_cannot_create_group(self):
        with self.assertRaises(PermissionDenied):
            create_group_conversation(
                creator=self.student1,
                title="Grupo no autorizado",
                participant_ids=[self.student2.pk],
            )


class SendMessageServiceTests(TestCase):

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
        self.conv = create_direct_conversation(self.student, self.teacher)

    def test_participant_can_send(self):
        msg = send_message(self.student, self.conv.pk, "Hola profe")
        self.assertEqual(msg.text, "Hola profe")
        self.assertEqual(msg.sender, self.student)

    def test_empty_message_raises(self):
        with self.assertRaises(ValidationError):
            send_message(self.student, self.conv.pk, "   ")

    def test_non_participant_cannot_send(self):
        intruder = User.objects.create_user(
            username="intruso",
            email="intruso@example.com",
            password="TestPassword123!",
        )
        with self.assertRaises(PermissionDenied):
            send_message(intruder, self.conv.pk, "Me cuelo")

    def test_mark_messages_as_read(self):
        msg = send_message(self.student, self.conv.pk, "Hola")
        mark_messages_as_read(self.conv.pk, self.teacher)
        msg.refresh_from_db()
        self.assertTrue(msg.is_read)
