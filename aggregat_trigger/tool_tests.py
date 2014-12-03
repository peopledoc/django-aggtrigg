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
import tool


class utilTests(unittest.TestCase):

    def test_equal(self):
        res = tool.parse_kwarg("foo")
        self.assertEqual(res, (1, 'foo', 'foo='))

    def test_greater_than(self):
        res = tool.parse_kwarg("foo__gt")
        self.assertEqual(res, (2, 'foo', 'foo >'))

    def test_greater_or_equal_than(self):
        res = tool.parse_kwarg("foo__gte")
        self.assertEqual(res, (2, 'foo', 'foo >='))

    def test_less_than(self):
        res = tool.parse_kwarg("foo__lt")
        self.assertEqual(res, (2, 'foo', 'foo <'))

    def test_less_or_equal_than(self):
        res = tool.parse_kwarg("foo__lte")
        self.assertEqual(res, (2, 'foo', 'foo <='))
