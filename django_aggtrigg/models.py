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
        # Introspection part, we want to know if some of the reverse
        # relations of the models contains some TriggerFieldMixin
        # pointing to the model we are working with.

        for field in self.model.__dict__.itervalues():
            if isinstance(
                    field,
                    models.fields.related.ForeignRelatedObjectsDescriptor):

                # the model we are working with has a reverse relation

                if isinstance(field.related.field, ForeignKeyTriggerField):
                    # ForeignKeyTriggerField is the type of relation
                    # we are looking for. We need to retreive the
                    # table where the aggregates are lying

                    table = "{}__{}_agg".format(
                        field.related.model._meta.db_table,
                        field.related.field.attname)
                    # Now that we have the table, we need to retreive
                    # the revelant fields name on this table to create
                    # the extra(s) we need.
                    #
                    # There is 2 forms of aggregate.
                    #
                    # The simplest is a string: "count", "sum", "max"...
                    #
                    # The second is a dict we only need to digg into
                    # the dict to retreive the type of aggregate
                    # (count, max, sum etc...) and for each type, the
                    # list of aggregate name
                    for agg in field.related.field.aggregate_trigger:
                        select = {}
                        filters = []
                        if isinstance(agg, dict):
                            # {"count":
                            #      [{"private":
                            #           {"field":
                            #              "somefield",
                            #            "filters":
                            #               "somefilters"},
                            #      ...]
                            for aggregate_type in agg.iterkeys():
                                for agg_filter in agg[aggregate_type]:
                                    for name in agg_filter:
                                        filters.append(
                                            "{}_{}".format(aggregate_type,
                                                           name))
                        else:
                            filters = [agg]

                        for filter in filters:
                            # We have to construct the query to call
                            # in the extra, a little more
                            # introspection here
                            #
                            # - "agg_{}".format(filter) => the filter we
                            #                              found earlier, with
                            #                              a agg_ prepended to
                            #                              avoid name clash
                            #
                            # - table : the table name found earlier
                            #
                            # - field.related.field.attname => the column name
                            #                          of the relation to the
                            #                          working models on the
                            #                          reverse related model
                            #                          (are you still with me?)
                            #                          Working model is Article
                            #                          ArticleComment has a
                            #                          foreignkey to Article,
                            #                          named "article", in the
                            #                          database, the column is
                            #                          article_id
                            # - self.model._meta.db_table => the model table we
                            #                                are working on
                            # - self.model._meta.pk.name => the column name of
                            #                               the working model
                            #                               pk
                            #
                            param = "select {} from {} where {}={}.{}".format(
                                "agg_{}".format(filter),
                                table,
                                field.related.field.attname,
                                self.model._meta.db_table,
                                self.model._meta.pk.name)
                            # create the select and create an extra for it
                            select["{}_{}".format(
                                field.related.var_name, filter)] = param
                            qs = qs.extra(select=select)
        # finaly return the augmented queryset
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
