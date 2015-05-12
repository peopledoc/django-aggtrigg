from StringIO import StringIO
from django.test import TestCase
from django.db import ProgrammingError
from django.core.management import call_command
from dummy.models import Tree, Leave
from django.db import connection
from django_aggtrigg.tests import AggTriggerTestMixin


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

class Utils(object):

    def create_objects(self):
        for a in range(20):
            t = Tree.objects.create(name="tree")
            for a in range(10):
                private = False
                if a % 2 == 0:
                    private = True
                Leave.objects.create(tree=t, name="leave", private=private)

    def delete_triggers(self):
        out = StringIO()
        cursor = connection.cursor()
        call_command('aggtrigg_drop', stdout=out)
        cursor.execute(out.getvalue())

class TestMockingTrigger(Utils, AggTriggerTestMixin, TestCase):

    def test_real_triggers(self):
        call_command('aggtrigg_create')
        call_command('aggtrigg_initialize', quiet=True)
        self.create_objects()
        self.unmock_get_count()
        # assert triggers are correctly set AND they retrun a correct
        # result (see TestUtils.create_objects to get why we have 10
        # leaves)

        self.assertEqual(Tree.objects.get_count().first().leave_count, 10)
        self.assertEqual(
            Tree.objects.get_count().first().leave_count_private_leaves, 5)

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
        # same result as with the triggers but no trigger at all!
        # You know nothing Django!
        self.assertEqual(Tree.objects.get_count().first().leave_count, 10)


class TestDemo(Utils, AggTriggerTestMixin, TestCase):
    """
    Show how to use AggTriggerTestMixin
    """

    def test_normal_operation(self):
        """
        We delete triggers to be absolutely sure no triggers are left (as
        there is a test how create triggers we don't know if triggers
        are presents or not.
        """
        self.delete_triggers()
        self.create_objects()
        self.assertEqual(Tree.objects.get_count().first().leave_count, 10)
        self.assertEqual(
            Tree.objects.get_count().first().leave_count_private_leaves,
            5)


class TestSetupAndTearDow(AggTriggerTestMixin, TestCase):

    def setUp(self):
        self.something = "something"
        super(TestSetupAndTearDow, self).setUp()

    def test_setup_is_not_overrided(self):
        self.assertTrue(hasattr(self, "something"))
