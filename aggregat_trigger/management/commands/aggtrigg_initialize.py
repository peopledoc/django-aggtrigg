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
from ... import util


class Command(BaseCommand):
    help = 'Import datas'

    def handle(self, *args, **options):
        """
        Read the table book without TextField
        """
        for trig in util.get_app_paths():
            self.init_agg(trig, options)

    def init_agg(self, trig, options):
        """
        {'table': u'apple_apple',
         'model': <class 'foo.apple.models.Apple'>,
         'aggs': ['max'],
         'field': 'indice'}
        """
        agg = util.AggTrigger(trig['table'], trig['field'], trig['aggs'])
        agg.verbose = int(options['verbosity'])

        message = u" ".join([u"Are you sure you want to initialize\n",
                             u"%s approx %s tuples in source,",
                             u"maybe long : [Y/n] "])

        answer = raw_input(message % (agg.table_name, agg.get_nb_tuples()))
        if answer == "Y":
            sys.stdout.write("Initialize %s" % (agg.table_name))
            agg.initialize()
        else:
            return
