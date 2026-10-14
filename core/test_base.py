# core/test_base.py
import sys

from django.test import TestCase


GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


class VerboseTestCase(TestCase):
    """
    TestCase que imprime el nombre de cada test con un indicador visual
    de pasado/fallado en la terminal, tipo:

        create user .......................... ✅ PASS
        email must be unique ................. ❌ FAIL
        user can have city ................... ✅ PASS
    """

    def __call__(self, result=None):
        pretty_name = self._testMethodName.replace("test_", "").replace("_", " ")
        dots = "." * max(1, 60 - len(pretty_name))

        sys.stdout.write(f"{pretty_name} {dots} ")
        sys.stdout.flush()

        try:
            super().__call__(result)
        except Exception:
            sys.stdout.write(f"{RED}❌ ERROR{RESET}\n")
            sys.stdout.flush()
            raise

        if self._test_failed(result):
            sys.stdout.write(f"{RED}❌ FAIL{RESET}\n")
        elif self._test_skipped(result):
            sys.stdout.write(f"{YELLOW}⚠️  SKIP{RESET}\n")
        else:
            sys.stdout.write(f"{GREEN}✅ PASS{RESET}\n")

        sys.stdout.flush()

    def _test_failed(self, result):
        if result is None:
            return False
        for test, _ in list(result.failures) + list(result.errors):
            if test.id() == self.id():
                return True
        return False

    def _test_skipped(self, result):
        if result is None:
            return False
        for test, _ in result.skipped:
            if test.id() == self.id():
                return True
        return False