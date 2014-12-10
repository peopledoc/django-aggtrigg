from StringIO import StringIO
from django.test import TestCase
from django.core.management import call_command


class TestCommands(TestCase):

    def test_check(self):
        out = StringIO()
        call_command('aggtrigg_check', stdout=out)
        out.seek(0)

