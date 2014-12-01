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
from django.db.models import get_models

FILENAME_CREATE = 'dbindex_create.json'
FILENAME_DROP = 'dbindex_drop.json'
PGBACKEND = 'django.db.backends.postgresql_psycopg2'


class DatabaseNotSupported(Exception):
    pass


class DatabaseUnknown(Exception):
    pass


class ActionUnknown(Exception):
    pass


def function_name(table, column, action):
    return "{0}_{1}_{2}()".format(table, column, action)


def trigger_name(table, column, action):
    return "{0}_{1}_{2}_trigger".format(table, column, action)


def table_name(table, column):
    """Compute the table name

    table (string) : the originate table's name
    column : the column name

    return : string
    """
    return "{0}__{1}_agg".format(table, column)


def command_check():
    """
    Check indexes
    """
    for fpath in get_app_paths():
        print fpath


def get_app_paths():
    """Return all paths defined in settings
    """
    trigg = []
    classes = ["<class 'foo.aggtrigg.models.IntegerTriggerField'>",
               "<class 'foo.aggtrigg.models.FloatTriggerField'>"]

    for model in get_models():
        for field in model._meta.fields:
            if str(field.__class__) in classes:
                trigg.append({"model": model,
                              "table": model._meta.db_table,
                              "field": field.name,
                              "aggs": field.aggregate_trigger})

    return trigg
