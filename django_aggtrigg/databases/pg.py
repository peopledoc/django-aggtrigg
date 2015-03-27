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
from django_aggtrigg.util import parse_where_clause
import os


class TriggerPostgreSQL(object):

    def __init__(self):
        self.name = "PostgreSQL"

    def sql_create_table(self, name, column, aggregats):
        """Return a SQL statement to create a FUNCTION

        name : functions name
        column (tuple): column name and typname
        aggregats (array): aggregats used

        - Each aggregate can be of 2 kind. string or dict.

        string is the simplest it can be on of count, max, sum, etc...

        dict is in the form:
            - aggregate_type:
                - pretty name
                    - list of filters with field and value.
        example::

            {"count":
                [
                    {"private": [
                        {"field": "is_private", "value": True}
                       ]
                    }
                ]
            }

        each "agg_type" can have more than one aggregate (one for
        public another for private for example), each aggregate can
        have multiple filters. All filters are ANDed OR and NOR is not
        possible for the moment.

        """
        tpl = os.path.join(os.path.dirname(__file__), 'templates')
        env = Environment(loader=FileSystemLoader(tpl))

        template = env.get_template('pg_create_table.sql')
        aggs = []

        for agg in aggregats:
            col_type = column[1]
            if agg == "count":
                col_type = "integer"
            if isinstance(agg, dict):
                agg_type = agg.keys()[0]
                if agg_type == "count":
                    col_type = "integer"
                for trigger in agg[agg_type]:
                    agg_name = trigger.keys()[0]
                    aggs.append(
                        {"name": "{}_{}".format(agg_type,
                                                agg_name),
                         "type": col_type})
            else:
                aggs.append({"name": agg,
                             "type": col_type})
        temp = template.render(
            name=name,
            column={"name": column[0], "type": column[1]},
            aggregats=aggs)
        return temp

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
        EXECUTE PROCEDURE {1}""".format(name, function, table,
                                        action.upper())

    def sql_create_function_insert(self, name, table,
                                   column, aggtable, action,
                                   where_clause=None,
                                   agg_key=None):
        """Return a SQL statement to create a FUNCTION

        name : function name
        table (string) : the originate of datas
        column : column name
        aggtable : the table where data will be stored
        """
        tpl = os.path.join(os.path.dirname(__file__), 'templates')
        env = Environment(loader=FileSystemLoader(tpl))
        template = env.get_template('pg_function_insert.sql')
        if agg_key is None:
            actions = "agg_count=agg_count+1"
        else:
            actions = "agg_count_{0}=agg_count_{0}+1".format(agg_key)
        insert_values = 1
        if where_clause:
            where_clause = parse_where_clause(where_clause, table, "NEW")
        tmp = template.render(name=name,
                              table=table,
                              aggtable=aggtable,
                              column=column,
                              actions=actions,
                              insert_values=insert_values,
                              where_clause=where_clause)
        return tmp

    def sql_create_function_delete(self, name, table,
                                   column, aggtable, action,
                                   where_clause=None,
                                   agg_key=None):
        """Return a SQL statement to create a FUNCTION

        name : functions name
        column : column name
        aggtable : the table where data will be stored
        action : action that fired the trigger
        """
        tpl = os.path.join(os.path.dirname(__file__), 'templates')
        env = Environment(loader=FileSystemLoader(tpl))
        template = env.get_template('pg_function_delete.sql')

        if agg_key is None:
            actions = "agg_count=agg_count+1"
        else:
            actions = "agg_count_{0}=agg_count_{0}-1".format(agg_key)

        if where_clause:
            where_clause = parse_where_clause(where_clause, table, "OLD")

        tmp = template.render(name=name,
                              table=aggtable,
                              column=column,
                              actions=actions,
                              where_clause=where_clause)
        return tmp

    def sql_create_function_update(self, name, table,
                                   column, aggtable, action,
                                   where_clause=None,
                                   agg_key=None):
        """Return a SQL statement to create a FUNCTION

        name : functions name
        column : column name
        aggtable : the table where data will be stored
        action : action that fired the trigger
        """
        tpl = os.path.join(os.path.dirname(__file__), 'templates')
        env = Environment(loader=FileSystemLoader(tpl))

        template = env.get_template('pg_function_update.sql')
        if agg_key is None:
            actions_new = "agg_count=agg_count+1"
            actions_old = "agg_count=agg_count-1"
        else:
            actions_new = "agg_count_{0}=agg_count_{0}+1".format(agg_key)
            actions_old = "agg_count_{0}=agg_count_{0}-1".format(agg_key)

        if where_clause:
            old_where_clause = parse_where_clause(where_clause, table, "OLD")
            where_clause = parse_where_clause(where_clause, table, "NEW")
        else:
            old_where_clause = None

        temp = template.render(name=name,
                               table=aggtable,
                               column=column,
                               actions_old=actions_old,
                               actions_new=actions_new,
                               where_clause=where_clause,
                               old_where_clause=old_where_clause)
        return temp

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

        temp = template.render(table=name,
                               aggtable=aggname,
                               column=column,
                               aggregats=aggregats)
        return temp

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
