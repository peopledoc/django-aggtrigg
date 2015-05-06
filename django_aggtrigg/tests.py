# -*- coding: utf-8 -*-

# Copyright (C) 2014 Rodolphe Quiedeville <rodolphe@quiedeville.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from util_tests import utilTests  # noqa
from tool_tests import toolTests  # noqa

from django.db import connection, models
from django.db.models import Q, Count
from django_aggtrigg.models import ForeignKeyTriggerField
from django_aggtrigg.models import AggCount
from django.db.models import get_models


def mocked_get_count(obj):
    """
    Mock the get_count method on the manager when no trigger really
    exists
    """

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


class AggTriggerTestMixin(object):
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

    def setUp(self):
        self.mock_get_count()
        super(AggTriggerTestMixin, self).setUp()

    def tearDown(self):
        self.unmock_get_count()
        super(AggTriggerTestMixin, self).tearDown()
