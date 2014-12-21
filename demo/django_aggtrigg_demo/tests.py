from StringIO import StringIO
from django.test import TestCase
from django.core.management import call_command
from django_aggtrigg.util import DatabaseNotSupported


class TestCommands(TestCase):

    def test_check(self):
        out = StringIO()
        with self.assertRaises(DatabaseNotSupported) as context:
            call_command('aggtrigg_check', stdout=out)
        out.seek(0)

    def test_drop(self):
        out = StringIO()
        with self.assertRaises(DatabaseNotSupported) as context:
            call_command('aggtrigg_drop', stdout=out)
        out.seek(0)

    def test_create(self):
        out = StringIO()
        with self.assertRaises(DatabaseNotSupported) as context:
            call_command('aggtrigg_create', stdout=out)
        out.seek(0)

    def test_initialize(self):
        out = StringIO()
        with self.assertRaises(DatabaseNotSupported) as context:
            call_command('aggtrigg_initialize', stdout=out)
        out.seek(0)
