# -*- coding: utf-8 -*-
#
# Copyright (c) 2014 Rodolphe Quiédeville <rodolphe@quiedeville.org>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of django-aggtrigg nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
#
from django.db import models
from django.db import connection
from djqmixin import QMixin
import tool
import util


class TooManyKwargs(Exception):
    pass


class MissingKwargs(Exception):
    pass


class TriggerFieldMixin(object):
    def __init__(self, *args, **kwargs):
        self.aggregate_trigger = ['count']
        super(TriggerFieldMixin, self).__init__(*args, **kwargs)


class ForeignKeyTriggerField(TriggerFieldMixin, models.ForeignKey):

    description = "An ForeignKeyField with trigger"


class IntegerTriggerField(TriggerFieldMixin, models.IntegerField):

    description = "An IntegerField with trigger"


class FloatTriggerField(TriggerFieldMixin, models.FloatField):

    description = "An FloatField with trigger"


class AggCount(QMixin):

    def get_count(self):
        """Returns a new QuerySet object.  Subclasses can override this method
        to easily customize the behavior of the Manager.
        """

        qs = self

        for k, v in self.model.__dict__.iteritems():
            if isinstance(
                    v,
                    models.fields.related.ForeignRelatedObjectsDescriptor):
                if isinstance(v.related.field, ForeignKeyTriggerField):
                    table = "{}__{}_agg".format(
                        v.related.model._meta.db_table,
                        v.related.field.attname)

                    for agg in v.related.field.aggregate_trigger:
                        select = {}
                        filters = []
                        if isinstance(agg, dict):
                            for key in agg.iterkeys():
                                for agg_filter in agg[key]:
                                    for title in agg_filter:
                                        filters.append(
                                            "{}_{}".format(key, title))
                        else:
                            filters = [agg]

                        for filter in filters:
                            param = "select {} from {} where {}={}.{}".format(
                                "agg_{}".format(filter),
                                table,
                                v.related.field.attname,
                                self.model._meta.db_table,
                                self.model._meta.pk.name)
                            select["{}_{}".format(
                                v.related.var_name, filter)] = param
                            qs = qs.extra(select=select)
        return qs


class AggTriggManager(models.Manager):

    def optimized_count(self, **kwargs):
        """Return count in optimized manner

        Apple.objects.filter(indice=4).count()
        Apple.objects.optimized_count(indice=4)

        """
        if (len(kwargs) == 0):
            raise MissingKwargs("you must specify the filter clause")
        if (len(kwargs) > 1):
            raise TooManyKwargs()
        # do not care about more than one kwarg
        (key, value) = kwargs.items()[0]
        (nbe, column, qfilter) = tool.parse_kwarg(key)

        agg = 'agg_count'
        agf = agg.split('_')

        agt = util.AggTrigger(util.PG_BACKEND, self.model._meta.db_table,
                              column)

        if nbe == 1:
            agf = agg
        elif nbe == 2:
            agf = agt.agg_function(agg, agf[1])

        cursor = connection.cursor()
        qry = """SELECT {} FROM {} WHERE {} %s"""

        tbname = util.table_name(self.model._meta.db_table, column)
        cursor.execute(qry.format(agf, tbname, qfilter), [value])
        row = cursor.fetchone()
        return row[0]


# As the fields define here are not special types, it's easy to let
# south add them to a migration. The code below will make the revelant
# work to make south able to manage the migration.
# cf. http://south.aeracode.org/wiki/MyFieldsDontWork for the explanation
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules(
        [], ["^django_aggtrigg\.models\.IntegerTriggerField"])
    add_introspection_rules(
        [], ["^django_aggtrigg\.models\.FloatTriggerField"])
except ImportError:
    pass
