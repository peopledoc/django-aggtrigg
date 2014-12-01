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

2. Import fields in your models::

    from aggregate_trigger.models import IntegerTriggerField
    from aggregate_trigger.models import FloatTriggerField

Manage triggers and related objects
-----------------------------------

To create the triggers just do::

    python manage.py aggtrigg_create

Dropping trigegrs is easy as doing::

    python manage.py aggtrigg_drop

To initialize the aggregeate table, you can fill it by hand or do::

    python manage.py aggtrigg_initialize
