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

3. By default only the `count` agggregat will be create, to user
another on configure your field as is::

    class Apple(models.Model):
        indice = IntegerTriggerField(default=0)
        indice.aggregate_trigger=['count','min']

        mark = FloatTriggerField(default=0)
        indice.aggregate_trigger=['min']

Two aaggregat will be compute for **indice** field, only one will be
done on **mark**


Manage triggers and related objects
-----------------------------------

To create the triggers just do::

    python manage.py aggtrigg_create

Dropping trigegrs is easy as doing::

    python manage.py aggtrigg_drop

To initialize the aggregeate table, you can fill it by hand or do::

    python manage.py aggtrigg_initialize

Howto use the new aggregat
--------------------------

The class **apple** was create in the app called **foo** so the
default name of the table that contains data will be **foo_apple**, we
use the tablename from the Model so if it's changed in **Meta** will
still be compliant.

A new table **foo_apple__indice_agg** is created in the same database
as **foo_apple**, it will contain the aggregat::

    foo=# \d foo_apple__indice_agg
    Table "public.foo_apple__indice_agg"
      Column   |  Type   | Modifiers 
    -----------+---------+-----------
     indice    | integer | 
     agg_count | integer | 
     agg_min   | integer | 
    Indexes:
        "foo_apple__indice_agg_indice_idx" btree (indice)

Instead of doing a COUNT as the traditionnal way::

    Apple.objects.filter(indice=42).count()

you can do:

    Apple.objects.raw("SELECT agg_count FROM foo_apple__indice_agg WHERE indice=%s", [42])

This is may be less easy, but so much more efficient when you
manipulate billions or tuples in your relations.
