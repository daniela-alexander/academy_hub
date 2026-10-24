from django.contrib.auth import get_user_model
from django.db import IntegrityError
from core.test_base import VerboseTestCase

from talent.models import Competence, PassportEntry, TalentPassport

User = get_user_model()


class PassportEntryModelTests(VerboseTestCase):

    def setUp(self):
        self.student = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="TestPassword123!",
            is_student=True,
        )
        self.passport = TalentPassport.objects.create(student=self.student)
        self.competence = Competence.objects.create(name="Inglés")

    def test_level_cannot_be_below_1(self):
        with self.assertRaises(IntegrityError):
            PassportEntry.objects.create(
                passport=self.passport,
                competence=self.competence,
                level=0,
            )

    def test_level_cannot_be_above_5(self):
        with self.assertRaises(IntegrityError):
            PassportEntry.objects.create(
                passport=self.passport,
                competence=self.competence,
                level=6,
            )

    def test_competence_unique_per_passport(self):
        PassportEntry.objects.create(
            passport=self.passport,
            competence=self.competence,
            level=3,
        )
        with self.assertRaises(IntegrityError):
            PassportEntry.objects.create(
                passport=self.passport,
                competence=self.competence,
                level=4,
            )