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
from django.db import connection
from django.core.management.base import BaseCommand
from optparse import make_option
from ... import util


class Command(BaseCommand):
    help = 'Import datas'
    option_list = BaseCommand.option_list + (
        make_option("-y",
                    "--yes",
                    dest="action",
                    action="store_true",
                    help="number of values to input",
                    default=False),
        )


    def handle(self, *args, **options):
        """
        Read the table book without TextField
        """
        agg = util.AggTrigger()

        aggs = ['count']
        column = 'author_id'
        table = 'tuna_book'

        sql = """WITH cte AS ( SELECT {1} a, count({1}) c FROM {0} GROUP BY {1} )
        SELECT a FROM cte LEFT JOIN {0}_{1}_agg ON ({0}_{1}_agg.{1} = cte.a)
        WHERE agg_{2} <> c OR agg_count IS NULL;
        """.format(table, column, 'count')

        if options['action']:
            cursor = connection.cursor()
            cursor.execute(sql)
            row = cursor.fetchone()
            print row
        else:
            print 'Warning, this may generate a high load on you server, if you really want to do, use -y option'
            print sql
