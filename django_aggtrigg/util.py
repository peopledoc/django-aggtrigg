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
# * Neither the name of django-aggtrigg nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
#
import six
from django.db.models import Q
from django.db import connections
import dbcommands
import sys


ACTIONS = ['insert', 'update', 'delete']

SQLITE_BACKEND = 'django.db.backends.sqlite3'
PG_BACKEND = 'django.db.backends.postgresql_psycopg2'


class DatabaseNotSupported(Exception):
    pass


class DatabaseUnknown(Exception):
    pass


class ActionUnknown(Exception):
    pass


def function_name(table, column, action, key=None):
    if key:
        action = "_".join([action, key])
    fname = "{0}_{1}_{2}()".format(table, column, action)
    return fname


def trigger_name(table, column, function, action):

    function = function.split("_")[-2][:-2]

    tname = "{0}_{1}_{2}_{3}_trigger".format(table, column, function, action)
    return tname


def triggers_name(table, column, functions):
    tgs = []

    for function, action in functions.iteritems():
        function = function.split("_")[-1][:-2]
        tgs.append("{0}_{1}_{2}_{3}_trigger".format(table, column,
                                                    function, action))
    return tgs


def parse_where_clause(where_clause, table, new_old=None):
    params = ["'{}'".format(param) if type(
        param) == six.string_types else param for
        param in where_clause[1]]

    return where_clause[0].replace(
        '"', "").replace(
            '%s', '{}').replace(
                table, new_old).format(*params)


def table_name(table, column):
    """Compute the table name

    table (string) : the originate table's name
    column : the column name

    return : string
    """
    return "{0}__{1}_agg".format(table, column)


class AggTrigger(object):
    """Manage database triggers
    """

    def __init__(self, engine, table, column,
                 aggregats=['count'],
                 database='default',
                 model=None):
        self.verbose = 0
        self.table = table
        self.column = column
        self.aggregats = aggregats
        self.database = database
        self.model = model
        self.functions = {}
        # use the right backend
        if engine == PG_BACKEND:
            from databases.pg import TriggerPostgreSQL
            self.backend = TriggerPostgreSQL()
        else:
            raise DatabaseNotSupported()

        for agg in self.aggregats:
            if isinstance(agg, dict):
                for agg_key, where_clause in self.extract_agg_where_clause(
                        agg).iteritems():
                    for action in ["insert", "update", "delete"]:
                        fname = function_name(table, column,
                                              action, key=agg_key)
                        self.functions[fname] = action
            else:
                for action in ["insert", "update", "delete"]:
                    fname = function_name(table, column, action)
                    self.functions[fname] = action

    @property
    def table_name(self):
        return table_name(self.table, self.column)

    @property
    def triggers_name(self):
        return triggers_name(self.table, self.column, self.functions)

    @property
    def functions_name(self):
        fns = []
        for action in ACTIONS:
            fns.append(function_name(self.table, self.column, action))
        return fns

    def create_objects(self):
        """Create all needed objects
        table (string)
        column (string)
        aggregats (array)
        """
        res = self.create_table()
        res = res + self.create_functions()
        res = res + self.create_triggers()
        return res

    def create_table(self):
        """
        table (string)
        column (string)
        aggregats (array)

        Return :
        - 0 is case of creation + success
        - 1 if table already exists
        """
        if not self.agg_table_ispresent():
            sql = self.sql_create_table()
            return dbcommands.execute_raw(sql, self.database)
        else:
            return 1

    def create_triggers(self):
        """Create all triggers
        """
        res = 0
        for (trigger_name, sql) in self.sql_create_triggers():

            if res == 0:
                if not self.trigger_on_table_is_present(trigger_name):
                    res = self.create_trigger(sql)
        return res

    def create_trigger(self, sql):
        """Create a trigger
        """
        if self.verbose > 2:
            stm = dbcommands.mogrify(sql, database=self.database)
            sys.stdout.write(stm)
        res = dbcommands.execute_raw(sql, self.database)
        return res

    def create_functions(self):
        """Create all functions in the database
        """
        res = 0
        for sql in self.sql_create_functions():
            if res == 0:
                res = dbcommands.execute_raw(sql, self.database)
        return res

    def sql_create_table(self):
        """
        """
        typname = self.column_typname()

        return self.backend.sql_create_table(self.table_name,
                                             (self.column, typname),
                                             self.aggregats)

    def column_typname(self):
        """Lookup for a column type

        Depending on backend.sql_get_column_typname()[1] we need to
        parse the result or not
        """
        (qry, parsefunc) = self.backend.sql_get_column_typname()
        params = (self.table, self.column)
        res = dbcommands.lookup(qry,
                                params=params,
                                database=self.database)
        if parsefunc is None:
            return res
        else:
            return eval("self.backend.%s('%s', '%s')" % (parsefunc,
                                                         res,
                                                         self.column))

    def sql_init(self):
        """
        Remplissage de la table technique avec les données existantes
        """
        aggs = {}
        for agg in self.aggregats:
            if isinstance(agg, dict):
                agg_type = agg.keys()[0]
                for trigger in agg[agg_type]:
                    agg_name = trigger.keys()[0]
                    aggs[agg_name] = {"column": "agg_{}_{}".format(agg_type,
                                                                   agg_name)}

                for agg_key, where_clause in self.extract_agg_where_clause(
                        agg).iteritems():
                    aggs[agg_key]["where"] = where_clause[0] % tuple(
                        where_clause[1])

            else:
                agg_type = agg
                agg_name = "agg_{}".format(agg_type)
                aggs[agg_name] = {"column": agg_name, "where": None}

        sql = self.backend.sql_init_aggtable(self.table,
                                             self.column,
                                             self.table_name,
                                             aggs)
        return sql

    def initialize(self):
        """Initialize the agregate table with values from source table
        May be long on huge tables
        """
        sql = self.sql_init()
        res = dbcommands.execute_raw(sql, database=self.database)
        return res

    def get_nb_tuples(self):
        """
        Remplissage de la table technique avec les données existantes
        """
        sql = self.backend.sql_nb_tuples()
        params = (self.table,)
        if self.verbose > 2:
            msg = "[SQL] %s\n" % (dbcommands.mogrify(sql,
                                                     params=params,
                                                     database=self.database))
            sys.stdout.write(msg)
        res = dbcommands.lookup(sql, params=params, database=self.database)
        return res

    def sql_create_triggers(self):
        """Declaration des triggers

        Return : Array of tuples (triggername, SQL_COMMAND)
        """
        sql = []
        for function, action in self.functions.iteritems():
            sql.append(self.sql_create_trigger(self.table,
                                               action,
                                               function))
        return sql

    def sql_create_trigger(self, table, action, function):
        """
        table (string): table name
        action (string): insert, update or create
        function (string): function's name called by the trigger
        """
        tgname = trigger_name(table, self.column, function, action)
        return (tgname, self.backend.sql_create_trigger(tgname,
                                                        function,
                                                        table,
                                                        action))

    def drop_table(self):
        sql = self.sql_drop_table()
        return dbcommands.execute_raw(sql)

    def drop_functions(self):
        """DROP all related functions
        """
        res = 0
        for sql in self.sql_drop_functions():
            res = res + dbcommands.execute_raw(sql)
        return res

    def sql_drop_functions(self):
        """Return SQL Statements to DROP all functions
        """
        sql = []
        for fname in self.functions.iterkeys():
            sql.append(self.sql_drop_function(fname))
        return sql

    def sql_create_functions(self):
        """Create all functions

        table (string)
        column (string)
        aggregats (array)
        """
        sql = []
        for action in ACTIONS:
            funcs = self.sql_create_function(self.table,
                                             self.column,
                                             self.aggregats,
                                             action)
            for func in funcs:
                sql.append(func)
        return sql

    def extract_agg_where_clause(self, agg):
        """
        For aggregations relying on the ORM extract the where clause from
        Django
        """
        connection = connections["default"]
        result = {}
        for aggregation_type in agg.iterkeys():
            # foreach aggregation type we can have multiple
            # aggregation with different filters
            for aggregation in agg[aggregation_type]:
                # at this level we can create the queryset and
                # extract the where clause
                for agg_key in aggregation:
                    # First we create a queryset with Q objects
                    query = Q()
                    for filter in aggregation[agg_key]:
                        query &= Q(
                            **{filter["field"]: filter["value"]})
                    compiler = self.model.objects.filter(
                        query).query.get_compiler(
                            connection=connection)
                    qn = compiler.quote_name_unless_alias
                    where_clause = self.model.objects.filter(
                        query).query.where.as_sql(
                            qn,
                            connection
                    )
                    result[agg_key] = where_clause
        return result

    def sql_create_function(self, table, column, aggregats, action):
        """
        table (string)
        column (string)
        aggregats (array)
        action (string)
        """
        fname = function_name(table, column, action)
        tname = table_name(table, column)
        sql = None
        if action not in ["insert", "update", "delete"]:
            raise ActionUnknown(Exception)
        meth = "sql_create_function_{}".format(action)
        sql = []
        for agg in aggregats:
            if isinstance(agg, dict):
                for agg_key, where_clause in self.extract_agg_where_clause(
                        agg).iteritems():
                    fname = function_name(table, column,
                                          action, key=agg_key)
                    sql.append(getattr(self.backend, meth)(
                        fname, table,
                        column, tname, action,
                        where_clause=where_clause,
                        agg_key=agg_key))
            else:
                fname = function_name(table, column,
                                      action)
                resp = getattr(self.backend, meth)(
                    fname, table,
                    column, tname, action)
                sql.append(resp)
        return sql

    def drop_triggers(self, name):
        """DROP related triggers
        """
        res = 0
        for sql in self.sql_drop_triggers(name):
            res = res + dbcommands.execute_raw(sql, self.database)
        return res

    def sql_drop_triggers(self):
        """Return SQL Statements to DROP ALL triggers
        """
        sql = []
        for function, action in self.functions.iteritems():
            tgname = trigger_name(self.table, self.column, function, action)
            sql.append(self.sql_drop_trigger(tgname, self.table))
        return sql

    def sql_drop_function(self, fname):
        """Return SQL statement from backend to DROP a function
        """
        return self.backend.sql_drop_function(fname)

    def sql_drop_trigger(self, name, table):
        """Return SQL statement from backend to DROP a trigger
        """
        return self.backend.sql_drop_trigger(name, table)

    def sql_drop_table(self):
        """Return SQL statement from backend to DROP a table
        """
        return self.backend.sql_drop_table(self.table_name)

    def agg_function(self, fname, agg):
        """Return the aggregate name

        fname (string) : min or max
        """
        return self.backend.agg_fname(agg, fname)

    def agg_table_ispresent(self):
        """Check if the agg table is present
        """
        qry = self.backend.sql_table_exists()
        params = (self.table_name,)
        res = dbcommands.lookup(qry,
                                params=params,
                                database=self.database)
        return res

    def triggers_on_table_are_present(self):
        """Check if the triggers are present in database
        """
        res = []
        qry = self.backend.sql_trigger_on_table_exists()

        for trig in self.triggers_name:
            params = (trig, self.table)
            res.append((trig, dbcommands.lookup(qry,
                                                params=params,
                                                database=self.database)))
        return res

    def trigger_on_table_is_present(self, trgname):
        """Check if a trigger is present on a table

        Return False is the trigger does not exists

        trganme : (string) trigger name
        """

        qry = self.backend.sql_trigger_on_table_exists()
        params = (trgname, self.table)
        res = dbcommands.lookup(qry, params=params, database=self.database)
        return res

    def functions_are_present(self):
        """Check if the functions are present in database
        """
        res = []
        qry = self.backend.sql_trigger_function_on_table_exists()
        functions = []
        for agg in self.aggregats:
            if isinstance(agg, dict):
                for agg_key, where_clause in self.extract_agg_where_clause(
                        agg).iteritems():
                    for action in ["insert", "update", "delete"]:
                        fname = function_name(self.table, self.column,
                                              action, key=agg_key)
                        functions.append(fname)
            else:
                for fname in self.functions_name:
                    functions.append(fname)

        for func in functions:
            params = (func[:-2], self.table)
            res.append((func, dbcommands.lookup(qry,
                                                params=params,
                                                database=self.database)))
        return res
