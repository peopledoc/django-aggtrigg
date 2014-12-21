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
import logging
import sys
from django.db import connections


def execute_raw(sql, database='default'):
    """Execute a raw SQL command

    sql (string) : SQL command
    database (string): the database name configured in settings
    """
    try:
        cursor = connections[database].cursor()
        cursor.execute(sql)
        cursor.close()
        return 0
    except:
        logging.error('Cant execute %s' % (sql))
        sys.stderr.write('Cant execute [%s]\n' % (sql))
        sys.exit(1)


def lookup(sql, params=None, database='default'):
    """Execute a raw SQL command

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
        sys.stderr.write("%s\n" % (mogrify(sql, params)))
        return False


def mogrify(sql, params=None, database='default'):
    """Mogrify a command

    sql (string) : SQL command
    database (string): the database name configured in settings
    """
    cursor = connections[database].cursor()
    try:
        return cursor.mogrify(sql, params)
    except AttributeError:
        # SQLite has no mogrify function
        return "%s -> %s" % (sql, params)
