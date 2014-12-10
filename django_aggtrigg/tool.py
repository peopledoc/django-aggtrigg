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


def parse_kwarg(arg):
    """Parse a string and build the corresponding SQL filter
    """
    ops = {'=': '=',
           'gt': '>',
           'gte': '>=',
           'lt': '<',
           'lte': '<='}

    cols = arg.split('__')

    nbe = len(cols)

    if nbe == 1:
        sqw = "%s=" % (cols[0])
    if nbe == 2:
        sqw = "%s %s" % (cols[0], ops[cols[1]])
    return (nbe, cols[0], sqw)
