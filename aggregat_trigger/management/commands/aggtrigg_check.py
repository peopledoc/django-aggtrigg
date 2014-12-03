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
from django.conf import settings
from optparse import make_option
from ... import util
import djutil


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
        make_option("-d",
                    "--database",
                    dest="database",
                    type="string",
                    help="table name",
                    default="default"),
        make_option("-c",
                    "--column",
                    dest="column",
                    type="string",
                    help="column name",
                    default=None))


    def handle(self, *args, **options):
        """
        Handle action
        """
        trigs = djutil.get_agg_fields()
        sys.stdout.write("found %d triggers\n" % (len(trigs)))
        for trig in trigs:
            self.check_trigger(trig, options)

    def check_trigger(self, trig, options):
        """
        {'table': u'apple_apple',
         'model': <class 'foo.apple.models.Apple'>,
         'aggs': ['max'],
         'field': 'indice'}
        """
        aggs = trig['aggs']
        column = trig['field']
        table = trig['table']

        engine = settings.DATABASES[options['database']]['ENGINE']

        agg = util.AggTrigger(engine, table, column, aggs)
        agg.verbose = int(options['verbosity'])

        comment = "--\nmodel: %s\ntable: %s, column: %s, aggregats: %s\n"

        if table and column and len(aggs) > 0:
            sys.stdout.write(comment % (trig['model'], table, column, aggs))
