#!/usr/bin/python2
# -*- coding: utf-8 -*-
# pylint: disable=all

#------------------------------------------------------
# Import der Libraries
#------------------------------------------------------
import os
import sys
import codecs
from time import localtime, strftime

# Weitere Resourcen importieren
import GameHeist_Time as myTime
from GameHeist_ChatBotHelper import ReadDatafromFile, WriteDataToFile, AppendDataToFile

#------------------------------------------------------
# Klasse
#------------------------------------------------------
class CustomLogger(object):
    ''' Meine Log-Funktion '''
    def __init__( self, parent, path, filename, logactive = True ):
        thisActionName = "__init__"
        
        self.ClassName = "CustomLogger"
        self.Version = "1.0.1"
        
        self.Parent = parent
        self.Path = path
        self.LogIsActive = logactive
        self.LogFileName = str( myTime.FileTimeStamp() ) + "_" + filename + ".txt"
        self.LogFilePath = path

        # Logging nur, wenn auch aktiviert
        if self.LogIsActive:
            
            # Log-Verzeichnis erzeugen, falls nicht vorhanden
            if not os.path.exists( self.LogFilePath ):
                os.makedirs( self.LogFilePath )

            self.LogFile = os.path.join( self.LogFilePath, self.LogFileName )
     
        return
           
    def WriteDebug( self, Command, message_text ):
        """
            Eintrag in Bot-Log schreiben
        """
        thisActionName = "WriteDebug"
        self.Parent.Log( Command, '[' + myTime.TimeStampLog() + '] : ' + str( message_text ) )
        return
    
    def WriteLog( self, message_text ):
        """
            Eintrag in Logfile schreiben
        """
        thisActionName = "WriteLog"

        # Logging nur, wenn auch aktiviert
        if self.LogIsActive:
        
            Text = str( '[' + myTime.TimeStampLog() + '] : ' + str( message_text ) )
            Result = AppendDataToFile( self.LogFile, Text )

            if not Result:
                self.Parent.Log( self.ClassName, '[' + myTime.TimeStampLog() + '] : ' + ' --- [FEHLER START] ---' )
                self.Parent.Log( self.ClassName, '[' + myTime.TimeStampLog() + '] : ' + ' --- Kann nicht ins File \'' + self.LogFile + '\' schreiben.' )
                self.Parent.Log( self.ClassName, '[' + myTime.TimeStampLog() + '] : ' + ' --- [FEHLER ENDE] ---' )
            
        return

        