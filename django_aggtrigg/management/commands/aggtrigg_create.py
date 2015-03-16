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
# * Neither the name of django-aggtrigg nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
#
import sys
from django.core.management.base import BaseCommand
from django.conf import settings
from optparse import make_option
from ... import util
from .. import djutil


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
        make_option("-d",
                    "--database",
                    dest="database",
                    type="string",
                    help="table name",
                    default="default"),
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

        for trig in djutil.get_agg_fields():
            self.create_trigger(trig, options)

    def create_trigger(self, trig, options):
        """
        {'table': u'apple_apple',
         'model': <class 'foo.apple.models.Apple'>,
         'aggs': ['max'],
         'field': 'indice'}
        """
        aggs = trig['aggs']
        # rely on django to find the "real" column name. foreignkeys
        # names are "relation" but column is "relation_id"
        model = trig["model"]
        column = model._meta.get_field(trig['field']).attname
        table = trig['table']
        engine = settings.DATABASES[options['database']]['ENGINE']
        agg = util.AggTrigger(engine, table, column, aggs, model=model)
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
                sys.stdout.write("%s\n" % (agg.sql_create_table()))
                for sql in agg.sql_create_functions():
                    sys.stdout.write(comment % (table, column, aggs))
                    sys.stdout.write("%s\n" % (sql))
                for tgs in agg.sql_create_triggers():
                    sys.stdout.write("%s\n" % (tgs[1]))
