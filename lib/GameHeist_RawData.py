#!/usr/bin/python2
# -*- coding: utf-8 -*-
# pylint: disable=all

#------------------------------------------------------
# Import der Libraries
#------------------------------------------------------
import os
import re
import codecs

import GameHeist_Time as myTime
from GameHeist_ChatBotHelper import AppendDataToFile
from GameHeist_ChatBotHelper import TransformLocale_Decimals

#------------------------------------------------------
# Klasse
#------------------------------------------------------
class RawData(object):
    ''' Tracker für Events im Twitch-Chat '''
    def __init__( self, scriptname, settings, parent, logger, logfilepath = False, datafilespath = False, cooldown = False, counterdb = False, supressMessage = False ):
        ''' Initialisierung '''
        thisActionName = "__init__"
        
        # Übernahme der Variablen für ganze Klasse
        self.ClassName = "RawData"
        self.Version = "2.0.3"
        self.ScriptName = scriptname
        self.LogFilesPath = logfilepath
        self.DataFilesPath = datafilespath
        self.Parent = parent
        self.Settings = settings
        self.Logger = logger
        self.CoolDown = cooldown
        self.CounterDB = counterdb
        self.DataFilesPrefix = "GIVEAWAY_"

        self.RawLogFile = ""
        self.SubscriberLogFile = ""
        self.LatestSubscriberFile = ""
        self.LatestCheerFile = ""
        self.CurrentSubgoalCounterFile = ""
        self.GiveawayCounterFile = ""

        # Sub Informationen
        self.SubTypeList = list( ( "subgift", "sub", "resub" ) )
        self.SubPlanList = list( ( "Prime", "1000", "2000", "3000" ) )
        self.LastSubGifterUserName = ""
        self.LastSubGifterCounter = int(0)

        # Regex-Compile
        self.reUserName = re.compile(r"^[a-z0-9][a-z0-9_]{3,24}$")
        self.rePRIVMSG = re.compile(r"(@(?P<irctags>[^\ ]*)=([^;]*)(?:;|$)?\.tmi\.twitch\.tv\ PRIVMSG)")
        self.reUSERNOTICE = re.compile(r"(?:^(?:@(?P<irctags>[^\ ]*)\ )?:tmi\.twitch\.tv\ USERNOTICE)")
        self.reCheckArgument = re.compile(r"^(?:(?P<t1>\d{1,3})\|(?P<t2>\d{1,3})\|(?P<t3>\d{1,3}))$")
        self.reJOIN = re.compile(r"(@(?P<name>[^;]*)(?:;|$)?\.tmi\.twitch\.tv\ JOIN)")
        self.reWHISPER = re.compile(r"(@(?P<name>[^;]*)(?:;|$)?\.tmi\.twitch\.tv\ WHISPER)")

        # Log Verzeichniss erstellen
        if self.LogFilesPath:
            if not os.path.exists(self.LogFilesPath):
                os.makedirs(self.LogFilesPath)

            # Log Files definieren
            self.RawLogFile = os.path.join( self.LogFilesPath, str(myTime.FileTimeStamp()) + "_GiveawayExtention_RawData.txt" )
            self.SubscriberLogFile = os.path.join( self.LogFilesPath, str(myTime.FileTimeStamp()) + "_GiveawayExtention_SubscriberData.txt" )
            self.SubGifterLogFile = os.path.join( self.LogFilesPath, str(myTime.FileTimeStamp()) + "_GiveawayExtention_SubGifterData.txt" )
            self.CheerLogFile = os.path.join( self.LogFilesPath, str(myTime.FileTimeStamp()) + "_GiveawayExtention_CheerData.txt" )

        # Text-Data Verzeichniss erstellen
        if self.DataFilesPath:
            if not os.path.exists(self.DataFilesPath):
                os.makedirs(self.DataFilesPath)    

            # Daten-Files definieren
            self.LatestSubscriberFile = os.path.join( self.DataFilesPath, self.DataFilesPrefix + "LATESTSUBSCRIBER.txt")
            self.LatestSubsGifterFile = os.path.join( self.DataFilesPath, self.DataFilesPrefix + "LATESTSUBGIFTER.txt")
            self.LatestCheerFile = os.path.join( self.DataFilesPath, self.DataFilesPrefix + "LATESTCHEER.txt")
            self.CurrentSubgoalCounterFile = os.path.join( self.DataFilesPath, self.DataFilesPrefix + "COUNTER_CURRENTSUBGOAL.txt" )
            self.GiveawayCounterFile = os.path.join( self.DataFilesPath, self.DataFilesPrefix + "COUNTER_GIVEAWAYS.txt" )

        # Nur ins Log schreiben, wenn nicht unterdrückt
        if not supressMessage:
            # Meldung ins Log schreiben
            self.Logger.WriteLog(" - 'RawData'")

        return

    ###########################################################################

    def write_RawDataLog( self, data ):
        ''' Schreibt die Raw-Daten in ein Logfile '''
        thisActionName = "write_RawDataLog"

        # Daten nur Schreiben, wenn des Log-Files-Verzeichnis angegeben wurde
        if self.LogFilesPath:

            # Alles ins Log ausser "Ping"- und "Pong"-Nachrichten
            if ( ( not "PING" in data.RawData ) and ( not "PONG" in data.RawData ) and ( not "JOIN" in data.RawData ) and ( not "PART" in data.RawData ) ):

                text = str( '[' + myTime.TimeStampLog() + '] : ' + str( data.RawData ) )

                # Schreibe Daten in Logfile
                AppendDataToFile( self.RawLogFile, text )
        
        return

    def write_SubscriberDataLog( self, subtype = "", subplan = "", submonth = "", userDisplayName = "" ):
        ''' Schreibt die Subscriber-Daten in ein Logfile '''
        thisActionName = "write_SubscriberDataLog"

        tmpText = "User = {0} ( SubType = {1} | SubPlan = {2} | SubMonth = {3} )".format( 
            userDisplayName, 
            str.upper( subtype ), 
            subplan, 
            submonth 
        )
        text = str( '[' + myTime.TimeStampLog() + '] : ' + str( tmpText ) )

        # Daten nur Schreiben, wenn des Log-Files-Verzeichnis angegeben wurde
        if self.LogFilesPath:
            AppendDataToFile( self.SubscriberLogFile, text )

        return

    def write_LastSubgifterToDataLog( self ):
        ''' Letzten Subgifter in ein Logfile schreiben '''

        # Daten nur Schreiben, wenn ein LogFile-Verzeichnis angegeben wurde und
        # nicht, wenn noch kein Subgift in dieser Session vergeben wurde
        if self.LogFilesPath and not (self.LastSubGifterCounter == 0):

            tmpText = "User = {0} ( Sub-Gifts = {1} )".format( self.LastSubGifterUserName, self.LastSubGifterCounter )
            text = str( '[' + myTime.TimeStampLog() + '] : ' + str( tmpText ) )

            # Daten nur Schreiben, wenn des Log-Files-Verzeichnis angegeben wurde
            if self.LogFilesPath:
                AppendDataToFile( self.SubGifterLogFile, text )

            return "Daten im Logfile eingetragen."

        return "Kein Subgifter - keine Daten zum Schreiben."


    def write_SubGifterDataLog(self, userDisplayName):
        ''' Zählt die Anzahl der geschenkten Subs eines Users und schreibt diese in eine Datei'''

        # Subgift kommt vom gleichen User
        if self.LastSubGifterUserName == userDisplayName:
            
            # Counter erhöhen
            self.LastSubGifterCounter += 1

        # Neuer Sub-Gifter
        else:

            # Letzten Subgifter in ein Logfile schreiben
            self.write_LastSubgifterToDataLog(self)

            # Neuer UserName und Counter zurücksetzen
            self.LastSubGifterUserName = userDisplayName
            self.LastSubGifterCounter = 1

        # Daten nur Schreiben, wenn des Daten-Files-Verzeichnis angegeben wurde
        if self.DataFilesPath:

            try:
                with codecs.open( self.LatestSubsGifterFile, encoding="utf-8", mode="w") as file:
                    file.write( str( "{0}".format( userDisplayName ) ) + os.linesep + str( "({0} verschenke Subs)".format( TransformLocale_Decimals( int(self.LastSubGifterCounter) ) ) ) )
                    file.close()

            except:
                pass

        return

    def write_CheerDataLog( self, cheerAmount = 0, userDisplayName = "" ):
        ''' Schreibt die Cheer-Daten in ein Logfile '''
        thisActionName = "write_CheerDataLog"

        tmpText = "User = {0} ( Bits: {1} )".format( userDisplayName, str(cheerAmount) )
        text = str( '[' + myTime.TimeStampLog() + '] : ' + str( tmpText ) )

        # Daten nur Schreiben, wenn des Log-Files-Verzeichnis angegeben wurde
        if self.LogFilesPath:
            AppendDataToFile( self.CheerLogFile, text )

        return

    def write_LatestCheerFile( self, cheerAmount = 0, userDisplayName = "" ):
        ''' Schreibt den letzten Cheerer mit der Anzahl der Bits in ein File '''
        thisActionName = "write_LatestCheerFile"

        # Daten nur Schreiben, wenn des Daten-Files-Verzeichnis angegeben wurde
        if self.DataFilesPath:
    
            with codecs.open( self.LatestCheerFile, encoding="utf-8", mode="w") as file:
                file.write( str( "{0}".format( userDisplayName ) ) + os.linesep + str( "({0} Bits)".format( TransformLocale_Decimals(int(cheerAmount)) ) ) )
                file.close()

        return

    def write_LatestSubscriberFile( self, submonth = "", userDisplayName = "" ):
        ''' Schreibt den letzten Subscriber mit der Anzahl der Monate in ein File '''
        thisActionName = "write_LatestSubscriberFile"

        # Daten nur Schreiben, wenn des Daten-Files-Verzeichnis angegeben wurde
        if self.DataFilesPath:

            with codecs.open( self.LatestSubscriberFile, encoding="utf-8", mode="w") as file:
                file.write( str( "{0}".format( userDisplayName ) ) + os.linesep + str( "({0}. Monat)".format( TransformLocale_Decimals(int(submonth)) ) ) )
                file.close()
        
        return
    
    def write_CurrentSubgoalFile( self, subs = 0 ):
        ''' Schreibt den letzten Subscriber mit der Anzahl der Monate in ein File '''
        thisActionName = "write_LatestSubscriberFile"

        if self.DataFilesPath:

            with codecs.open( self.CurrentSubgoalCounterFile, encoding="utf-8", mode="w") as file:
                file.write( str( "{0}".format( subs ) ) )
                file.close()
        
        return

    def write_GiveawayCountFile( self, counter = 0 ):
        ''' Schreibt den letzten Subscriber mit der Anzahl der Monate in ein File '''
        thisActionName = "write_GiveawayCountFile"

        if self.DataFilesPath:

            with codecs.open( self.GiveawayCounterFile, encoding="utf-8", mode="w") as file:
                file.write( str( "{0}".format( counter ) ) )
                file.close()
        
        return

    ###########################################################################

    def Get_RawMessageData( self, data ):
        ''' Auswerten von Twitch-Meldungen Roh-Daten '''
        thisActionName = "Get_RawMessageData"
        tags = False

        # RawData auswerten
        PRIVMSG = self.rePRIVMSG.search( data.RawData )
        USERNOTICE = self.reUSERNOTICE.search( data.RawData )
        JOIN = self.reJOIN.search( data.RawData )
        WHISPER = self.reWHISPER.search( data.RawData )

        if USERNOTICE:
            ''' Nachricht ist vom Typ: USERNOTICE

                VERFÜGBARE TAGS (Allgemeine Übersicht):
                - user-id                               > User ID des Users
                - login                                 > User Name des Users
                - display-name                          > Display Name des Users
                - msg-id                                > Typ der Nachricht 
                                                          (sub, resub, charity, subgift, raid, rewardgift)
                - msg-param-months                      > Anzahl der Subs (zusammenhängend)
                - msg-param-cumulative-months           > Anzahl der Subs (insgesamt)
                - msg-param-sub-plan                    > Sub Stufe (Prime, 1000, 2000, 3000)
                - msg-param-recipient-id                > Gift Empfänger - User ID
                - msg-param-recipient-user-name         > Gift Empfänger - User Name
                - msg-param-recipient-display-name      > Gift Empfänger - Display Name
                - msg-param-profileImageURL             > Profilbild des Users

                #########################################################################
                VERFÜGBARE TAGS (Sub):
                #########################################################################
                - msg-id                                > Typ der Nachricht ("sub")
                - user-id                               > User ID des Users
                - login                                 > Benutzername des Users
                - display-name                          > DisplayName des Users
                - color                                 > Vom User festgelegte Farbe
                - msg-param-cumulative-months           > Anzahl der Subs (insgesamt)
                - msg-param-streak-months               > Anzahl der Monate in Serie
                - msg-param-sub-plan                    > Sub Stufe (Prime, 1000, 2000, 3000)

                #########################################################################
                VERFÜGBARE TAGS (Sub-Gift):
                #########################################################################
                - msg-id                                > Typ der Nachricht ("subgift")
                - user-id                               > User ID des Users
                - login                                 > Benutzername des Users
                - display-name                          > DisplayName des Users
                - color                                 > Vom User festgelegte Farbe
                - msg-param-cumulative-months           > Anzahl der Subs (insgesamt)
                - msg-param-streak-months               > Anzahl der Monate in Serie
                - msg-param-sub-plan                    > Sub Stufe (Prime, 1000, 2000, 3000)
                - msg-param-recipient-id                > UserID des Empfängers
                - msg-param-recipient-user-name         > Username des Empfängers
                - msg-param-recipient-display-name      > DisplayName des Empfängers

                #########################################################################
                VERFÜGBARE TAGS (Reward-Gift):
                #########################################################################
                - msg-id                                > Typ der Nachricht ("rewardgift")
                - user-id                               > User ID des Users
                - login                                 > Benutzername des Users
                - display-name                          > DisplayName des Users
                - color                                 > Vom User festgelegte Farbe
                - msg-param-selected-count=5
                - msg-param-total-reward-count=5
                
                #########################################################################
                VERFÜGBARE TAGS (Resub):
                #########################################################################
                - msg-id                                > Typ der Nachricht ("resub")
                - user-id                               > User ID des Users
                - login                                 > Benutzername des Users
                - display-name                          > DisplayName des Users
                - color                                 > Vom User festgelegte Farbe
                - msg-param-cumulative-months           > Anzahl der Subs (insgesamt)
                - msg-param-streak-months               > Anzahl der Monate in Serie
                - msg-param-sub-plan                    > Sub Stufe (Prime, 1000, 2000, 3000)
                
                #########################################################################
                VERFÜGBARE TAGS (Raid):
                #########################################################################
                - msg-id                                > Typ der Nachricht ("raid")
                - user-id                               > User ID des Users
                - login                                 > Benutzername des Users
                - display-name                          > DisplayName des Users
                - color                                 > Vom User festgelegte Farbe
                - msg-param-profileImageURL             > Profilbild des Users
                - msg-param-viewerCount                 > Anzahl der Viewer bei einem Raid

                #########################################################################
                VERFÜGBARE TAGS (Host):
                #########################################################################
                - msg-id                                > Typ der Nachricht ("host")
                - user-id                               > User ID des Users
                - login                                 > Benutzername des Users
                - display-name                          > DisplayName des Users
                - color                                 > Vom User festgelegte Farbe
                - msg-param-profileImageURL             > Profilbild des Users
                - msg-param-viewerCount                 > Anzahl der Viewer bei einem Raid

            '''
            # Tags auslesen
            tags = dict( re.findall( r"([^=]+)=([^;]*)(?:;|$)", USERNOTICE.group( "irctags" ) ) )

        elif PRIVMSG:
            ''' Nachricht ist vom Typ: PRIVMSG

                #########################################################################
                VERFÜGBARE TAGS:
                #########################################################################
                - user-id                               > User-ID
                - display-name                          > Display-Name des Users
                - color                                 > Vom User festgelegte Farbe
                - subscriber                            > Ist aktuell Subscriber (0 oder 1)
                - bits                                  > Aktuelle Anzahl der gecheerten Bits
                                                          !!!Nur Verfügbar, wenn auch Bits gecheert wurden!!!
            
            '''
            tags = dict( re.findall( r"([^=]+)=([^;]*)(?:;|$)", PRIVMSG.group( "irctags" ) ) )

        # elif WHISPER:
        #     '''
        #         #########################################################################
        #         VERFÜGBARE TAGS (Whisper):
        #         #########################################################################
        #         - user-id                               > User ID des Users
        #         - display-name                          > DisplayName des Users
        #         - color                                 > Vom User festgelegte Farbe

        #     '''

            #tags = dict( re.findall( r"([^=]+)=([^;]*)(?:;|$)", WHISPER.group( "irctags" ) ) )


        # elif JOIN:
        #     ''' Nachricht ist vom Typ: JOIN 
            
        #         Liefert nur den Benutzer
        #     '''
        #     tags = JOIN.group( "name" )

        else:
            ''' Es wurde keine der definierten Nachrichten-Typen gefunden '''
            #self.Logger.WriteLog( " --- RAWDATEN: {0}".format( "RAW-Daten sind nicht auswertbar" ) )
            tags = False
        
        return tags

    def Subscription_Handler( self, data ):
        ''' USERNOTICE - User hat einen Sub erhalten oder selbst gekauft

                #########################################################################
                VERFÜGBARE TAGS (Sub):
                #########################################################################
                - msg-id                                > Typ der Nachricht ("sub")
                - user-id                               > User ID des Users
                - login                                 > Benutzername des Users
                - display-name                          > DisplayName des Users
                - color                                 > Vom User festgelegte Farbe
                - msg-param-cumulative-months           > Anzahl der Subs (insgesamt)
                - msg-param-streak-months               > Anzahl der Monate in Serie
                - msg-param-sub-plan                    > Sub Stufe (Prime, 1000, 2000, 3000)

                #########################################################################
                VERFÜGBARE TAGS (Sub-Gift):
                #########################################################################
                - msg-id                                > Typ der Nachricht ("subgift")
                - user-id                               > User ID des Users
                - login                                 > Benutzername des Users
                - display-name                          > DisplayName des Users
                - color                                 > Vom User festgelegte Farbe
                - msg-param-cumulative-months           > Anzahl der Subs (insgesamt)
                - msg-param-streak-months               > Anzahl der Monate in Serie
                - msg-param-sub-plan                    > Sub Stufe (Prime, 1000, 2000, 3000)
                - msg-param-recipient-id                > UserID des Empfängers
                - msg-param-recipient-user-name         > Username des Empfängers
                - msg-param-recipient-display-name      > DisplayName des Empfängers

                #########################################################################
                VERFÜGBARE TAGS (Resub):
                #########################################################################
                - msg-id                                > Typ der Nachricht ("resub")
                - user-id                               > User ID des Users
                - login                                 > Benutzername des Users
                - display-name                          > DisplayName des Users
                - color                                 > Vom User festgelegte Farbe
                - msg-param-cumulative-months           > Anzahl der Subs (insgesamt)
                - msg-param-streak-months               > Anzahl der Monate in Serie
                - msg-param-sub-plan                    > Sub Stufe (Prime, 1000, 2000, 3000)
        '''
        thisActionName = "Subscription_Handler"

        testdata = ""

        # RawData auswerten
        USERNOTICE = self.reUSERNOTICE.search( data.RawData )

        # Basisparameter für Subgifts festlegen
        thisIsSubGift = False
        thisSubGifterName = ""
        thisDictResult = {}

        if USERNOTICE:

            # Schreibe Daten in Raw-Data-Log, wenn aktiviert
            if self.Settings.ActivateRawLog:
                self.write_RawDataLog(data=data)

            tags = dict( re.findall( r"([^=]+)=([^;]*)(?:;|$)", USERNOTICE.group( "irctags" ) ) )

            # Nachricht enthält Informationen zu einer Subscription
            if ( ( tags["msg-id"] in self.SubTypeList ) and ( tags["msg-param-sub-plan"] in self.SubPlanList ) ):
                
                # Sub von User
                if ( tags["msg-id"] == "sub" or tags["msg-id"] == "resub" ):

                    thisSubType = tags["msg-id"]
                    thisSubPlan = tags["msg-param-sub-plan"]
                    thisSubMonth = tags["msg-param-cumulative-months"]
                    
                    thisUser = tags["login"]
                    thisUserName = tags["display-name"]
                    thisIsSubGift = False
                    thisSubGifterName = False
                    
                    self.Logger.WriteLog( " !!! '{0}' WURDE ERKANNT: ( SubPlan = '{1}' - User = '{2}' ( {3}. Monat ) )".format(
                        thisSubType, 
                        thisSubPlan, 
                        thisUserName, 
                        str(thisSubMonth) ) 
                    )
                    self.write_SubscriberDataLog(
                        userDisplayName = thisUserName, 
                        subtype = thisSubType, 
                        subplan = thisSubPlan, 
                        submonth = str(thisSubMonth)
                    )
                
                # Ist ein Gifted Sub
                elif ( tags["msg-id"] == "subgift" ):

                    thisSubType = tags["msg-id"]
                    thisSubPlan = tags["msg-param-sub-plan"]
                    thisSubMonth = tags["msg-param-months"]

                    thisUser = tags["msg-param-recipient-user-name"]
                    thisUserName = tags["msg-param-recipient-display-name"]
                    thisIsSubGift = True
                    thisSubGifterName = tags["login"]

                    self.Logger.WriteLog( " !!! '{0}' WURDE ERKANNT: ( SubPlan = '{1}' - User = '{2}' ( {3}. Monat ) ) von User = '{4}'".format( 
                        str.upper( thisSubType ), 
                        str(thisSubPlan), 
                        thisUserName, 
                        str(thisSubMonth), 
                        thisSubGifterName ) 
                    )
                    self.write_SubscriberDataLog( 
                        userDisplayName = thisUserName, 
                        subtype = thisSubType, 
                        subplan = thisSubPlan, 
                        submonth = thisSubMonth 
                    )

                    # Daten des Subgifters in Datei schreiben
                    self.write_SubGifterDataLog(userDisplayName=self.Parent.GetDisplayName(thisSubGifterName))

                # Nur ausführen, wenn die CounterDB bei der Initialisierung übergeben wurde
                if self.CounterDB:
                    counterValue = self.CounterDB.increase_CounterValue( "SubCounter" )
                
                    # Counter für Subgoal erhöhen
                    if int( counterValue ) == int( self.Settings.Raffle_GiveAwaySubGoal ):
                        self.CounterDB.increase_CounterValue( "GiveAwayCounter" )
                        self.CounterDB.reset_CounterValue( "SubCounter" )

                # Aktuelle Subscriber Daten in File schreiben
                self.write_LatestSubscriberFile( 
                    userDisplayName = thisUserName, 
                    submonth = str(thisSubMonth) 
                )
                
                # Nur ausführen, wenn die CounterDB bei der Initialisierung übergeben wurde
                if self.CounterDB:
                    self.write_CurrentSubgoalFile( subs = self.CounterDB.get_Value( "SubCounter" ) )
                    self.write_GiveawayCountFile( counter = self.CounterDB.get_Value( "GiveAwayCounter" ) )

                # Daten in Dict aufnehmen
                thisDictResult = {
                    "UserName": thisUser,
                    "UserDisplayName": thisUserName,
                    "IsSubGift": thisIsSubGift,
                    "SubGifterName": thisSubGifterName,
                    "SubPlan": thisSubPlan
                }

                # Daten an Funktion zurückliefern
                return thisDictResult
                
            else:
                ''' Enthält keine Informationen zu Subscribtions '''
                return False
        else:
            ''' Ist nicht vom Typ USERNOTICE '''
            return False

    def Join_Handler( self, data ):
        ''' Ein User hat den Chat betreten '''
        thisActionName = "Subscription_Handler"
        tmpTestMessage = ":nachtmeisterbot!nachtmeisterbot@nachtmeisterbot.tmi.twitch.tv JOIN #nachtmeister666"

        JOIN = self.reJOIN.search( data.RawData )

        if JOIN:
            tag = JOIN.group( "name" )
            UserDisplayName = self.Parent.GetDisplayName( tag )

            return UserDisplayName

        return False

    def Cheer_Handler( self, data=False, rawmessage=False ):
        ''' Raw Daten auswerten, ob es sich um einen Cheer handelt '''
        thisActionName = "Cheer_Handler"
        tags = False

        # RawData auswerten
        if data:
            PRIVMSG = self.rePRIVMSG.search( data.RawData )
        
        elif rawmessage:
            PRIVMSG = self.rePRIVMSG.search( rawmessage )
        
        else:
            return False

        if PRIVMSG:
            tags = dict( re.findall( r"([^=]+)=([^;]*)(?:;|$)", PRIVMSG.group( "irctags" ) ) )

            # self.Logger.WriteLog(" {0} - CHEER DATA: {1}".format(
            #     thisActionName,
            #     str(tags))
            # )

            try:
                # PRIVMSG ist ein Cheer
                if tags["bits"]:

                    # Aktuelle Daten in Files schreiben
                    self.write_LatestCheerFile( userDisplayName = tags["display-name"], cheerAmount = int(tags["bits"]) )
                    self.write_CheerDataLog( userDisplayName = tags["display-name"], cheerAmount = int(tags["bits"]) )

                    return tags

            except:
                # PRIVMSG ist kein Cheer

                # self.Logger.WriteLog(message_text = " {0} - ERROR: {1}".format(
                #     thisActionName,
                #     str(sys.exc_info()))
                # )

                return False


