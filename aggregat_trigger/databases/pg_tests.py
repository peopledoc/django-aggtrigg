#! /usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 Rodolphe Quiedeville <rodolphe@quiedeville.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
from pg import TriggerPostgreSQL


class utilTests(unittest.TestCase):

    def setUp(self):
        self.agg = TriggerPostgreSQL()
        self.maxDiff = None

    def test_init(self):
        trig = TriggerPostgreSQL()
        self.assertEqual('PostgreSQL', trig.name)

    def test_sql_drop_trigger(self):
        res = self.agg.sql_drop_trigger('foo', 'table_bar')
        self.assertTrue(isinstance(res, str))
        #  TODO mov test to pgTests
        #  self.assertEqual(res, 'DROP TRIGGER IF EXISTS foo ON table_bar')

    def test_sql_drop_function(self):
        res = self.agg.sql_drop_function('foo')
        self.assertTrue(isinstance(res, str))

    def test_sql_drop_table(self):
        res = self.agg.sql_drop_table('table_bar')
        self.assertTrue(isinstance(res, str))

    def test_sql_create_function_insert(self):
        trig = TriggerPostgreSQL()
        res = trig.sql_create_function_insert('book_nbpage_insert()',
                                              'book',
                                              'nbpage',
                                              'book_nbpage')

        attend = u"""CREATE OR REPLACE FUNCTION book_nbpage_insert() RETURNS TRIGGER AS $BODY$
BEGIN
IF (SELECT nbpage FROM book_nbpage WHERE nbpage=NEW.nbpage) IS NOT NULL THEN
    UPDATE book_nbpage SET agg_count=agg_count+1 WHERE nbpage=NEW.nbpage;
ELSE
    INSERT INTO book_nbpage VALUES (NEW.nbpage, 1);
END IF;
RETURN NEW;
END;
$BODY$ LANGUAGE plpgsql;"""
        self.assertEqual(res, attend)

    def test_sql_create_table(self):
        """Test with only one aggregat
        """
        res = self.agg.sql_create_table('book', 'nbpage', ['count'])

        attend = u"""CREATE TABLE book (nbpage int4, agg_count int4);
CREATE INDEX ON book (nbpage);"""

        self.assertEqual(res, attend)

    def test_sql_create_table_twoagg(self):
        """Test with two aggregats
        """
        res = self.agg.sql_create_table('book', 'nbpage', ['count', 'min'])

        attend = u"""CREATE TABLE book (nbpage int4, agg_count int4, agg_min int4);
CREATE INDEX ON book (nbpage);"""

        self.assertEqual(res, attend)
