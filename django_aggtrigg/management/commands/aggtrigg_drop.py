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
from optparse import make_option
from django.core.management.base import BaseCommand
from django.conf import settings
from ... import util
import djutil


class Command(BaseCommand):
    help = 'Drop database relations'
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
        """Do the job
        """
        if options['quiet']:
            options['verbosity'] = 0

        for trig in djutil.get_agg_fields():
            self.drop_trigger(trig, options)

    def drop_trigger(self, trig, options):
        aggs = trig['aggs']
        column = trig['field']
        table = trig['table']

        engine = settings.DATABASES[options['database']]['ENGINE']

        agg = util.AggTrigger(engine, table, column, aggs)

        comment = "-- table:    %s\n-- column:   %s\n-- aggregat: %s\n"
        sys.stdout.write("Warning, this will drop triggers and Table\n")
        sys.stdout.write(comment % (agg.table_name, column, aggs))
        print agg.drop_objects()
