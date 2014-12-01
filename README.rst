===================
django-aggtrigg
===================

Describe your database index in json files into your apps

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "aggregate_trigger" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'aggregate_trigger',
    )

2. Import IntegerTriggerField in yoour models::

    from aggregate_trigger.models import IntegerTriggerField

Create indexes
--------------

