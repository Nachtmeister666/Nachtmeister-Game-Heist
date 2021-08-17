#!/usr/bin/python2
# -*- coding: utf-8 -*-
# pylint: disable=all 

#------------------------------------------------------
#   Import Libraries
#------------------------------------------------------
import os
import sys
import json
import ctypes
import winsound
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))


#------------------------------------------------------
# Import eigener Klassen und Funktionen
#------------------------------------------------------
from GameHeist_Settings import CustomSettings
from GameHeist_Logger import CustomLogger
from GameHeist_RawData import RawData
from GameHeist_GameHeist import HeistSystem
import GameHeist_ChatBotHelper as BotHelper




# ------------------------------------------------------
# Script Information
# ------------------------------------------------------
ScriptName = "Nachti's Game 'Heist'"
Website = "https://nachtmeister.net"
Description = "Ein Spiel in dem man zusammen mit anderen Chat-Teilnehmern einen Raub ausführen kann.\nDas 'Heist'-Modul des Chatbots sollte unter 'Minigames' deaktiviert werden."
Creator = "Nachtmeister666"
Version = "1.0.0"
Command = "GameHeist"


# ------------------------------------------------------
# Define Global Variables
# ------------------------------------------------------
myScriptSettings = None
mySettingsFile = None
myLogger = None
myParent = None
myRawDataHandler = None
myPath = os.path.dirname(__file__)
myLogDir = os.path.join(myPath, "../_NACHTIS_LOG_FILES_")
myLogFileName = "GameHeist"
myDatabaseDir = os.path.join(myPath, "../_NACHTIS_DATABASE_FILES_")
myChannelName = ""
myGameHeist = None

MessageBox = ctypes.windll.user32.MessageBoxW
MB_YES = 6


def Init():
    '''Initialisierung des Skriptes'''
    global myParent
    global myScriptSettings, mySettingsFile
    global myPath
    global myLogDir
    global myLogFileName
    global myDatabaseDir
    global myLogger
    global myRawDataHandler
    global myGameHeist

    # --- Notwendige Verzeichnisse erstellen falls notwendig
    if not os.path.exists(myLogDir):
        os.makedirs(myLogDir)

    if not os.path.exists(myDatabaseDir):
        os.makedirs(myDatabaseDir)

    # Übergabe von 'Parent' an globale Variable um Fehler bei importierten
    # Modulen und Klassen zu vermeiden
    myParent = Parent

    # --- EINSTELLUNGEN LADEN ---
    mySettingsFile = os.path.join(myPath, "settings.json")
    myScriptSettings = CustomSettings(mySettingsFile)

    # Log-File initialisieren
    myLogger = CustomLogger(parent=myParent, path=myLogDir,
                            filename=myLogFileName, logactive=myScriptSettings.ActivateLog)

    ###########################################################################
    #
    # Start-Eintrag des Logfiles schreiben
    #
    myLogger.WriteLog("")
    myLogger.WriteLog(
        "---------------------------------------------------------------")
    myLogger.WriteLog(
        "----            INITIALISIERUNG BOT-ERWEITERUNG            ----")
    myLogger.WriteLog(
        "---------------------------------------------------------------")
    myLogger.WriteLog("")
    myLogger.WriteLog(" Erweiterung  : {}".format(ScriptName))
    myLogger.WriteLog(" Autor        : {}".format(Creator))
    myLogger.WriteLog(" Version      : {}".format(Version))
    myLogger.WriteLog("")
    myLogger.WriteLog(
        "---------------------------------------------------------------")
    myLogger.WriteLog("")

    myLogger.WriteLog(" Initialisierung verschiedener Funktionen:")

    ###########################################################################
    #
    # --- Funktions Klassen initialisieren ---
    #

    # RawData ist eine Abhängikeit zu den anderen Funktionen
    # und muss daher zuerst aktiviert werden
    myRawDataHandler = RawData(
        scriptname=ScriptName,
        settings=myScriptSettings,
        parent=myParent,
        logger=myLogger       
    )

    myGameHeist = HeistSystem(
        parent = myParent,
        settings = myScriptSettings,
        path = myPath,
        dbpath = myDatabaseDir,
        logger = myLogger,
        rawdatahandler = myRawDataHandler
    )



    ###########################################################################
    #
    # Abschlussnachricht der Initialisierung ins Logfile schreiben
    #
    myLogger.WriteLog("")
    myLogger.WriteLog(
        " ---------------------------------------------------------------")
    myLogger.WriteLog(
        " ----             INITIALISIERUNG  ABGESCHLOSSEN            ----")
    myLogger.WriteLog(
        " ---------------------------------------------------------------")
    myLogger.WriteLog("")

    return

# ------------------------------------------------------
# Tick (zeitgesteuerte Aktionen)
# ------------------------------------------------------


def Tick():

    # Reagiere nur wenn:
    # - die Erweiterung aktiv ist
    # - der Stream Live ist (sofern eingestellt)
    # ansonsten Skript hier abbrechen
    if (not myScriptSettings.ActivateExtention) or (
            (myScriptSettings.OnlyLive) and not myParent.IsLive()):
        return
    
    # --- Timer für laufende Multi-Raffles ---
    result = myGameHeist.game_Timer()

# ------------------------------------------------------
# Reload Settings
# ------------------------------------------------------


def ReloadSettings(jsonData):
    ''' Erneutes Laden der Einstellungen '''
    global myScriptSettings, mySettingsFile
    global myLogger

    # Execute json reloading here
    myScriptSettings.__dict__ = json.loads(jsonData)
    myScriptSettings.Save(mySettingsFile)

    # Meldung ins Log schreiben
    myLogger.WriteLog("")
    myLogger.WriteLog(
        " ---------------------------------------------------------------")
    myLogger.WriteLog(
        " ----             Konfiguration neu eingelesen              ----")
    myLogger.WriteLog(
        " ---------------------------------------------------------------")
    myLogger.WriteLog("")

    return


# ------------------------------------------------------
# Funktionen fuer Settings-Schalter
# ------------------------------------------------------


def OpenLogDir():
    ''' Oeffnet das Log-Verzeichnis'''
    global myLogDir

    # Logfile-Verzeichnis öffnen
    os.startfile(myLogDir)

    return

def OpenDatabaseDir():
    ''' Oeffnet das Datenbank-Verzeichnis'''
    global myDatabaseDir

    # Logfile-Verzeichnis öffnen
    os.startfile(myDatabaseDir)

    return

def OpenREADMEtxt():
    ''' Oeffnen der README.txt im aktuellen Skriptverzeichnis '''
    global myPath

    location = os.path.join(myPath, "README.md")

    # README-Datei öffnen
    os.startfile(location)

    return

def ResetDefaultMessageData():
    ''' Lösche alle Daten in der Tabelle 'game_heist_messages'
        und schreibe die Default Daten in die Tabelle
    '''
    global myGameHeist

    # Benachrichtigung, dass alle Daten gelöscht werden
    winsound.MessageBeep()
    returnValue = MessageBox(0, u"Du willst die ursprünglichen Benachrichtigungen wiederherstellen?"
                                "\r\nAlle bisherigen Einstellungen werden dabei gelöscht!"
                             , u"Bist du sicher?", 4)

    if returnValue == MB_YES:

        # Funktion zum Zurücksetzen aufrufen
        myGameHeist.DB_create_DefaultMessages()

        # Nachrichtenbox
        MessageBox(0, u"Die Benachrichtigungen wurden auf die Grundeinstellungen zurückgesetzt!"
                      "\r\nLade das Skript neu und aktualisiere die Einstellungen."
                   , u"Reset wurde abgeschlossen!", 0)

        # Information ins Log schreiben
        myLogger.WriteLog("")
        myLogger.WriteLog(
            " ---------------------------------------------------------------")
        myLogger.WriteLog(
            " ----        BENACHRICHTIGSTEXTE WURDEN ZURÜCKGESETZT       ----")
        myLogger.WriteLog(
            " ---------------------------------------------------------------")
        myLogger.WriteLog("")

    return

def ResetDefaultTargetNames():
    ''' Lösche alle Daten in der Tabelle 'game_heist_targets'
        und schreibe die Default Daten in die Tabelle
    '''
    global myGameHeist
    global myLogger

    # Benachrichtigung, dass alle Daten gelöscht werden
    winsound.MessageBeep()
    returnValue = MessageBox(0, u"Du willst die ursprünglichen Namen der Ziele wiederherstellen?"
                                "\r\nAlle bisherigen Einstellungen werden dabei gelöscht!"
                             , u"Bist du sicher?", 4)

    if returnValue == MB_YES:

        # Funktion zum Zurücksetzen aufrufen
        myGameHeist.DB_create_DefaultTargets()

        # Nachrichtenbox
        MessageBox(0, u"Die Namen der Ziele wurden auf die Grundeinstellungen zurückgesetzt!"
                      "\r\nLade das Skript neu und aktualisiere die Einstellungen."
                   , u"Reset wurde abgeschlossen!", 0)

        # Information ins Log schreiben
        myLogger.WriteLog("")
        myLogger.WriteLog(
            " ---------------------------------------------------------------")
        myLogger.WriteLog(
            " ----           TARGET DATEN WURDEN ZURÜCKGESETZT           ----")
        myLogger.WriteLog(
            " ---------------------------------------------------------------")
        myLogger.WriteLog("")

    return

# ------------------------------------------------------
# Unload
# ------------------------------------------------------


def Unload():
    global myGameHeist
    global myLogger

    myLogger.WriteLog("")
    myLogger.WriteLog(
        " ---------------------------------------------------------------")
    myLogger.WriteLog(
        " ----         KONTROLLIERTES ENTLADEN DES SKRIPTES          ----")
    myLogger.WriteLog(
        " ---------------------------------------------------------------")
    myLogger.WriteLog("")

    myLogger.WriteLog(" Trenne Datenbank Verbindung:")

    # Datenbankverbindung schliessen
    myGameHeist.DB_close()

    myLogger.WriteLog("")
    myLogger.WriteLog(
        " ---------------------------------------------------------------")
    myLogger.WriteLog(
        " ----                         ENDE                          ----")
    myLogger.WriteLog(
        " ---------------------------------------------------------------")
    myLogger.WriteLog("")

    return

# ------------------------------------------------------
# ScriptToggled
# ------------------------------------------------------


def ScriptToggled(state):
    pass

# ------------------------------------------------------
# Execute Data / Process messages
# ------------------------------------------------------


def Execute(data):
    '''Ausführung der Aktionen'''
    global myParent
    global myScriptSettings
    global myLogger
    global myRawDataHandler


    # Reagiere nur wenn:
    # - die Erweiterung aktiv ist
    # - der Stream Live ist (sofern eingestellt)
    # ansonsten Skript hier abbrechen
    if (not myScriptSettings.ActivateExtention) or (
            (myScriptSettings.OnlyLive) and not myParent.IsLive()):
        return

    ###############################################################################
    # alle Daten vom Twitch-Chat (keine Whisper)
    ###############################################################################
    if (data.IsFromTwitch() and (data.IsChatMessage() and not data.IsWhisper())):

        if (data.GetParam(0).lower() == str(myScriptSettings.Game_Command).lower()): # and myParent.HasPermission(data.User, myScriptSettings.Game_Command_Permission, ""):
            
            myGameHeist.game_StartHeist(data)
    

