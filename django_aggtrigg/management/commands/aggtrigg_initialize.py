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
    help = 'Import datas'
    option_list = BaseCommand.option_list + (
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
        Read the table book without TextField
        """
        for trig in djutil.get_agg_fields():
            self.init_agg(trig, options)

    def init_agg(self, trig, options):
        """
        {'table': u'apple_apple',
         'model': <class 'foo.apple.models.Apple'>,
         'aggs': ['max'],
         'field': 'indice'}
        """
        engine = settings.DATABASES[options['database']]['ENGINE']

        agg = util.AggTrigger(
            engine,
            trig['table'],
            trig["model"]._meta.get_field(trig['field']).attname,
            trig['aggs'])

        agg.verbose = int(options['verbosity'])

        message = u" ".join([u"Are you sure you want to initialize %s ?\n",
                             u"%s contains %s tuples approximatively,",
                             u"maybe long : [y/N] (please type yes to do)\n"])

        answer = raw_input(message % (agg.table_name,
                                      trig['table'],
                                      agg.get_nb_tuples()))
        if answer == "yes":
            sys.stdout.write(" Initialize %s ...\n" % (agg.table_name))
            agg.initialize()
            sys.stdout.write(" done, %s is initialized\n" % (agg.table_name))
        else:
            return
