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
# * Neither the name of django-json-dbindex nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
#
from django.db import models
from django.db import connection
import tool
import util

class AggTriggManager(models.Manager):
    
    def optimized_count(self, **kwargs):
        """Return count in optimized manner

        Apple.objects.filter(indice=4).count()
        Apple.objects.optimized_count(indice=4)
        
        """
        # do not care about more than one kwarg
        for key, value in kwargs.iteritems():
            print "%s = %s" % (key, value)
            (column, qfilter) = tool.parse_kwarg(key)
        
        cursor = connection.cursor()

        qry = """SELECT agg_count FROM {} WHERE {} %s"""
        tbname = util.table_name(self.model._meta.db_table, column)
        cursor.execute(qry.format(tbname, qfilter), [value])
        row = cursor.fetchone()

        return row[0]


class IntegerTriggerField(models.IntegerField):

    description = "An IntegerField with trigger"

    def __init__(self, *args, **kwargs):
        self.aggregate_trigger = ['count']
        super(IntegerTriggerField, self).__init__(*args, **kwargs)


class FloatTriggerField(models.FloatField):

    description = "An FloatField with trigger"

    def __init__(self, *args, **kwargs):
        self.aggregate_trigger = ['count']
        super(FloatTriggerField, self).__init__(*args, **kwargs)
