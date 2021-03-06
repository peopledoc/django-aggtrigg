from django.db import models
from django_aggtrigg.models import IntegerTriggerField
from django_aggtrigg.models import FloatTriggerField
from django_aggtrigg.models import ForeignKeyTriggerField
from django_aggtrigg.models import AggCount, AggTriggManager


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
    private = models.BooleanField(default=False)
    tree.aggregate_trigger = [
        {"count": [
            {"private_leaves": [{"field": "private", "value": True}]},
            {"public_leaves": [{"field": "private", "value": False}]},
        ]},
        "count"]
