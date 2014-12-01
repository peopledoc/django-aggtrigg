from StringIO import StringIO

from django.test import TestCase
from django.core.management import call_command


class TestCommands(TestCase):

    def test_check(self):
        out = StringIO()
        call_command('check_jsdbindex', stdout=out)
        out.seek(0)
        value = out.read()
        self.assertTrue(value)
        self.assertTrue(value.startswith('KO'))

    def test_create(self):
        # Create index first
        call_command('create_jsdbindex')
        # Then check
        out = StringIO()
        call_command('check_jsdbindex', stdout=out)
        out.seek(0)
        value = out.read()
        self.assertTrue(value)
        self.assertTrue(value.startswith('OK'))

    def test_list(self):
        out = StringIO()
        call_command('list_jsdbindex', stdout=out)
        out.seek(0)
        value = out.read()
        self.assertTrue(value)
        self.assertIn('Found 1 index', value)
