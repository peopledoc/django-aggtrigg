from django.db import models
from django_aggtrigg.models import IntegerTriggerField
from django_aggtrigg.models import FloatTriggerField
from django_aggtrigg.models import ForeignKeyTriggerField
from django_aggtrigg.models import AggCount, AggTriggManager
from djqmixin import Manager

TreeManager = Manager.include(AggCount)


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
        {"count": [{
            "private_leaves": [{"field": "private", "value": False}],
            "public_leaves": models.Q(private=True),
            }]},
        "count"]
