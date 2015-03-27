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
from django.db.models import get_models
from django_aggtrigg.models import TriggerFieldMixin


def get_agg_fields():
    """Return all special field defined
    """
    trigg = []

    for model in get_models():

        for field in model._meta.fields:

            if isinstance(field, TriggerFieldMixin):
                trigg.append({"model": model,
                              "table": model._meta.db_table,
                              "field": field.name,
                              "aggs": field.aggregate_trigger})

    return trigg
