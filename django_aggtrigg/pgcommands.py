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
import logging
from django.db import connections


def index_exists(index, database='default'):
    """Execute raw sql
    """
    cursor = connections[database].cursor()
    qry = "SELECT COUNT(indexname) FROM pg_indexes WHERE indexname = %s"
    cursor.execute(qry, [index['name']])
    row = cursor.fetchone()
    cursor.close()
    return row[0] == 1


def execute_raw(sql, database='default'):
    """
    Execute a raw SQL command

    sql (string) : SQL command
    database (string): the database name configured in settings
    """
    cursor = connections[database].cursor()
    cursor.execute(sql)
    cursor.close()
    return 0


def lookup(sql, params=None, database='default'):
    """
    Execute a raw SQL command

    sql (string) : SQL command
    database (string): the database name configured in settings
    """
    try:
        cursor = connections[database].cursor()
        cursor.execute(sql, params)
        row = cursor.fetchone()
        cursor.close()
        return row[0]
    except:
        logging.error('Cant execute %s' % (sql))
        return False


def mogrify(sql, params=None, database='default'):
    """Mogrify a command

    sql (string) : SQL command
    database (string): the database name configured in settings
    """
    cursor = connections[database].cursor()
    return cursor.mogrify(sql, params)


def drop_index(index, database='default'):
    """
    Check if index exists and drop it

    index (dict) : index description
    """
    if 'database' in index:
        database = index['database']

    if index_exists(index, database):
        logging.info("Will drop %s" % index['name'])

        res = execute_raw(index['cmd'], database)

        logging.info("%s dropped" % index['name'])
    else:
        res = 1
        logging.info("%s doesn't exists" % index['name'])
    return res


def create_index(index, database='default'):
    """
    Create an index

    index (dict) : index description
       {"name": "foo",
        "database": "default",
        "cmd": "CREATE INDEX foo_idx ON table (column)"
       }
    """
    if 'database' in index:
        database = index['database']

    if index_exists(index, database):
        logging.info("%s still exists" % index['name'])
        res = 1
    else:
        logging.info("Will create %s" % index['name'])
        res = execute_raw(index['cmd'], database)
        logging.info("%s created" % index['name'])
    return res
