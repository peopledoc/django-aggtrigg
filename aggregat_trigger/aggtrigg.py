
import pgcommands
from django.conf import settings
import sys
import databases

ACTIONS = ['insert', 'update', 'delete']

class AggTrigger(object):


    database = 'default'

    def __init__(self, table, column, aggregats, database='default'):
        self.verbose = 0
        self.table = table
        self.column = column
        self.aggregats = aggregats
        self.database = database

        # use the right backend
        if database in settings.DATABASES:
            if settings.DATABASES[database]['ENGINE'] == PGBACKEND:
                from databases.pg import TriggerPostgreSQL
                self.backend = TriggerPostgreSQL()
            else:
                raise DatabaseNotSupported()
        else:
            raise DatabaseUnknown()

    @property
    def table_name(self):
        return table_name(self.table, self.column)

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

    def drop_objects(self):
        """Drop all relations from database
        table (string)
        column (string)
        """
        res = self.drop_triggers(self.table)

        res = res + self.drop_functions(self.table, self.column)

        res = res + self.drop_table(self.table_name)

        return res

    def create_table(self):
        """
        table (string)
        column (string)
        aggregats (array)
        """
        sql = self.sql_create_table()
        return pgcommands.execute_raw(sql, self.database)

    def create_triggers(self):
        res = 0
        for sql in self.sql_create_triggers():
            if res == 0:
                if self.verbose > 2:
                    sys.stdout.write(pgcommands.mogrify(sql, database=self.database))
                res = pgcommands.execute_raw(sql, self.database)
        return res

    def create_functions(self):
        res = 0
        for sql in self.sql_create_functions():
            if res == 0:
                res = pgcommands.execute_raw(sql, self.database)
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
        """
        qry = self.backend.sql_get_column_typname()
        params = (self.table, self.column)
        res = pgcommands.lookup(qry,
                                params=params,
                                database=self.database)
        return res

    def sql_init(self):
        """
        Remplissage de la table technique avec les données existantes
        """
        sql = self.backend.sql_init_aggtable(self.table,
                                             self.column,
                                             self.table_name,
                                             self.aggregats)
        return sql

    def initialize(self):
        """Initialize the agregate table with values from source table
        May be long on huge tables
        """
        sql = self.sql_init()
        res = pgcommands.execute_raw(sql, database=self.database)
        return res

    def get_nb_tuples(self):
        """
        Remplissage de la table technique avec les données existantes
        """
        sql = self.backend.sql_nb_tuples()
        params = (self.table,)
        if self.verbose > 2:
            msg = "[SQL] %s\n" % (pgcommands.mogrify(sql,
                                                     params=params,
                                                     database=self.database)))
            sys.stdout.write(msg)
        res = pgcommands.lookup(sql, params=params, database=self.database)
        return res

    def sql_create_triggers(self):
        """Declaration des triggers
        """
        sql = []
        for action in ACTIONS:
            function = function_name(self.table, self.column, action)
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
        tgname = trigger_name(table, self.column, action)
        return self.backend.sql_create_trigger(tgname,
                                               function,
                                               table,
                                               action)

    def drop_table(self, name):
        sql = self.sql_drop_table(name)
        return pgcommands.execute_raw(sql)

    def drop_functions(self, name, column):
        """DROP all related functions
        """
        res = 0
        for sql in self.sql_drop_functions(name, column):
            res = res + pgcommands.execute_raw(sql)
        return res

    def sql_drop_functions(self, table, column):
        """
        Functions appellées par les triggers
        """
        sql = []
        for action in ACTIONS:
            fname = function_name(table, column, action)
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
            sql.append(self.sql_create_function(self.table,
                                                self.column,
                                                self.aggregats,
                                                action))
        return sql

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
        if action == 'insert':
            sql = self.backend.sql_create_function_insert(fname, table, column, tname)
        elif action == 'update':
            sql = self.backend.sql_create_function_update(fname, column, tname, action)
        elif action == 'delete':
            sql = self.backend.sql_create_function_delete(fname, column, tname, action)
        else:
            raise ActionUnknown(Exception)
        
        return sql

    def drop_triggers(self, name):
        """DROP related triggers
        """
        res = 0
        for sql in self.sql_drop_triggers(name):
            res = res + pgcommands.execute_raw(sql, self.database)
        return res

    def sql_drop_triggers(self, table):
        """DROP triggers

        table (string) : the table name
        """
        sql = []
        for action in ACTIONS:
            tgname = trigger_name(table, self.column, action)
            sql.append(self.sql_drop_trigger(tgname, table))
        return sql

    def sql_drop_function(self, name):
        """Return SQL statement build by the backend
        """
        return self.backend.sql_drop_function(name)

    def sql_drop_trigger(self, name, table):
        """Return SQL statement build by the backend
        """
        return self.backend.sql_drop_trigger(name, table)

    def sql_drop_table(self, name):
        """Return SQL statement build by the backend
        """
        return self.backend.sql_drop_table(name)
