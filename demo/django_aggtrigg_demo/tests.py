from StringIO import StringIO
from django.test import TestCase
from django.core.management import call_command


class TestCommands(TestCase):

    def test_commands(self):
        out = StringIO()
        call_command('aggtrigg_create', stdout=out)
        out.seek(0)
        out = StringIO()
        call_command('aggtrigg_initialize', quiet=True, stdout=out)
        out.seek(0)
        out = StringIO()
        call_command('aggtrigg_check', stdout=out)
        out.seek(0)
        out = StringIO()
        call_command('aggtrigg_drop', stdout=out)
        out.seek(0)
