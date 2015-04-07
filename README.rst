django-aggtrigg
===============

Automatic trigger generator for Django

.. image:: https://img.shields.io/pypi/v/djorm-pgarray.svg?style=flat
    :target: https://pypi.python.org/pypi/django-aggtrigg

.. image:: https://img.shields.io/pypi/dm/djorm-pgarray.svg?style=flat
    :target: https://pypi.python.org/pypi/django-aggtrigg

Create triggers to do some aggregate and permit to count objects from
database without using COUNT() aggregat.
Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "django_aggtrigg" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'django_aggtrigg',
    )

2. Import fields in your models::

    from django_aggtrigg.models import IntegerTriggerField
    from django_aggtrigg.models import FloatTriggerField

3. Configure your fields as is::

    class Apple(models.Model):
        indice = IntegerTriggerField(default=0)
        indice.aggregate_trigger=['count','min']

        mark = FloatTriggerField(default=0)
        mark.aggregate_trigger=['min']

By default only the `count` aggregat will be created.

4. Use the new manager on you Model

    objects = AggTriggManager()


Manage triggers and related objects
-----------------------------------

To create the triggers in the database do::

    python manage.py aggtrigg_create

Dropping triggers is easy as doing::

    python manage.py aggtrigg_drop | psql -d DATABASE NAME

For safety reason the drop command just ouptput on stdout the SQL statements.

To initialize the aggregeate table, you can fill it by hand or do::

    python manage.py aggtrigg_initialize

Howto use the new aggregat
--------------------------

Instead of doing a COUNT as the traditionnal way::

    Apple.objects.filter(indice=42).count()

you will do::

    Apple.objects.optimized_count(indice=42)

This is may be less easy, but so much more efficient when you
manipulate billions or tuples in your relations.

What inside
-----------

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

Aggregate on related table
--------------------------

If you need to maintain count on related objects, for example the
comment count per Article, you can use ForeignKeyTriggerField::

    from django_aggtrigg.models import ForeignKeyTriggerField

Trade the ForeignKey on ArticleComment for a ForeignKeyTriggerField::

    class ArticleComment(models.Model):
        ...
        article = ForeignKeyTriggerField(Article)
        ...

Add simple count::

        article.aggregate_trigger = ["count"]

Or complex one with some filters::

        article.aggregate_trigger = {'count': [
                                        {'private': [ {
                                            "field": "is_private",
                                            "value": False}
                                                     ]
                                         }
                                               ]
                                     }

Create your triggers::

    python manage.py aggtrigg_create

Initialize your triggers::

    python manage.py aggtrigg_initialize


To use those triggers easily, you can use AggCount manager::

    from django_aggtrigg.models import AggCount

    ArticleManager = Manager.include(AggCount)

AggCount give you a new method on your model: ``get_count``. You can
use it juste like a traditional queryset method. ex::

    Article.objects.filter(..).get_count().values("articlecomment_count_private")
    [{'ticketcomment_count_private': 4},
    {'ticketcomment_count_private': 2},..]

    Article.objects.filter(..).get_count().first().__dict__
    {'id': 24,
     ...
     'ticketcomment_count_private': 3
     ...}

The only thing you cannot do with get_count is filtering on the
aggregates. ex::

    Article.objects.get_count().filter(articlecomment_count_private__gte=3)
    # THIS DOES NOT WORK !!!

Because the aggregates are not on the table you working on, Django
does not really know anything about this table. THis is the reason why
you do not have to bother with migrations.
