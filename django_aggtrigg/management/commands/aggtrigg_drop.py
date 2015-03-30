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
from optparse import make_option
from django.core.management.base import BaseCommand
from django.conf import settings
from ... import util
from .. import djutil


class Command(BaseCommand):
    """Print SQL Statements on STDOUT to DROP all objects
    """
    help = 'Drop database relations'
    option_list = BaseCommand.option_list + (
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
                    default="default"))

    def handle(self, *args, **options):
        """Do the job
        """
        for trig in djutil.get_agg_fields():
            self.drop_trigger(trig, options)

    def drop_trigger(self, trig, options):
        aggs = trig['aggs']
        model = trig["model"]
        column = model._meta.get_field(trig['field']).attname
        table = trig['table']

        engine = settings.DATABASES[options['database']]['ENGINE']

        agg = util.AggTrigger(engine, table, column, aggs, model=model)

        for sqltrig in agg.sql_drop_triggers():
            sys.stdout.write("%s;\n" % (sqltrig))

        for sqlfunc in agg.sql_drop_functions():
            sys.stdout.write("%s;\n" % (sqlfunc))
        sys.stdout.write("%s;\n" % (agg.sql_drop_table()))
