from StringIO import StringIO
from django.test import TestCase
from django.db import ProgrammingError
from django.core.management import call_command
from dummy.models import Tree, Leave
from django.db.models import get_models
from django.db import connection, models
from django.db.models import Q, Count
from django_aggtrigg.models import AggCount, ForeignKeyTriggerField


def mocked_get_count(obj):
    triggs = []
    for name, field in obj.model.__dict__.iteritems():
        if isinstance(
                field,
                models.fields.related.ForeignRelatedObjectsDescriptor):
            if isinstance(field.related.field, ForeignKeyTriggerField):
                model = field.related.field.model
                table = field.related.field.model._meta.db_table
                model_name = field.related.field.model._meta.model_name
                foreing = field.related.field.attname
                related_field = field.related.field.rel.field_name
                related_table = obj.model._meta.db_table
                triggs.append({"model": obj.model,
                              "table": obj.model._meta.db_table,
                               "field": name,
                               "aggs": field.related.field.aggregate_trigger})
    for trigg in triggs:
        for agg in trigg["aggs"]:
            if isinstance(agg, dict):
                for aggregate_type in agg.iterkeys():
                    for agg_filter in agg[aggregate_type]:
                        for name in agg_filter:
                            extra_name = "{}_{}_{}".format(model_name,
                                                           aggregate_type,
                                                           name)
                            query = Q()
                            for filter in agg_filter[name]:
                                query &= Q(
                                    **{filter["field"]: filter["value"]})
                            compiler = model.objects.filter(
                                query).query.get_compiler(
                                    connection=connection)
                            qn = compiler.quote_name_unless_alias
                            where_clause = model.objects.filter(
                                query).query.where.as_sql(
                                    qn,
                                    connection
                                )
                            qs = """select count(*) from "{}" WHERE {}={}.{}
                                    AND {}""".format(
                                table,
                                foreing,
                                related_table,
                                related_field,
                                where_clause[0] % where_clause[1][0])
                            obj = obj.extra(select={extra_name: qs})
            else:
                filter = "{}_count".format(model_name)
                obj = obj.annotate(**{filter: Count(model_name)})
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


class TestUtils(object):
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


class TestMockingTrigger(TestUtils, TestCase):

    def test_real_triggers(self):
        call_command('aggtrigg_create')
        call_command('aggtrigg_initialize', quiet=True)
        self.create_objects()
        self.unmock_get_count()
        # assert triggers are correctly set AND they retrun a correct
        # result (see TestUtils.create_objects to get why we have 10
        # leaves)

        self.assertEqual(Tree.objects.get_count().first().leave_count, 10)

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
