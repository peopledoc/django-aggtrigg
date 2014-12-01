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
        aggs = trig['aggs']
        column = trig['field']
        table = trig['table']

        agg = util.AggTrigger(table, column, aggs)
        agg.verbose = int(options['verbosity'])

        answer = raw_input(u"Are you sure you want to initialize %s approx %s tuples in source, maybe long : [YES/n]" % (
            table, 400)
        if answer != "YES":
            return
                  

        
        agg.initialize()



