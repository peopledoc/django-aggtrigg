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
from django.db.models import get_models

CLASSES = ["aggregat_trigger.models.IntegerTriggerField",
           "aggregat_trigger.models.FloatTriggerField"]

def is_trigg_field(fieldclass):
    """Check if the field is a triggered field

    <class 'foo.aggregat_trigger.models.IntegerTriggerField'>
    <class 'foo.aggregat_trigger.models.FloatTriggerField'>    
    """
    ift = False
    fdc = fieldclass.split("'")
    for fclass in CLASSES:
        ift = ift or fdc[1].endswith(fclass)
    return ift

def get_agg_fields():
    """Return all special field defined
    """
    trigg = []

    for model in get_models():
        for field in model._meta.fields:
            if is_trigg_field(str(field.__class__)):
                trigg.append({"model": model,
                              "table": model._meta.db_table,
                              "field": field.name,
                              "aggs": field.aggregate_trigger})

    return trigg
