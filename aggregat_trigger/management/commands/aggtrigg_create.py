#!/usr/bin/env python
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
import sys
from django.core.management.base import BaseCommand
from optparse import make_option
from ... import util


class Command(BaseCommand):
    help = 'Import datas'
    option_list = BaseCommand.option_list + (
        make_option("-s",
                    "--simulate",
                    dest="simulate",
                    action="store_true",
                    help="juste print on stdout SQL commande, do nothing",
                    default=False),
        make_option("-t",
                    "--table",
                    dest="table",
                    type="string",
                    help="table name",
                    default=None),
        make_option("-c",
                    "--column",
                    dest="column",
                    type="string",
                    help="column name",
                    default=None),
        make_option("-q",
                    "--quiet",
                    dest="quiet",
                    action="store_true",
                    default=False))

    def handle(self, *args, **options):
        """
        Handle action
        """
        if options['quiet']:
            options['verbosity'] = 0

        for trig in util.get_app_paths():
            self.create_trigger(trig, options)

    def create_trigger(self, trig, options):
        """
        {'table': u'apple_apple',
         'model': <class 'foo.apple.models.Apple'>,
         'aggs': ['max'],
         'field': 'indice'}
        """
        aggs = trig['aggs']
        column = trig['field']
        table = trig['table']

        agg = util.AggTrigger(table, column, aggs)
        agg.verbose = int(options['verbosity'])

        comment = "-- table:    %s\n-- column:   %s\n-- aggregat: %s\n"

        if table and column and len(aggs) > 0:
            if not options['simulate']:
                agg.create_objects()
                if options['verbosity'] > 0:
                    sys.stdout.write(comment % (table, column, aggs))
                    sys.stdout.write("Create table : %s\n" % (agg.table_name))

            #  do nothing
            else:
                for sql in agg.sql_create_functions(table, column, aggs):
                    sys.stdout.write(comment % (table, column, aggs))
                    sys.stdout.wrtite(sql)
                for sql in agg.sql_create_triggers(table, column):
                    sys.stdout.wrtite(sql)
                print agg.sql_create_table(table, column, aggs)
