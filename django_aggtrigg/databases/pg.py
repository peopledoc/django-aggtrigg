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

from jinja2 import Environment, FileSystemLoader
import os


class TriggerPostgreSQL(object):

    def __init__(self):
        self.name = "PostgreSQL"

    def sql_create_table(self, name, column, aggregats):
        """Return a SQL statement to create a FUNCTION

        name : functions name
        column (tuple): column name and typname
        aggregats (array): aggregats used
        """
        tpl = os.path.join(os.path.dirname(__file__), 'templates')
        env = Environment(loader=FileSystemLoader(tpl))

        template = env.get_template('pg_create_table.sql')
        aggs = []
        for agg in aggregats:
            aggs.append({"name": agg,
                         "type": column[1]})

        return template.render(name=name,
                               column={"name": column[0], "type": column[1]},
                               aggregats=aggs)

    def sql_drop_table(self, name):
        """Return a command to drop a table in PostgreSQL

        name (string) : the table name
        """
        return "DROP TABLE IF EXISTS {0}".format(name)

    def sql_drop_trigger(self, name, table):
        """Return a command to drop a trigger in PostgreSQL

        name (string): the triggers's name
        table (string) : the table name
        """
        return "DROP TRIGGER IF EXISTS {0} ON {1}".format(name, table)

    def sql_drop_function(self, name):
        """Return a command to drop a function in PostgreSQL

        name (string): the function's name to drop
        """
        return "DROP FUNCTION IF EXISTS {0}".format(name)

    def sql_create_trigger(self, name, function, table, action):
        """Return the SQL statement to create a trigger

        name (string): the function's name to call
        """
        return """CREATE TRIGGER {0} AFTER {3} ON {2}
        FOR EACH ROW
        EXECUTE PROCEDURE {1}""".format(name, function, table, action.upper())

    def sql_create_function_insert(self, name, table, column, aggtable):
        """Return a SQL statement to create a FUNCTION

        name : function name
        table (string) : the originate of datas
        column : column name
        aggtable : the table where data will be stored
        """
        tpl = os.path.join(os.path.dirname(__file__), 'templates')
        env = Environment(loader=FileSystemLoader(tpl))

        template = env.get_template('pg_function_insert.sql')

        actions = "agg_count=agg_count+1"

        insert_values = 1

        return template.render(name=name,
                               table=table,
                               aggtable=aggtable,
                               column=column,
                               actions=actions,
                               insert_values=insert_values)

    def sql_create_function_delete(self, name, column, aggtable, action):
        """Return a SQL statement to create a FUNCTION

        name : functions name
        column : column name
        aggtable : the table where data will be stored
        action : action that fired the trigger
        """
        tpl = os.path.join(os.path.dirname(__file__), 'templates')
        env = Environment(loader=FileSystemLoader(tpl))
        template = env.get_template('pg_function_delete.sql')

        actions = "agg_count=agg_count-1"

        return template.render(name=name,
                               table=aggtable,
                               column=column,
                               actions=actions)

    def sql_create_function_update(self, name, column, aggtable, action):
        """Return a SQL statement to create a FUNCTION

        name : functions name
        column : column name
        aggtable : the table where data will be stored
        action : action that fired the trigger
        """
        tpl = os.path.join(os.path.dirname(__file__), 'templates')
        env = Environment(loader=FileSystemLoader(tpl))

        template = env.get_template('pg_function_update.sql')

        actions_new = "agg_count=agg_count+1"
        actions_old = "agg_count=agg_count-1"

        return template.render(name=name,
                               table=aggtable,
                               column=column,
                               actions_old=actions_old,
                               actions_new=actions_new)

    def sql_get_column_typname(self):
        """Return the query to find the typename of a column
        """
        qry = " ".join(["SELECT typname",
                        "FROM pg_class,pg_attribute,pg_type",
                        "WHERE relname=%s",
                        "AND attname=%s",
                        "AND atttypid=pg_type.oid",
                        "AND attrelid=pg_class.oid"])
        return (qry, None)

    def sql_init_aggtable(self, name, column, aggname, aggregats):
        """Return a SQL statement to initialize aggregate table

        name : functions name
        column (tuple): column name and typname
        aggname (string) : aggregate table name
        aggregats (array): aggregats used
        """
        tpl = os.path.join(os.path.dirname(__file__), 'templates')
        env = Environment(loader=FileSystemLoader(tpl))

        template = env.get_template('pg_init.sql')
        aggs = []
        for agg in aggregats:
            aggs.append(agg)
        return template.render(table=name,
                               aggtable=aggname,
                               column=column,
                               aggregats=aggs)

    def sql_nb_tuples(self):
        """Return a SQL statement to know appox number of tuples in a table
        """
        qry = """SELECT reltuples FROM pg_class WHERE relname=%s"""
        return qry

    def agg_fname(self, agg, fname):

        AGGS = {'count': 'SUM',
                'max': 'GREATEST',
                'min': 'LEAST'}

        try:
            res = "%s(%s)" % (AGGS[agg], fname)
        except KeyError:
            res = fname

        return res

    def sql_table_exists(self):
        """Return the query to find the typename of a column
        """
        qry = " ".join(["SELECT count(relname)",
                        "FROM pg_class",
                        "WHERE relname=%s",
                        "AND relkind='r'"])
        return qry

    def sql_trigger_on_table_exists(self):
        """Return the query to find the typename of a column
        """
        qry = " ".join(["SELECT count(pg_trigger.tgname)",
                        "FROM pg_trigger,pg_class",
                        "WHERE pg_trigger.tgrelid=pg_class.oid",
                        "AND pg_trigger.tgname=%s",
                        "AND pg_class.relname=%s"])
        return qry

    def sql_trigger_function_on_table_exists(self):
        """Return the query to find the typename of a column
        """
        qry = " ".join(["SELECT count(pg_trigger.tgname)",
                        "FROM pg_trigger,pg_class,pg_proc",
                        "WHERE pg_trigger.tgrelid=pg_class.oid",
                        "AND pg_trigger.tgfoid=pg_proc.oid",
                        "AND pg_proc.proname=%s",
                        "AND pg_class.relname=%s"])
        return qry
