#!/usr/bin/python2
# -*- coding: utf-8 -*-
# pylint: disable=all

# ------------------------------------------------------
# Import der Libraries
# ------------------------------------------------------

import os
import sys
import datetime
import math
import time
import random

# ------------------------------------------------------
# Import eigener Klassen und Funktionen
# ------------------------------------------------------
import GameHeist_Time as myTime
import GameHeist_ChatBotHelper as BotHelper
from GameHeist_ChatBotHelper import TransformLocale_Decimals
from GameHeist_DBConnector import DBConnector


# ------------------------------------------------------
# Klasse
# ------------------------------------------------------
class HeistSystem(object):
    ''' Klasse für das Spiel "Heist" '''

    #####################################################################################

    def __init__(self, parent, settings, path, dbpath, logger, rawdatahandler):
        ''' Initialisierung der Klasse '''
        thisActionName = "__init__"

        # Klassen Variablen
        self.ClassName = "Spiel 'Heist'"
        self.Version = "1.0.0"
        self.ScriptName = str(self.ClassName)
        self.Parent = parent
        self.Settings = settings
        self.Path = path
        self.dbPath = dbpath
        self.Logger = logger
        self.RawDataHandler = rawdatahandler

        # Daten des Spiel zwischenspeichern
        self.GameStartTimestamp = ""
        self.LastGameFinishTimestamp = ""
        self.GameID = 0
        self.GameTargetName = ""

        # Nachrichten Typen
        self.MessageType_IsOnCooldown = "IsOnCoolDown"
        self.MessageType_NewGameStart = "NewGameStart"
        self.MessageType_GameStartIntro = "GameStartIntro"
        self.MessageType_GameCooldownOver = "GameCooldownOver"
        self.MessageType_NewPlayer = "NewPlayer"
        self.MessageType_NotEnoughPlayer = "NotEnoughPlayer"
        self.MessageType_NotEnoughPoints = "NotEnoughPoints"
        self.MessageType_StakeBelowMinimum = "StakeBelowMinimum"
        self.MessageType_StakeOverMaximum = "StakeOverMaximum"
        self.MessageType_WrongCommandOption = "WrongCommandOption"

        self.MessageType_Outcome_100Percent = "Outcome_100Percent"
        self.MessageType_Outcome_75_99Percent = "Outcome_75_99Percent"
        self.MessageType_Outcome_25_74Percent = "Outcome_25_74Percent"
        self.MessageType_Outcome_01_24Percent = "Outcome_01_24Percent"
        self.MessageType_Outcome_00Percent = "Outcome_00Percent"

        # Verbindung zur MultiRaffle-Datenbank aufbauen
        self.GameDBFile = os.path.join(self.dbPath, "Games.db")
        self.GameDB = DBConnector(str(self.GameDBFile))

        # Cooldown-Helper initialisieren
        self.CD = BotHelper.CoolDownHelper(
            parent=self.Parent,
            logger=self.Logger
        )

        # Tabellen erzeugen
        self.DB_create_Tables()

        # Wenn ".init"-Datei nicht vorhanden,
        if not (os.path.isfile(os.path.join(self.Path, ".init"))):

            # Default Nachrichten erzeugen
            self.DB_create_DefaultMessages()
            self.DB_create_DefaultTargets()

            # ".init"-Datei erzeugen
            init = open(os.path.join(self.Path, ".init"), 'w+')
            init.close()

        # Meldung bezueglich der Initialisierung der Klasse ins Log schreiben
        self.Logger.WriteLog(str(" - '{0}'").format(self.ScriptName))

        return

    #####################################################################################

    def DB_close(self):
        ''' Verbindung zur Datenbank schliessen '''
        thisActionName = "DB_close"

        self.Logger.WriteLog(" - Datenbank 'Games.db'")
        self.GameDB.close()

        return

    def DB_create_Tables(self):
        ''' Erzeuge Tabelle für statistische Zwecke '''
        thisActionName = "DB_create_Tables"

        # ---  Tabellen - falls notwendig - erzeugen

        # Tabelle 'game_heist_gamedata' vorbereiten
        sql_game_heist_gamedata = "CREATE TABLE IF NOT EXISTS game_heist_gamedata("
        sql_game_heist_gamedata += "autoID INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,"
        sql_game_heist_gamedata += "gameID INTEGER NOT NULL,"
        sql_game_heist_gamedata += "gameStartTimestamp DATETIME DEFAULT '',"
        sql_game_heist_gamedata += "userName TEXT NOT NULL DEFAULT '',"
        sql_game_heist_gamedata += "userStake INTEGER DEFAULT 0,"
        sql_game_heist_gamedata += "lastChange DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP)"

        # Tabelle 'game_heist_messages' vorbereiten
        sql_game_heist_messages = "CREATE TABLE IF NOT EXISTS game_heist_messages("
        sql_game_heist_messages += "autoID INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,"
        sql_game_heist_messages += "messageType TEXT NOT NULL DEFAULT '',"
        sql_game_heist_messages += "messageText TEXT NOT NULL DEFAULT '' UNIQUE)"

        # Tabelle 'game_heist_targets' vorbereiten
        sql_game_heist_targets = "CREATE TABLE IF NOT EXISTS game_heist_targets("
        sql_game_heist_targets += "autoID INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,"
        sql_game_heist_targets += "targetName TEXT NOT NULL DEFAULT '' UNIQUE)"

        # SQL ausführen
        self.GameDB.execute(sql_game_heist_gamedata)
        self.GameDB.execute(sql_game_heist_messages)
        self.GameDB.execute(sql_game_heist_targets)
        self.GameDB.commit()

        return

    def DB_create_DefaultMessages(self):
        ''' Erzeuge verschiedene Benachrichtigungs-Einträge in der Datenbank '''
        thisActionName = "DB_create_DefaultMessages"

        # Nachrichten Listen
        message_CoolDown = []
        message_GameCooldownOver = []
        message_NewGameStart = []
        message_NewPlayerEntry = []
        message_NotEnoughPoints = []
        message_NotEnoughPlayer = []
        message_StakeOverMaximum = []
        message_WrongCommandOption = []
        message_StakeBelowMinimum = []

        message_Outcome_100Percent = []
        message_Outcome_75_99Percent = []
        message_Outcome_25_74Percent = []
        message_Outcome_01_24Percent = []
        message_Outcome_00Percent = []

        message_GameStartIntro = []

        #
        #
        ###    Default Texte vorbereiten    ###
        #
        #
        # Sollte mehr als eine Nachricht mit dem selben Nachrichten-Typ (messageType) vorhanden
        # sein, so wird eine der Nachrichten per Zufall ausgewählt.
        #
        #

        ###    Benachrichtigung - Kommando ist im Cooldown    ###
        #
        # mögliche Variablen:
        #
        #   {time}          = Cooldown Zeit
        #   {command}       = Kommando des Spiels
        #

        # Erster Text
        coolDown_text = "Die Sicherheitskräfte sind aktuell alamiert und patrouillieren noch in der Gegend. "
        coolDown_text += "Du musst noch {time} warten bis zum nächsten Überfall."

        # Text der Liste hinzufügen
        message_CoolDown.append(coolDown_text)

        # Zweiter Text
        coolDown_text = "Das Kommando '{command}' befindet sich derzeit im Cooldown. "
        coolDown_text += "Du musst noch {time} warten bis zur nächsten Ausführung des Kommandos."

        # Text der Liste hinzufügen
        message_CoolDown.append(coolDown_text)

        ###    Benachrichtigung - Cooldown ist abgelaufen   ###
        #
        # mögliche Variablen:
        #
        #   {command}       = Kommando des Spiels
        #

        # Erster Text
        gameCooldownOver_text = "Die Sicherheitskräfte der Megaplexe haben ihre Patrouille beendet "
        gameCooldownOver_text += "und kehren in ihre Kasernen zurück. "
        gameCooldownOver_text += "Verwende '{command} <EINSATZ>' um ein Team für einen neuen Überfall "
        gameCooldownOver_text += "zusammenzustellen. "

        # Text der Liste hinzufügen
        message_GameCooldownOver.append(gameCooldownOver_text)

        ###    Benachrichtigung - Spiel wurde gestartet    ###
        #
        # mögliche Variablen:
        #
        #   {user}          = Name des Spielers, der den Heist starten will
        #   {command}       = Kommando des Spiels
        #   {target}        = Name des Ziels
        #   {time}          = Zeit bis das Spiel startet
        #   {maxpoints}     = Höhe des maximalen Einsatzes
        #   {pointsname}    = Name der Chatbot-Punkte
        #

        # Erster Text
        newGameStart_Text = "🗨️ {user} stellt ein Team zusammen um geheime Daten von {target} zu stehlen. "
        newGameStart_Text += "Schreibe '{command} <EINSATZ>' in den Chat um an dem Überfall teilzunehmen. "
        newGameStart_Text += "Du hast {time} Zeit. "

        # Text der Liste hinzufügen
        message_NewGameStart.append(newGameStart_Text)

        # Zweiter Text
        newGameStart_Text = "🗨️ {user} plant einen Überfall, um Daten von {target} zu stehlen. "
        newGameStart_Text += "Werde ein Teil des Teams und schreibe '{command} <EINSATZ>' in den Chat um an dem Run teilzunehmen. "
        newGameStart_Text += "Du hast {time} Zeit. "

        # Text der Liste hinzufügen
        message_NewGameStart.append(newGameStart_Text)

        ###    Benachrichtigung - Introtext für den Spielstart    ###
        #
        # mögliche Variablen:
        #
        #   {target}        = Name des Ziels
        #
        #

        # Erster Text
        gameStartIntro_Text = "👥 Es geht los! Schnappt euch eure Ausrüstung und überprüft nochmals eure Waffen. "
        gameStartIntro_Text += "Seit Vorsichtig, die Sicherheitskräfte von {target} schiessen erst und stellen später fragen... "

        # Text zur Liste hinzufügen
        message_GameStartIntro.append(gameStartIntro_Text)

        # Zweiter Text
        gameStartIntro_Text = "👥 Wir starten jetzt unseren Angriff auf den Megaplex von {target}. "
        gameStartIntro_Text += "Prüft eure Decks und ladet eure Waffen. "

        # Text zur Liste hinzufügen
        message_GameStartIntro.append(gameStartIntro_Text)

        ###    Benachrichtigung - Neuer Spieler    ###
        #
        # mögliche Variablen:
        #
        #   {user}          = Name des Spielers, der den Heist starten will
        #   {target}        = Name des Ziels
        #   {stake}         = Einsatz des Spielers
        #   {pointsname}    = Name der Chatbot-Punkte
        #

        # Erster Text
        newPlayerEntry_Text = "✅ {user} nimmt mit einem Einsatz von {stake} {pointsname} am Überfall auf {target} teil. "

        message_NewPlayerEntry.append(newPlayerEntry_Text)

        ###    Benachrichtigung - Spieler hat nicht genug Punkte    ###
        #
        # mögliche Variablen:
        #
        #   {user}          = Name des Spielers
        #   {target}        = Name des Ziels
        #   {points}        = Punkte des Spielers
        #   {pointsname}    = Name der Chatbot-Punkte
        #

        # Erster Text
        notEnoughPoints_Text = "🛑 @{user}, du verfügst nur über {points} {pointsname} und kannst daher nicht "
        notEnoughPoints_Text += "mit einem so hohen Einsatz am Überfall auf {target} teilnehmen. "
        notEnoughPoints_Text += "Versuche es erneut mit einem reduzierten Einsatz."

        # Text zur Liste hinzufügen
        message_NotEnoughPoints.append(notEnoughPoints_Text)

        # Zweiter Text
        notEnoughPoints_Text = "🛑 @{user}, du verfügst nur über {points} {pointsname} und kannst daher nicht "
        notEnoughPoints_Text += "mit einem so hohen Einsatz am Überfall teilnehmen. "
        notEnoughPoints_Text += "Versuche es erneut mit einem reduzierten Einsatz."

        # Text zur Liste hinzufügen
        message_NotEnoughPoints.append(notEnoughPoints_Text)

        ###    Benachrichtigung - ungenügende Anzahl Spieler    ###
        #
        # mögliche Variablen:
        #
        #   {target}        = Name des Ziels
        #   {pointsname}    = Name der Chatbot-Punkte
        #

        notEnoughPlayer_Text = "Leider sind nicht genügend Runner zusammen gekommen, um den "
        notEnoughPlayer_Text += "Run auf {target} erfolgreich durchführen zu können. "
        notEnoughPlayer_Text += "Die eingesetzten {pointsname} wurden erstattet. "

        # Text zur Liste hinzufügen
        message_NotEnoughPlayer.append(notEnoughPlayer_Text)

        ###    Benachrichtigung - Einsatz kleiner eingestelltes Minimum    ###
        #
        # mögliche Variablen:
        #
        #   {user}          = Name des Spielers
        #   {minpoints}     = minimaler Einsatze
        #   {pointsname}    = Name der Chatbot-Punkte

        # Erster Text
        stakeBelowMinimum_Text = "🛑 @{user}, dein Einsatz liegt unterhalb der Grenze "
        stakeBelowMinimum_Text += "von {minpoints} {pointsname}. "
        stakeBelowMinimum_Text += "Versuche es erneut mit einem höheren Einsatz."

        # Text zur Liste hinzufügen
        message_StakeBelowMinimum.append(stakeBelowMinimum_Text)

        ###    Benachrichtigung - Spieler will mehr Punkte einsetzen, als das erlaubte Maximum    ###
        #
        # mögliche Variablen:
        #
        #   {user}          = Name des Spielers
        #   {target}        = Name des Ziels
        #   {command}       = Kommando zum Aufruf des Spieles
        #   {maxpoints}     = Höhe des maximalen Einsatzes
        #   {pointsname}    = Name der Chatbot-Punkte
        #
        #

        # Erster Text
        stakeOverMaximum_Text = "🛑 @{user}, dein Einsatz überschreitet den maximal möglichen Betrag "
        stakeOverMaximum_Text += "in Höhe von {maxpoints} {pointsname}. "
        stakeOverMaximum_Text += "Reduziere den Betrag und versuche es erneut. "

        # Text zur Liste hinzufügen
        message_StakeOverMaximum.append(stakeOverMaximum_Text)

        ###    Benachrichtigung - Falscher Kommandoaufruf    ###
        #
        # mögliche Variablen:
        #
        #   {user}          = Name des Spielers
        #   {command}       = Kommando zum Aufruf des Spieles
        #   {maxpoints}     = Höhe des maximalen Einsatzes
        #   {pointsname}    = Name der Chatbot-Punkte
        #
        #

        # Erster Text
        wrongCommandOption_Text = "⛔ @{user}, das Kommando '{command}' wurde fehlerhaft verwendet. "
        wrongCommandOption_Text += "Benutze folgendes Format: '{command} <Zahl>'. "
        wrongCommandOption_Text += "Der maximale Einsatz beträgt {maxpoints} {pointsname}."

        # Text zur Liste hinzufügen
        message_WrongCommandOption.append(wrongCommandOption_Text)

        ###    Benachrichtigung - 100%iger Erfolg    ###
        #
        # mögliche Variablen:
        #
        #   {target}        = Name des Ziels
        #
        #

        # Erster Text
        outcome_100Percent_Text = "Alle Teilnehmer erfüllten ihre Aufgabe perfekt beim Run auf {target}. "
        outcome_100Percent_Text += "Es gab keinerlei Verluste und der Job brachte die gewünschten Informationen. "
        outcome_100Percent_Text += "Der Erlös des Verkaufs der erbeuteten Daten wird anteilsmäßig an die Teilnehmer verteilt: "

        message_Outcome_100Percent.append(outcome_100Percent_Text)

        # Zweiter Text
        outcome_100Percent_Text = "Der Plan funktionierte Perfekt. Das ganze Team konnte unerkannt "
        outcome_100Percent_Text += "in den Komplex von {target} eindringen, ohne das die Konzerntruppen alamiert wurden. "
        outcome_100Percent_Text += "Der Erlös des Verkaufs der erbeuteten Daten wird anteilsmäßig an die Teilnehmer verteilt: "

        # Text zur Liste hinzufügen
        message_Outcome_100Percent.append(outcome_100Percent_Text)

        ###    Benachrichtigung - 75-99% Überlebende des Run    ###
        #
        # mögliche Variablen:
        #
        #   {target}        = Name des Ziels
        #
        #

        # Erster Text
        outcome_75_99Percent_Text = "Nicht alle konnten unerkannt in die Schatten entkommen. "
        outcome_75_99Percent_Text += "Die Konzerntruppen von {target} konnten ein paar unglückliche des Teams "
        outcome_75_99Percent_Text += "ausschalten, die anderen konnten mit wertvollen Informationen entkommen. "
        outcome_75_99Percent_Text += "Der Erlös des Verkaufs der erbeuteten Daten wird anteilsmäßig an die "
        outcome_75_99Percent_Text += "überlebenden Teilnehmer verteilt: "

        # Text zur Liste hinzufügen
        message_Outcome_75_99Percent.append(outcome_75_99Percent_Text)

        # Zweiter Text
        outcome_75_99Percent_Text = "Es gab ein paar wenige Verluste beim Run auf {target}. "
        outcome_75_99Percent_Text += "Die meisten entkamen unerkannt in die Schatten. "
        outcome_75_99Percent_Text += "Der Erlös des Verkaufs der erbeuteten Daten wird anteilsmäßig an die "
        outcome_75_99Percent_Text += "überlebenden Teilnehmer verteilt: "

        # Text zur Liste hinzufügen
        message_Outcome_75_99Percent.append(outcome_75_99Percent_Text)

        ###    Benachrichtigung - 25-74% Überlebende des Run    ###
        #
        # mögliche Variablen:
        #
        #   {target}        = Name des Ziels
        #
        #

        # Erster Text
        outcome_25_74Percent_Text = "Verluste waren beim Run einkalkuliert, doch der Preis war hoch. "
        outcome_25_74Percent_Text += "Die Kernmannschaft konnte bei dem Run auf {target} "
        outcome_25_74Percent_Text += "mit den gewünschten Informationen entkommen. "
        outcome_25_74Percent_Text += "Der Erlös des Verkaufs der erbeuteten Daten wird anteilsmäßig an die "
        outcome_25_74Percent_Text += "überlebenden Teilnehmer verteilt: "

        # Text zur Liste hinzufügen
        message_Outcome_25_74Percent.append(outcome_25_74Percent_Text)

        # Zweiter Text
        outcome_25_74Percent_Text = "Das Team musste einen zu hohen Preis für ihren Erfolg zahlen. "
        outcome_25_74Percent_Text += "Trotz hoher Verluste konnten einige Teilnehmer den Run auf {target} "
        outcome_25_74Percent_Text += "erfolgreich abschliessen. "
        outcome_25_74Percent_Text += "Der Erlös des Verkaufs der erbeuteten Daten wird anteilsmäßig an die "
        outcome_25_74Percent_Text += "überlebenden Teilnehmer verteilt: "

        # Text zur Liste hinzufügen
        message_Outcome_25_74Percent.append(outcome_25_74Percent_Text)

        ###    Benachrichtigung - 01-24% Überlebende des Run    ###
        #
        # mögliche Variablen:
        #
        #   {target}        = Name des Ziels
        #
        #

        # Erster Text
        outcome_01_24Percent_Text = "Das Team hat bei dem Run auf {target} fast alle Mitglieder verloren. "
        outcome_01_24Percent_Text += "Die wenigen Überlebenden verkriechen sich in den Schatten um "
        outcome_01_24Percent_Text += "ihre Wunden zu versorgen und die gefallenen Kameraden zu betrauern. "
        outcome_01_24Percent_Text += "Der Erlös des Verkaufs der erbeuteten Daten wird anteilsmäßig an die "
        outcome_01_24Percent_Text += "überlebenden Teilnehmer verteilt: "

        # Text zur Liste hinzufügen
        message_Outcome_01_24Percent.append(outcome_01_24Percent_Text)

        ###    Benachrichtigung - keine Überlebende des Run    ###
        #
        # mögliche Variablen:
        #
        #   {target}        = Name des Ziels
        #
        #

        # Erster Text
        outcome_00Percent_Text = "Die Leben aller Runner wurden ausgelöscht... "
        outcome_00Percent_Text += "Die Streitkräfte von {target} waren besser bewaffnet und offensichtlich vorbereitet. "
        outcome_00Percent_Text += "Eine bessere Planung hätte diesen Fehlschlag wohl verhindern können. "

        # Text zur Liste hinzufügen
        message_Outcome_00Percent.append(outcome_00Percent_Text)

        # Zweiter Text
        outcome_00Percent_Text = "Die Leben aller Runner wurden ausgelöscht... "
        outcome_00Percent_Text += "Die Sicherheitskräfte von {target} waren offenbar gewarnt. "
        outcome_00Percent_Text += "War der Verräter in den eigenen Reihen? "

        # Text zur Liste hinzufügen
        message_Outcome_00Percent.append(outcome_00Percent_Text)

        # Dritter Text
        outcome_00Percent_Text = "Was ist da nur dermassen schief gelaufen? "
        outcome_00Percent_Text += "Die Sicherheitskräfte von {target} haben alle Runner ausgelöscht, "
        outcome_00Percent_Text += "bevor auch nur einer den Megaplex betreten konnte. "
        outcome_00Percent_Text += "Wurden wir etwa verraten? "

        # Text zur Liste hinzufügen
        message_Outcome_00Percent.append(outcome_00Percent_Text)

        #
        #
        ###    Benachrichtigs-Texte in die Datenbank eintragen    ###
        #
        #

        # Bestehende Tabelle löschen
        self.DB_dropTable_Messages()

        # Tabelle neu erzeugen
        self.DB_create_Tables()

        # Basis SQL Kommando um neue Daten in die Tabelle einzutragen
        sql = "INSERT INTO game_heist_messages ( messageType, messageText ) VALUES ( ?,? )"

        #
        # Für jeden Eintrag der 'message_CoolDown'-Liste einen Datensatz in der Datenbank erzeugen
        for message in message_CoolDown:

            # Variablen für das SQL-Basis Kommando vorbereiten
            val = (self.MessageType_IsOnCooldown, message)

            # In die Datenbank schreiben - Doppelte Werte werden ignoriert
            try:
                self.GameDB.execute(sql, val)

            except:
                pass
        #
        # Für jeden Eintrag der 'message_GameCooldownOver'-Liste einen Datensatz in der Datenbank erzeugen
        for message in message_GameCooldownOver:

            # Variablen für das SQL-Basis Kommando vorbereiten
            val = (self.MessageType_GameCooldownOver, message)

            # In die Datenbank schreiben - Doppelte Werte werden ignoriert
            try:
                self.GameDB.execute(sql, val)

            except:
                pass 
        #
        # Für jeden Eintrag der 'message_NewGameStart'-Liste einen Datensatz in der Datenbank erzeugen
        for message in message_NewGameStart:

            # Variablen für das SQL-Basis Kommando vorbereiten
            val = (self.MessageType_NewGameStart, message)

            # In die Datenbank schreiben - Doppelte Werte werden ignoriert
            try:
                self.GameDB.execute(sql, val)

            except:
                pass
        #
        # Für jeden Eintrag der 'message_GameStartIntro'-Liste einen Datensatz in der Datenbank erzeugen
        for message in message_GameStartIntro:

            # Variablen für das SQL-Basis Kommando vorbereiten
            val = (self.MessageType_GameStartIntro, message)

            # In die Datenbank schreiben - Doppelte Werte werden ignoriert
            try:
                self.GameDB.execute(sql, val)

            except:
                pass
        #
        # Für jeden Eintrag der 'message_NewPlayerEntry'-Liste einen Datensatz in der Datenbank erzeugen
        for message in message_NewPlayerEntry:

            # Variablen für das SQL-Basis Kommando vorbereiten
            val = (self.MessageType_NewPlayer, message)

            # In die Datenbank schreiben - Doppelte Werte werden ignoriert
            try:
                self.GameDB.execute(sql, val)

            except:
                pass
        #
        # Für jeden Eintrag der 'message_NotEnoughPoints'-Liste einen Datensatz in der Datenbank erzeugen
        for message in message_NotEnoughPoints:

            # Variablen für das SQL-Basis Kommando vorbereiten
            val = (self.MessageType_NotEnoughPoints, message)

            # In die Datenbank schreiben - Doppelte Werte werden ignoriert
            try:
                self.GameDB.execute(sql, val)

            except:
                pass
        #
        # Für jeden Eintrag der 'message_NotEnoughPlayer'-Liste einen Datensatz in der Datenbank erzeugen
        for message in message_NotEnoughPlayer:

            # Variablen für das SQL-Basis Kommando vorbereiten
            val = (self.MessageType_NotEnoughPlayer, message)

            # In die Datenbank schreiben - Doppelte Werte werden ignoriert
            try:
                self.GameDB.execute(sql, val)

            except:
                pass
        #
        # Für jeden Eintrag der 'message_StakeBelowMinimum'-Liste einen Datensatz in der Datenbank erzeugen
        for message in message_StakeBelowMinimum:

            # Variablen für das SQL-Basis Kommando vorbereiten
            val = (self.MessageType_StakeBelowMinimum, message)

            # In die Datenbank schreiben - Doppelte Werte werden ignoriert
            try:
                self.GameDB.execute(sql, val)

            except:
                pass
        #
        # Für jeden Eintrag der 'message_StakeOverMaximum'-Liste einen Datensatz in der Datenbank erzeugen
        for message in message_StakeOverMaximum:

            # Variablen für das SQL-Basis Kommando vorbereiten
            val = (self.MessageType_StakeOverMaximum, message)

            # In die Datenbank schreiben - Doppelte Werte werden ignoriert
            try:
                self.GameDB.execute(sql, val)

            except:
                pass
        #
        # Für jeden Eintrag der 'message_WrongCommandOption'-Liste einen Datensatz in der Datenbank erzeugen
        for message in message_WrongCommandOption:

            # Variablen für das SQL-Basis Kommando vorbereiten
            val = (self.MessageType_WrongCommandOption, message)

            # In die Datenbank schreiben - Doppelte Werte werden ignoriert
            try:
                self.GameDB.execute(sql, val)

            except:
                pass
        #
        # Für jeden Eintrag der 'message_Outcome_100Percent'-Liste einen Datensatz in der Datenbank erzeugen
        for message in message_Outcome_100Percent:

            # Variablen für das SQL-Basis Kommando vorbereiten
            val = (self.MessageType_Outcome_100Percent, message)

            # In die Datenbank schreiben - Doppelte Werte werden ignoriert
            try:
                self.GameDB.execute(sql, val)

            except:
                pass
        #
        # Für jeden Eintrag der 'message_Outcome_75_99Percent'-Liste einen Datensatz in der Datenbank erzeugen
        for message in message_Outcome_75_99Percent:

            # Variablen für das SQL-Basis Kommando vorbereiten
            val = (self.MessageType_Outcome_75_99Percent, message)

            # In die Datenbank schreiben - Doppelte Werte werden ignoriert
            try:
                self.GameDB.execute(sql, val)

            except:
                pass
        #
        # Für jeden Eintrag der 'message_Outcome_25_74Percent'-Liste einen Datensatz in der Datenbank erzeugen
        for message in message_Outcome_25_74Percent:

            # Variablen für das SQL-Basis Kommando vorbereiten
            val = (self.MessageType_Outcome_25_74Percent, message)

            # In die Datenbank schreiben - Doppelte Werte werden ignoriert
            try:
                self.GameDB.execute(sql, val)

            except:
                pass
        #
        # Für jeden Eintrag der 'message_Outcome_01_24Percent'-Liste einen Datensatz in der Datenbank erzeugen
        for message in message_Outcome_01_24Percent:

            # Variablen für das SQL-Basis Kommando vorbereiten
            val = (self.MessageType_Outcome_01_24Percent, message)

            # In die Datenbank schreiben - Doppelte Werte werden ignoriert
            try:
                self.GameDB.execute(sql, val)

            except:
                pass
        #
        # Für jeden Eintrag der 'message_Outcome_00Percent'-Liste einen Datensatz in der Datenbank erzeugen
        for message in message_Outcome_00Percent:

            # Variablen für das SQL-Basis Kommando vorbereiten
            val = (self.MessageType_Outcome_00Percent, message)

            # In die Datenbank schreiben - Doppelte Werte werden ignoriert
            try:
                self.GameDB.execute(sql, val)

            except:
                pass

        # Daten speichern
        self.GameDB.commit()

        return

    def DB_create_DefaultTargets(self):
        ''' Erzeuge verschiedene Target-Einträge in der Datenbank '''
        thisActionName = "DB_create_DefaultTargets"

        # Bestehende Tabelle löschen
        self.DB_dropTable_Targets()

        # Tabelle neu erzeugen
        self.DB_create_Tables()

        # Basis SQL Kommando um neue Daten in die Tabelle einzutragen
        sql = "INSERT INTO game_heist_targets ( targetName ) VALUES ( ? )"

        targets = ["Ares Macrotechnology",
                   "Aztechnology",
                   "Mitsuhama Computer Technologies",
                   "Renraku Computer Systems",
                   "Saeder-Krupp",
                   "Yamatetsu Corporation"]

        # Für jeden Eintrag der Liste einen Datensatz in der Datenbank erzeugen
        for target in targets:

            # Variable für das SQL-Basis Kommando vorbereiten
            val_target = (target, )

            # In die Datenbank schreiben - Doppelte Werte werden ignoriert
            try:
                self.GameDB.execute(sql, val_target)

            except:
                pass

        # Daten speichern
        self.GameDB.commit()

        return

    #####################################################################################

    def DB_dropTable_Messages(self):
        ''' Benachrichtigungs Tabelle löschen '''
        thisActionName = "DB_dropTable_Messages"

        # Bestehende Tabelle löschen
        sql = "DROP TABLE game_heist_messages"

        try:
            self.GameDB.execute(sql)
            self.GameDB.commit()

        except Exception as e:

            # Fehler in Log-Datei schreiben
            self.Logger.WriteLog(
                " --- FEHLER - {0} ---".format(thisActionName))
            self.Logger.WriteLog(
                " --- EXCEPTION: {0}".format(str(sys.exc_info())))

            return False

        return True

    def DB_dropTable_Targets(self):
        ''' Targets Tabelle löschen '''
        thisActionName = "DB_dropTable_Targets"

        # Bestehende Tabelle löschen
        sql = "DROP TABLE game_heist_targets"

        try:
            self.GameDB.execute(sql)
            self.GameDB.commit()

        except Exception as e:

            # Fehler in Log-Datei schreiben
            self.Logger.WriteLog(
                " --- FEHLER - {0} ---".format(thisActionName))
            self.Logger.WriteLog(
                " --- EXCEPTION: {0}".format(str(sys.exc_info())))

            return False

        return True

    #####################################################################################

    def DB_delete_Data(self):
        ''' Lösche nicht mehr benötigte Daten aus der Datenbank '''
        thisActionName = "DB_delete_Data"

        # Eine GameID ist vorhanden
        if not (self.GameID == 0):

            # Daten der letzten 5 Spiele erhalten
            gameHeistOldesID = int(self.GameID) - 5

            # SQL vorbereiten
            sql = "DELETE FROM game_heist_gamedata WHERE gameID <= ?"
            val = (int(gameHeistOldesID), )

            # SQL ausführen
            try:
                self.GameDB.execute(sql, val)

            except:
                self.Logger.WriteLog(
                    " FEHLER: Datenbank 'MultiRaffle' - {0}".format(thisActionName))
                self.Logger.WriteLog(
                    " --- EXCEPTION: {0}".format(str(sys.exc_info())))

        return

    #####################################################################################

    def DB_check_PlayerExist(self, playerName):
        ''' Prüft, ob der Spieler bereits in der Datenbank eingetragen wurde '''
        thisActionName = "DB_check_PlayerExist"

        sql = "SELECT count(userName) FROM game_heist_gamedata WHERE userName = ? AND gameID = ?"
        val = (playerName, self.GameID)

        try:
            result = self.GameDB.execute(sql, val).fetchone()[0]

        except Exception as e:

            # Fehler in Log-Datei schreiben
            self.Logger.WriteLog(
                " --- FEHLER - {0} ---".format(thisActionName))
            self.Logger.WriteLog(
                " --- EXCEPTION: {0}".format(str(sys.exc_info())))

            return 0

        # Spieler nimmt bereits am Spiel teil
        if not result == 0:
            return True

        # Spieler noch nicht in der Datenbank
        else:
            return False

    def DB_get_LastID(self):
        ''' Auslesen der letzten HeistID aus der Datenbank '''
        thisActionName = "DB_get_LastID"

        # SQL-Abfrage vorbereiten
        sql = "SELECT MAX(gameID) FROM game_heist_gamedata"

        try:
            # SQL-Abfrage ausführen
            lastHeistID = self.GameDB.execute(sql).fetchone()[0]

        except Exception as e:

            # Fehler in Log-Datei schreiben
            self.Logger.WriteLog(
                " --- FEHLER - {0} ---".format(thisActionName))
            self.Logger.WriteLog(
                " --- EXCEPTION: {0}".format(str(sys.exc_info())))

        if not lastHeistID:
            lastHeistID = 0

        return lastHeistID

    def DB_get_MessageText(self, messageType):
        ''' Auslesen eines Textes aus der Datenbank '''
        thisActionName = "DB_get_MessageText"
        resultList = []

        # SQL-Abfrage vorbereiten
        sql = "SELECT messageText FROM game_heist_messages WHERE messageType = ?"
        val = (messageType, )

        try:
            # SQL-Abfrage ausführen
            rows = self.GameDB.execute(sql, val).fetchall()

        except Exception as e:

            # Fehler in Log-Datei schreiben
            self.Logger.WriteLog(
                " --- FEHLER - {0} ---".format(thisActionName))
            self.Logger.WriteLog(
                " --- EXCEPTION: {0}".format(str(sys.exc_info())))

            return resultList

        # Abfrage lieferte Daten
        if rows:

            # Für jeden Datensatz ausführen
            for row in rows:

                # Übergebe Daten an Liste
                resultList.append(row[0])

        return resultList

    def DB_get_PlayersData(self):
        ''' Auslesen der Teilnehmerdaten aus der Datenbank '''
        thisActionName = "DB_get_PlayersData"
        resultList = []
        resultDict = {}

        # SQL-Abfrage vorbereiten
        sql = "SELECT userName, userStake FROM game_heist_gamedata WHERE gameID = ? ORDER BY userStake DESC"
        val = (self.GameID, )

        try:
            # SQL-Abfrage ausführen
            rows = self.GameDB.execute(sql, val).fetchall()

        except Exception as e:

            # Fehler in Log-Datei schreiben
            self.Logger.WriteLog(
                " --- FEHLER - {0} ---".format(thisActionName))
            self.Logger.WriteLog(
                " --- EXCEPTION: {0}".format(str(sys.exc_info())))

            return resultList

        # Abfrage lieferte Daten
        if rows:

            # Für jeden Datensatz ausführen
            for row in rows:

                # Spielerdaten in Dictionary übernehmen
                resultDict = {
                    "userName": row[0],
                    "userStake": row[1]
                }

                # Übergebe Daten an Liste
                resultList.append(resultDict)

        return resultList

    def DB_get_TargetNames(self):
        ''' Auslesen der möglichen Ziele aus der Datenbank '''
        thisActionName = "DB_get_TargetNames"
        resultList = []

        # SQL-Abfrage vorbereiten
        sql = "SELECT targetName FROM game_heist_targets"

        try:
            # SQL-Abfrage ausführen
            rows = self.GameDB.execute(sql).fetchall()

        except Exception as e:

            # Fehler in Log-Datei schreiben
            self.Logger.WriteLog(
                " --- FEHLER - {0} ---".format(thisActionName))
            self.Logger.WriteLog(
                " --- EXCEPTION: {0}".format(str(sys.exc_info())))

            return resultList

        # Abfrage lieferte Daten
        if rows:

            # Für jeden Datensatz ausführen
            for row in rows:

                # Übergebe Daten an Liste
                resultList.append(row[0])

        return resultList

    #####################################################################################

    def DB_insert_NewPlayer(self, playerData):
        ''' Neuen Spieler in der Datenbank eintragen, falls nocht nicht vorhanden '''
        thisActionName = "DB_insert_NewPlayer"

        sql = "INSERT INTO game_heist_gamedata( gameID, gameStartTimestamp, userName, userStake ) VALUES ( ?,?,?,? )"
        val = (self.GameID, self.GameStartTimestamp,
               playerData["playerName"], playerData["playerStake"])

        try:
            # SQL-Abfrage ausführen
            self.GameDB.execute(sql, val)
            self.GameDB.commit()

        except Exception as e:

            # Fehler in Log-Datei schreiben
            self.Logger.WriteLog(
                " --- FEHLER - {0} ---".format(thisActionName))
            self.Logger.WriteLog(
                " --- EXCEPTION: {0}".format(str(sys.exc_info())))

            return False

        return True

    #####################################################################################

    def chat_WriteTextMessage(self, messageText):
        ''' Schreibt eine Nachricht in den Chat '''
        thisActionName = "chat_WriteTextMessage"

        # Text in den Chat schreiben
        self.Parent.SendStreamMessage(
            "/me : {messagetext}".format(
                messagetext=str(messageText)
            )
        )

        return

    #####################################################################################

    def RandomMessage_ByType(self, messageType):
        ''' Auslesen einer zufälligen Nachricht aus der Datenbank '''
        thisActionName = "RandomMessage_ByType"

        # Nachrichten aus der Datenbank auslesen
        messagesList = self.DB_get_MessageText(
            messageType=messageType
        )

        # Die Liste enthält Nachrichten-Texte
        if messagesList:

            # Liste durchmischen
            random.shuffle(messagesList)
            # Anzahl der Listenelemente bestimmen
            listLength = int(len(messagesList))
            # Nachrichten-Text übernehmen
            message = messagesList[self.Parent.GetRandom(0, listLength)]

            # Rückgabe der zufälligen Nachricht an aufrufende Funktion
            return message

        return

    def RandomTarget_ByName(self):
        ''' Ein zufälliges Ziel für den Heist auswählen '''
        thisActionName = "RandomTarget_ByName"

        # Ziele aus der Datenbank auslesen
        targetList = self.DB_get_TargetNames()

        # Die Liste enthält Nachrichten-Texte
        if targetList:

            # Liste durchmischen
            random.shuffle(targetList)
            # Anzahl der Listenelemente bestimmen
            listLength = int(len(targetList))
            # Nachrichten-Text übernehmen
            target = targetList[self.Parent.GetRandom(0, listLength)]

            # Rückgabe der zufälligen Nachricht an aufrufende Funktion
            return target

        return

    #####################################################################################

    def WriteMessage_IsOnCooldown(self):
        ''' Vorbereiten der Cooldown-Nachricht zur Ausgabe in den Chat '''
        thisActionName = "WriteMessage_IsOnCooldown"

        # Benachrichtigung aus der Datenbank auslesen
        messageText = self.RandomMessage_ByType(
            messageType=self.MessageType_IsOnCooldown
        )

        # Verbleibende Cooldown-Zeit ermitteln
        cooldownTime = myTime.TimePrettyFormatString(
            self.CD.GetCooldownDuration(
                scriptname=self.ScriptName, command=self.ClassName
            )
        )

        # Nachricht in den Chat schreiben
        self.chat_WriteTextMessage(
            messageText=str(messageText).format(
                time=cooldownTime,
                command=self.Settings.Game_Command
            )
        )

        return

    def WriteMessage_GameCooldownOver(self):
        ''' Vorbereiten der Cooldown-Abgelaufen-Nachricht zur Ausgabe in den Chat '''
        thisActionName = "WriteMessage_GameCooldownOver"

        # Benachrichtigung aus der Datenbank auslesen
        messageText = self.RandomMessage_ByType(
            messageType=self.MessageType_GameCooldownOver
        )

        # Nachricht in den Chat schreiben
        self.chat_WriteTextMessage(
            messageText=str(messageText).format(
                command=self.Settings.Game_Command
            )
        )

        return

    def Writemessage_NewGameStart(self, data):
        ''' Schreibt die Benachrichtigung über den Start eines neuen Spiels in den Chat '''
        thisActionName = "Writemessage_NewGameStart"

        # Benachrichtigung aus der Datenbank auslesen
        messageText = self.RandomMessage_ByType(
            messageType=self.MessageType_NewGameStart
        )

        # Nachricht in den Chat schreiben
        self.chat_WriteTextMessage(
            messageText=str(messageText).format(
                user=data.UserName,
                command=self.Settings.Game_Command,
                target=self.GameTargetName,
                time=myTime.TimePrettyFormatString(
                    int(self.Settings.Game_UntilStart_Time)
                ),
                maxpoints=TransformLocale_Decimals(
                    self.Settings.Game_Settings_MaxStake
                ),
                pointsname=self.Parent.GetCurrencyName()
            )
        )

        return

    def Writemessage_GameStartIntroMessage(self):
        ''' Schreibt die Intro-Nachricht in den Chat '''
        thisActionName = "Writemessage_GameStartIntroMessage"

        # Benachrichtigung aus der Datenbank auslesen
        messageText = self.RandomMessage_ByType(
            messageType=self.MessageType_GameStartIntro
        )

        # Nachricht in den Chat schreiben
        self.chat_WriteTextMessage(
            messageText=str(messageText).format(
                target=self.GameTargetName
            )
        )

        return

    def Writemessage_NewPlayerEntry(self, playerData):
        ''' Schreibt die Benachrichtigung über Teilnahme eines neuen Spielers in den Chat '''
        thisActionName = "Writemessage_NewPlayerEntry"

        # Benachrichtigung aus der Datenbank auslesen
        messageText = self.RandomMessage_ByType(
            messageType=self.MessageType_NewPlayer
        )

        # Nachricht in den Chat schreiben
        self.chat_WriteTextMessage(
            messageText=str(messageText).format(
                user=playerData["playerDisplayName"],
                target=self.GameTargetName,
                stake=TransformLocale_Decimals(
                    playerData["playerStake"]
                ),
                pointsname=self.Parent.GetCurrencyName()
            )
        )

        return

    def WriteMessage_NotEnoughPoints(self, data):
        ''' Schreibt eine Benachrichtigung in den Chat, dass der Spieler nicht 
            über ausreichend Punkte verfügt.
        '''
        thisActionName = "WriteMessage_NotEnoughPoints"

        # Benachrichtigung aus der Datenbank auslesen
        messageText = self.RandomMessage_ByType(
            messageType=self.MessageType_NotEnoughPoints
        )

        # Nachricht in den Chat schreiben
        self.chat_WriteTextMessage(
            messageText=str(messageText).format(
                user=data.UserName,
                target=self.GameTargetName,
                points=TransformLocale_Decimals(
                    self.Parent.GetPoints(data.User)
                ),
                pointsname=self.Parent.GetCurrencyName()
            )
        )

        return

    def WriteMessage_NotEnoughPlayer(self, allPlayerData):
        ''' Schreibt eine Benachrichtigung in den Chat, dass sich nicht genügend
            Spieler eingefunden haben
        '''
        thisActionName = "WriteMessage_NotEnoughPlayer"

        # Rückerstattung des Einsatzes
        for player in allPlayerData:

            # Punkte zurück erstatten
            self.Parent.AddPoints(player["userName"],
                                  self.Parent.GetDisplayName(
                                      player["userName"]),
                                  player["userStake"])

        # Benachrichtigung aus der Datenbank auslesen
        messageText = self.RandomMessage_ByType(
            messageType=self.MessageType_NotEnoughPlayer
        )

        # Nachricht in den Chat schreiben
        self.chat_WriteTextMessage(
            messageText=str(messageText).format(
                target=self.GameTargetName,
                pointsname=self.Parent.GetCurrencyName()
            )
        )

        return

    def Writemessage_StakeBelowMinimum(self, data):
        ''' Schreibt die Benachrichtigung über einen negativen Einsatz in den Chat '''
        thisActionName = "Writemessage_StakeBelowMinimum"

        # Benachrichtigung aus der Datenbank auslesen
        messageText = self.RandomMessage_ByType(
            messageType=self.MessageType_StakeBelowMinimum
        )

        # Nachricht in den Chat schreiben
        self.chat_WriteTextMessage(
            messageText=str(messageText).format(
                user=data.UserName,
                minpoints=TransformLocale_Decimals(
                    self.Settings.Game_Settings_MinStake),
                pointsname=self.Parent.GetCurrencyName()
            )
        )

        return

    def WriteMessage_StakeOverMaximum(self, data):
        ''' Schreibt eine Benachrichtigung in den Chat, dass der Einsatz des Spieler 
            das Maximum überschritten hat und somit reduziert wird.
        '''
        thisActionName = "WriteMessage_StakeOverMaximum"

        # Benachrichtigung aus der Datenbank auslesen
        messageText = self.RandomMessage_ByType(
            messageType=self.MessageType_StakeOverMaximum
        )

        # Nachricht in den Chat schreiben
        self.chat_WriteTextMessage(
            messageText=str(messageText).format(
                user=data.UserName,
                target=self.GameTargetName,
                command=self.Settings.Game_Command,
                maxpoints=TransformLocale_Decimals(
                    int(self.Settings.Game_Settings_MaxStake)
                ),
                pointsname=self.Parent.GetCurrencyName()
            )
        )

        return

    def WriteMessage_WrongCommandOption(self, data):
        ''' Schreibt eine Benachrichtigung in den Chat, dass der Spieler 
            das Kommando fehlerhaft aufgerufen hat.
        '''
        thisActionName = "WriteMessage_StakeOverMaximum"

        # Benachrichtigung aus der Datenbank auslesen
        messageText = self.RandomMessage_ByType(
            messageType=self.MessageType_WrongCommandOption
        )

        # Nachricht in den Chat schreiben
        self.chat_WriteTextMessage(
            messageText=str(messageText).format(
                user=data.UserName,
                command=self.Settings.Game_Command,
                maxpoints=TransformLocale_Decimals(
                    int(self.Settings.Game_Settings_MaxStake)
                ),
                pointsname=self.Parent.GetCurrencyName()
            )
        )

        return

    def WriteMessage_GameResult(self, percentage):
        ''' Schreibt die Endnachricht in den Chat
        '''
        thisActionName = "WriteMessage_GameResult"

        # Nachricht nach der übergebenen Prozentzahlen auslesen
        if (percentage == 0):

            # Benachrichtigung aus der Datenbank auslesen
            messageText = self.RandomMessage_ByType(
                messageType=self.MessageType_Outcome_00Percent
            )

        elif (percentage >= 1) and (percentage <= 24):

            # Benachrichtigung aus der Datenbank auslesen
            messageText = self.RandomMessage_ByType(
                messageType=self.MessageType_Outcome_01_24Percent
            )

        elif (percentage >= 25) and (percentage <= 74):

            # Benachrichtigung aus der Datenbank auslesen
            messageText = self.RandomMessage_ByType(
                messageType=self.MessageType_Outcome_25_74Percent
            )

        elif (percentage >= 75) and (percentage <= 99):

            # Benachrichtigung aus der Datenbank auslesen
            messageText = self.RandomMessage_ByType(
                messageType=self.MessageType_Outcome_75_99Percent
            )

        else:

            # Benachrichtigung aus der Datenbank auslesen
            messageText = self.RandomMessage_ByType(
                messageType=self.MessageType_Outcome_100Percent
            )

        # Nachricht in den Chat schreiben
        self.chat_WriteTextMessage(
            messageText=str(messageText).format(
                target=self.GameTargetName)
        )

        return

    def WriteMessage_GamePayout(self, payoutdata):
        ''' Ausgabe der Auszahlung der Gewinner im Chat '''
        thisActionName = "WriteMessage_GamePayout"
        tempTextOutput = ""
        pointsName = self.Parent.GetCurrencyName()

        # Für jeden Datensatz ausführen
        for userData in payoutdata:

            # Text vorbereiten
            tempTextOutput += str(userData["userDisplayName"]) + " (" + \
                TransformLocale_Decimals(
                    userData["userPayout"]) + " " + pointsName + "), "

        # Ersetze letztes Komma im String
        textWinner = BotHelper.ReplaceFromRight(tempTextOutput, ", ", "", 1)
        # Ersetze vorletztes Komma im String
        textWinner = BotHelper.ReplaceFromRight(textWinner, ", ", " und ", 1)

        # Ausgabe des Textes
        self.chat_WriteTextMessage(textWinner)

        return

    #####################################################################################

    def game_NewPlayerData(self, data):
        ''' Neuer Spieler: Daten prüfen in einem Dictonary zurückgeben '''
        thisActionName = "game_NewPlayer"
        dictPlayerData = {}
        playerStake = 0

        # Spieler will alles einsetzen
        if (data.GetParam(1).lower() == "max") or (data.GetParam(1).lower() == "all") or (data.GetParam(1).lower() == "allin"):

            # Übernehme die aktuellen Punkte aus der Datenbank
            playerStake = int(self.Parent.GetPoints(data.User))

        else:

            # Übernehme die Zahl aus den Parametern
            try:
                playerStake = int(data.GetParam(
                    1).replace(".", "").replace(",", ""))

            # Übergebener Parameter ist keine Zahl
            except:

                # Abbruch und leeres Dictionary an aufrufende Funktion
                return dictPlayerData

        # Einsatz ist grösser als Maximum
        if playerStake > int(self.Settings.Game_Settings_MaxStake):

            playerStake = int(self.Settings.Game_Settings_MaxStake)
            maximumStakeReached = True

        else:
            maximumStakeReached = False

        # Einsatz ist kleiner oder gleich dem eingestellten Minimum
        if playerStake < self.Settings.Game_Settings_MinStake:
            belowStake = "belowMinStake"

        else:
            belowStake = True

        # Spieler hat nicht genügend Punkte um am Einsatz teilzunehmen
        if playerStake > int(self.Parent.GetPoints(data.User)):
            notEnoughPoints = True

        else:
            notEnoughPoints = False

        # Daten in Dictionary übertragen
        dictPlayerData = {
            "playerName": data.User,
            "playerDisplayName": data.UserName,
            "playerStake": playerStake,
            "belowStake": belowStake,
            "maximumStake": maximumStakeReached,
            "currentPlayerPoints": int(self.Parent.GetPoints(data.User)),
            "notEnoughPoints": notEnoughPoints
        }

        return dictPlayerData

    def game_PayReward(self, winnerdata):
        ''' Auszahlen des erbeuteten Gewinns '''
        resultData = []
        tempDict = {}

        for winner in winnerdata:

            # Gewinn errechnen
            payout = winner["userStake"] * \
                float(self.Settings.Game_Result_Multiplier)

            # Wert auf die nächste Zahl aufrunden
            payout = math.ceil(payout)

            # Daten in Dictionary übernehmen
            tempDict = {
                "userName": winner["userName"],
                "userDisplayName": self.Parent.GetDisplayName(
                    winner["userName"]),
                "userPayout": int(payout)
            }

            # Punkte an User übergeben
            self.Parent.AddPoints(tempDict["userName"],
                                  tempDict["userDisplayName"],
                                  tempDict["userPayout"])

            resultData.append(tempDict)

        return resultData

    #####################################################################################

    def game_StartHeist(self, data):
        ''' Starte das Spiel und/oder fügt neue Spieler hinzu '''
        thisActionName = "game_StartHeist"

        # Spiel ist im Cooldown und es läuft kein Heist - Abbruch
        if self.CD.IsOnCooldown(scriptname=self.ScriptName, command=self.ClassName) and (self.GameStartTimestamp == ""):

            # Letzte Benachrichtigung ist bereits die eingestellte Zeit vergangen
            if not self.CD.IsOnCooldown(scriptname=self.ScriptName, command=self.ClassName + " Supress Message"):

                # Nachricht über Cooldown in den Chat schreiben
                self.WriteMessage_IsOnCooldown()

                # Setze Cooldown-Zeit zur Unterdrückung zu vieler Nachrichten im Chat
                self.CD.AddCooldown(scriptname=self.ScriptName,
                                    command=self.ClassName + " Supress Message",
                                    cooldownTime=int(15)
                                    )

            return

        # Spielerdaten überprüfen
        playerData = self.game_NewPlayerData(data=data)
        playerExist = self.DB_check_PlayerExist(playerName=data.User)

        # Das Kommando wurde falsch aufgerufen - Abbruch
        if not playerData:
            self.WriteMessage_WrongCommandOption(data=data)
            return

        # Spieler hat nicht genügend Punkte um am Einsatz teilzunehmen - Abbruch
        if playerData["playerStake"] > playerData["currentPlayerPoints"]:
            self.WriteMessage_NotEnoughPoints(data=data)
            return

        # Spieler setzt weniger ein, als das eingestellte Minimum - Abbruch
        if not (playerData["belowStake"] == True):
            self.Writemessage_StakeBelowMinimum(data=data)
            return

        ### ALLE PRÜFUNGEN WURDEN ERFOLGREICH DURCHGEFÜHRT ###

        # --- SPIEL IST BEREITS AKTIV ---
        if not (self.GameStartTimestamp == ""):

            # Spieler ist noch nicht beigetreten
            if not playerExist:

                # Spieler muss den Einsatz reduzieren, da über dem maximalen Wert
                if playerData["maximumStake"]:
                    self.WriteMessage_StakeOverMaximum(data=data)
                    return

                # Neuen Spieler in Datenbank eintragen
                self.DB_insert_NewPlayer(playerData=playerData)

                self.Logger.WriteLog(
                    " {0} - Neuer Teilnehmer: {1}".format(
                        thisActionName,
                        playerData["playerDisplayName"]
                    ))

                # Punkte vom Konto des Users abziehen
                self.Parent.RemovePoints(playerData["playerName"],
                                         playerData["playerDisplayName"],
                                         playerData["playerStake"])

                # Benachrichtigung im Chat
                self.Writemessage_NewPlayerEntry(playerData=playerData)

                return

        # --- NEUES SPIEL STARTEN ---
        else:

            # Spieler muss den Einsatz reduzieren, da über dem maximalen Wert
            if playerData["maximumStake"]:
                self.WriteMessage_StakeOverMaximum(data=data)
                return

            # Zeitstempel in Variable übernehmen
            self.GameStartTimestamp = time.time()
            # Ziel in Variable übernehmen
            self.GameTargetName = self.RandomTarget_ByName()
            # GameID in Variable übernehmen
            self.GameID = int(self.DB_get_LastID()) + 1

            # Ältere Spieldaten löschen
            self.DB_delete_Data()

            self.Logger.WriteLog(
                " {0} - Neues Spiel von {1} gestartet".format(
                    thisActionName,
                    playerData["playerDisplayName"]
                ))

            # Neuen Spieler in Datenbank eintragen
            self.DB_insert_NewPlayer(playerData=playerData)

            # Punkte vom Konto des Users abziehen
            self.Parent.RemovePoints(playerData["playerName"],
                                     playerData["playerDisplayName"],
                                     playerData["playerStake"])

            # Nachricht in den Chat schreiben
            self.Writemessage_NewGameStart(data=data)

        return

    def game_EndHeist(self):
        ''' Beende das aktuelle Spiel '''
        thisActionName = "game_EndHeist"
        winnerData = []

        # Daten aller Spieler ermitteln
        allPlayerData = self.DB_get_PlayersData()
        # Anzahl der Spieler
        numberOfPlayers = len(allPlayerData)

        # Mindest Spieleranzahl wurde nicht erreicht - Beenden
        if numberOfPlayers < self.Settings.Game_Min_Participant:

            # Nachricht in den Chat schreiben
            self.WriteMessage_NotEnoughPlayer(allPlayerData=allPlayerData)

            # Nachricht ins Log schreiben
            self.Logger.WriteLog(
                " {0} - Unzureichende Anzahl Spieler".format(thisActionName))

        # Genügend Spieler vorhanden
        else:

            # Intro Nachricht in den Chat schreiben
            self.Writemessage_GameStartIntroMessage()

            # Gewinner ermitteln
            for singlePlayerData in allPlayerData:

                # Zufällig über Tod oder Leben entscheiden
                result = int(self.Parent.GetRandom(0, 2))

                # Spieler hat überlebt
                if result == 1:

                    # Spieler in Gewinnerliste übernehmen
                    winnerData.append(singlePlayerData)

            # Anzahl der Gewinner
            numberOfWinner = len(winnerData)

            # Prozentuale Anzahl der Gewinner berechnen und abrunden
            probability = int(float(float(numberOfWinner) /
                                    float(numberOfPlayers) * 100))

            # Ausgabe des Textes für den Spielausgang
            self.WriteMessage_GameResult(percentage=probability)

            # Gewinner auszahlen
            resultData = self.game_PayReward(winnerdata=winnerData)

            # Nur in den Chat schreiben, wenn ein Teilnehmer überlebt hat
            if not probability == 0:

                # Auszahlungsdetails in den Chat schreiben
                self.WriteMessage_GamePayout(payoutdata=resultData)

            # Nachricht ins Log schreiben
            self.Logger.WriteLog(
                " {0} - Spiel beendet, {1} Prozent Gewinner".format(
                    thisActionName,
                    probability
                ))

        # Zeitstempel zurücksetzen
        self.GameStartTimestamp = ""
        # Ziel zurücksetzen
        self.GameTargetName = ""
        # Zeitstempel für Cooldown-Benachrichtigung setzen
        self.LastGameFinishTimestamp = time.time()

        # Setze Cooldown-Zeit bevor das Spiel neu gestartet werden kann
        self.CD.AddCooldown(scriptname=self.ScriptName,
                            command=self.ClassName,
                            cooldownTime=int(self.Settings.Game_Cooldown_Time)
                            )

        return

    def game_Timer(self):
        ''' Timer für das Spiel '''
        thisActionName = "game_Timer"

        # Es läuft kein Heist und auch kein Cooldown - Abbruch
        if (self.GameStartTimestamp == "") and (self.LastGameFinishTimestamp == ""):
            return

        # Es läuft ein Spiel - Timer prüfen
        if not (self.GameStartTimestamp == ""):

            # aktuelle Laufzeit berechnen
            elapsedTime = (time.time() - self.GameStartTimestamp)

            # Zeit zum Beenden des Spieles erreicht
            if (elapsedTime >= int(self.Settings.Game_UntilStart_Time)):

                self.Logger.WriteLog(
                    " {0} - Spiel wird beendet".format(thisActionName))

                # Spiel beenden
                self.game_EndHeist()


        # Cooldown ist aktiv
        if not (self.LastGameFinishTimestamp == ""):

            # aktuelle Laufzeit berechnen
            elapsedTime = (time.time() - self.LastGameFinishTimestamp)

            # Heist ist nicht mehr im Cooldown
            if (elapsedTime >= int(self.Settings.Game_Cooldown_Time)):
    
                self.Logger.WriteLog(
                    " {0} - Cooldown-Zeit abgelaufen".format(thisActionName))

                self.WriteMessage_GameCooldownOver()

                # Zeitstempel zurücksetzen
                self.LastGameFinishTimestamp = ""

        return
