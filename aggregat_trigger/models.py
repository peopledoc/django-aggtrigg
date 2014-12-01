from django.db import models


class IntegerTriggerField(models.IntegerField):

    description = "An IntegerField with trigger"

    def __init__(self, *args, **kwargs):
        self.aggregate_trigger = ['count']
        super(IntegerTriggerField, self).__init__(*args, **kwargs)


class FloatTriggerField(models.FloatField):

    description = "An FloatField with trigger"

    def __init__(self, *args, **kwargs):
        self.aggregate_trigger = ['count']
        super(FloatTriggerField, self).__init__(*args, **kwargs)
