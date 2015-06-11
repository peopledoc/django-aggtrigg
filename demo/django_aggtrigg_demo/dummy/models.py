from django.db import models
from django_aggtrigg.models import IntegerTriggerField
from django_aggtrigg.models import FloatTriggerField
from django_aggtrigg.models import ForeignKeyTriggerField
from django_aggtrigg.models import AggCount, AggTriggManager
from django import get_version
from distutils.version import LooseVersion
from djqmixin import Manager

if LooseVersion(
            get_version()) < LooseVersion("1.7.0"):
    TreeManager = Manager.include(AggCount)
else:
    TreeManager = AggCount.as_manager


class Apple(models.Model):
    """An apple
    """
    name = models.CharField(max_length=300)

    indice = IntegerTriggerField(default=0)
    indice.aggregate_trigger = ['count']

    mark = FloatTriggerField(default=0)
    indice.aggregate_trigger = ['count', 'min']

    objects = AggTriggManager()


class Tree(models.Model):
    name = models.CharField(max_length=300)
    objects = TreeManager()


class Leave(models.Model):
    name = models.CharField(max_length=300)
    tree = ForeignKeyTriggerField(Tree)
    private = models.BooleanField()
    tree.aggregate_trigger = [
        {"count": [
            {"private_leaves": [{"field": "private", "value": True}]},
            {"public_leaves": [{"field": "private", "value": False}]},
        ]},
        "count"]
