#!/usr/bin/python2
# -*- coding: utf-8 -*-
# pylint: disable=all

#------------------------------------------------------
# Import der Libraries
#------------------------------------------------------
import clr
clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")
import sqlite3

#------------------------------------------------------
# Klasse
#------------------------------------------------------
class DBConnector( object ):
    ''' Instanziert eine Datenbank als Objekt '''
    def __init__( self, dbfile ):
        """ Instanz einer Datenbank erstellen. """
        self.ClassName = "DBConnector"
        thisActionName = "__init__"
        
        self._connection = sqlite3.connect(
            dbfile,
            check_same_thread=False,
            detect_types=sqlite3.PARSE_DECLTYPES
            | sqlite3.PARSE_COLNAMES )
        self._cursor = self._connection.cursor()

    def __del__( self ):
        """ Close the instanced database connection on destroy. """
        thisActionName = "__del__"
        self._connection.close()

    def execute( self, sql_query, query_args=None ):
        """ Execute a sql query on the instanced database. """
        thisActionName = "execute"
        
        if query_args:
            self._cursor.execute( sql_query, query_args )
        else:
            self._cursor.execute( sql_query )

        return self._cursor

    def commit( self ):
        """ Commit any changes of the instanced database. """
        thisActionName = "commit"
        
        try:
            self._connection.commit()
            return True
        except sqlite3.Error:
            return False

    def close( self ):
        """ Close the instanced database connection. """
        
        self._connection.close()
        return


