from StringIO import StringIO

from django.test import TestCase
from django.core.management import call_command


class TestCommands(TestCase):

    def test_check(self):
        out = StringIO()
        call_command('aggtrigg_create', stdout=out)
        out.seek(0)
        value = out.read()
        self.assertTrue(value)
        self.assertTrue(value.startswith('KO'))
