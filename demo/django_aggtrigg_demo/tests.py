from StringIO import StringIO
from django.test import TestCase
from django.db import ProgrammingError
from django.core.management import call_command
from dummy.models import Tree, Leave
from django.db.models import get_models
from django.db import connection

from django_aggtrigg.models import AggCount


def mocked_get_count(obj):
    return obj


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


class TestMockingTrigger(TestCase):

    def mock_get_count(self):
        for model in get_models():
            if hasattr(model.objects, "QuerySet"):
                if hasattr(model.objects.QuerySet, "get_count"):
                    model.objects.QuerySet.get_count = mocked_get_count

    def unmock_get_count(self):
        for model in get_models():
            if hasattr(model.objects, "QuerySet"):
                if hasattr(model.objects.QuerySet, "get_count"):
                    model.objects.include(AggCount)
                    model.objects.QuerySet.get_count = AggCount['get_count']

    def create_objects(self):
        for a in range(20):
            t = Tree.objects.create(name="tree")
            for a in range(10):
                Leave.objects.create(tree=t, name="leave")

    def delete_triggers(self):
        out = StringIO()
        cursor = connection.cursor()
        call_command('aggtrigg_drop', stdout=out)
        cursor.execute(out.getvalue())

    def test_no_triggers(self):
        """
        Ensure Table, Triggers and function does not exists,
        """
        out = StringIO()
        cursor = connection.cursor()
        call_command('aggtrigg_drop', stdout=out)
        cursor.execute(out.getvalue())
        call_command('aggtrigg_check')
        out = StringIO()
        call_command('aggtrigg_check', stdout=out)
        for report in out.getvalue().split("\n"):
            self.assertFalse(
                report.startswith("OK")
            )

    def test_no_trigger_raises(self):
        self.delete_triggers()
        self.create_objects()
        self.unmock_get_count()
        with self.assertRaises(ProgrammingError):
            Tree.objects.get_count().first()

    def test_mocked_triggers_do_not_raises(self):
        self.mock_get_count()
        self.delete_triggers()
        self.create_objects()
        Tree.objects.get_count().first()
