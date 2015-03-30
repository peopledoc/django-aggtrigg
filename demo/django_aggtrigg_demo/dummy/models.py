from django.db import models
from django_aggtrigg.models import IntegerTriggerField
from django_aggtrigg.models import FloatTriggerField
from django_aggtrigg.models import AggTriggManager


class Apple(models.Model):
    """An apple
    """
    name = models.CharField(max_length=300)

    indice = IntegerTriggerField(default=0)
    indice.aggregate_trigger = ['count']

    mark = FloatTriggerField(default=0)
    indice.aggregate_trigger = ['count', 'min']

    objects = AggTriggManager()
