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
# * Neither the name of django-json-dbindex nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
#
from django.utils.importlib import import_module
from django.db.models import get_app, get_models
from django.conf import settings
import json
import sys
import re
import logging
import pgcommands
from databases import pg




from os import path

FILENAME_CREATE = 'dbindex_create.json'
FILENAME_DROP = 'dbindex_drop.json'

class DatabaseNotSupported(Exception):
    pass

def command_check():
    """
    Check indexes
    """
    for fpath in get_app_paths():
        print fpath


def command_list():
    """
    List all indexes
    """
    for fpath in get_app_paths():
        indexes = list_indexes(fpath)
        if len(indexes):
            sys.stdout.write("-- Found %d index in %s\n" % (len(indexes),
                                                            fpath))
            for index in indexes:
                sys.stdout.write("%s\n" % (index['cmd']))


def get_app_paths():
    """
    Return all paths defined in settings
    """
    for model in get_models():
        for field in model._meta.fields:
            if str(field.__class__) == "<class 'foo.aggtrigg.models.IntegerTriggerField'>":
                print field.aggregate_trigger
            

    return ""

def create_table(name):
    """
    --
    -- Table technique, mise à jour par triggers
    --
    """

    sql = """
CREATE TABLE boats_per_skipper (
  skipper_id int,
  nb_boats int
);
"""
    index =  """    
CREATE CONCURRENTLY INDEX idx_c_one ON boats_per_skipper (skipper_id, nb_boats);
"""

def sql_init(name):
    """
    Remplissage de la table technique avec les données existantes
    """

    sql = """
    BEGIN;
    
    LOCK TABLE skipper IN EXCLUSIVE MODE;
    LOCK TABLE boat IN EXCLUSIVE MODE;
    
    DELETE FROM boats_per_skipper;
    
    INSERT INTO boats_per_skipper (
    SELECT skipper.id, count(boat.skipper_id) 
    FROM skipper 
    LEFT JOIN boat ON boat.skipper_id = skipper.id 
    GROUP BY skipper.id );

    COMMIT;
    """

def drop_functions(name, column, aggregate):

    sql = sql_drop_functions(name, column, aggregate)
    pgcommands.execute_raw(sql)

        
def sql_drop_functions(table, column, aggregate):
    """
    Functions appellées par les triggers
    """
    return sql_postgres_drop_functions(table, column, aggregate)

def sql_postgres_drop_functions(table, column, aggregate):
    """
    Functions appellées par les triggers
    """

    sql = """
    DROP FUNCTION {0}_insert();
    DROP FUNCTION {0}_insert();
    DROP FUNCTION {0}_insert();
    """.format(table, column, aggregate)
    return sql

def sql_create_functions(table, column, aggregate):
    """
    Functions appellées par les triggers
    """

    sql = """
    CREATE OR REPLACE FUNCTION {0}_insert() RETURNS TRIGGER AS $BODY$
    BEGIN 
    INSERT INTO {0}_{2} ({0}_{1}, {1}_{2}) VALUES (NEW.{1}, 0 );
    RETURN NEW;
    END;
    $BODY$ LANGUAGE plpgsql;

    CREATE OR REPLACE FUNCTION {0}_delete() RETURNS TRIGGER AS $BODY$
    BEGIN 
    DELETE FROM {0}_{2} WHERE {0}_id = OLD.{1};
    RETURN NEW;
    END;
    $BODY$ LANGUAGE plpgsql;

    CREATE OR REPLACE FUNCTION {0}_update() RETURNS TRIGGER AS $BODY$
    BEGIN 
    IF NEW.skipper_id != OLD.skipper_id THEN
    UPDATE boats_per_skipper SET nb_boats = nb_boats - 1 WHERE skipper_id = OLD.skipper_id;
    UPDATE boats_per_skipper SET nb_boats = nb_boats + 1 WHERE skipper_id = NEW.skipper_id;
    END IF;
    RETURN NEW;
    END;
    $BODY$ LANGUAGE plpgsql;
    """.format(table, column, aggregate)

    return sql

def create_trigger(name):

    sql =  sql_create_functions(name, 'id', 'count')
    pgcommands.execute_raw(sql)

    
    sql =  sql_triggers(name)
    pgcommands.execute_raw(sql)

def drop_triggers(name):

    for sql in sql_drop_triggers(name):
        pgcommands.execute_raw(sql)


def sql_drop_triggers(table, database='default'):
    """DROP triggers

    table (string) : the table name
    """
    sql = []
    for action in ["insert", "update", "delete"]:
        name = "{0}_{1}_trigger".format(table, action)
        sql.append(sql_drop_trigger(name, table, database))

    return sql

def sql_drop_trigger(name, table, database):

    if settings['DATABASES'][database] = 'django.db.backends.postgresql_psycopg2':
        pg.sql_drop_trigger(name, table)
    else:
        raise DatabaseNotSupported()

def sql_triggers(name):
    """
    --
    -- Declaration des triggers
    --
    """
    sql = """

    CREATE TRIGGER {0}_insert_trigger
    AFTER INSERT ON {0}
    FOR EACH ROW
    EXECUTE PROCEDURE {0}_insert();
    
    CREATE TRIGGER {0}_delete_trigger
    AFTER DELETE ON {0}
    FOR EACH ROW
    EXECUTE PROCEDURE {0}_delete();
    """.format(name)

    return sql
