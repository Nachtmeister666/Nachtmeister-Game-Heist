#!/usr/bin/python2
# -*- coding: utf-8 -*-
# pylint: disable=all

#------------------------------------------------------
# Import der Libraries
#------------------------------------------------------
import sys
import locale
import codecs
import os
from GameHeist_Time import TimePrettyFormatString

#------------------------------------------------------
# Klasse
#------------------------------------------------------
class CoolDownHelper(object):
    ''' Funktionen für den Umgang mit Cooldown Objekten '''
    def __init__( self, parent, logger, debug = False ):
        self.ClassName = "CoolDownHelper"
        thisActionName = "__init__"
        self.Parent = parent
        self.Logger = logger
        self.Debug = debug
        
        self.Logger.WriteLog( " - '{0}' geladen".format(self.ClassName))

    def IsOnCooldown( self, scriptname, command ):
        '''Globalen Cooldown abfragen'''
        
        thisActionName = "IsOnCooldown"
        thisResponse = False
        
        if self.Parent.IsOnCooldown( scriptname, command.lower() ):
            thisResponse = True

        if ( self.Debug ):
            self.Logger.WriteDebug( command, "Kommando im globalen Cooldown? - {0}".format(thisResponse))
            
        # self.Logger.WriteLog( command + ": Kommando im globalen Cooldown? - {0}".format(thisResponse))
        
        return thisResponse

    def IsOnUserCooldown( self, scriptname, command, user ):
        '''Cooldown für User abfragen'''
        thisActionName = "IsOnCooldown"
        UserDisplayName = self.Parent.GetDisplayName( user )
        thisResponse = False
        
        if self.Parent.IsOnUserCooldown( scriptname, command.lower(), user ):
            thisResponse = True

        if ( self.Debug ):
            self.Logger.WriteDebug( command, "User '{0}' im Cooldown? - {1}".format(UserDisplayName,
                                                                                    thisResponse))
            
        # self.Logger.WriteLog( command + ": User '{0}' im Cooldown? - {1}".format(UserDisplayName,
        #                                                                          thisResponse))
        
        return thisResponse

    def AddCooldown( self, scriptname, command, cooldownTime ):
        '''Globalen Cooldown setzen'''
        thisActionName = "AddCooldown"
        
        self.Parent.AddCooldown( scriptname, command.lower(), cooldownTime )
        
        if ( self.Debug ):
            self.Logger.WriteDebug( command, "Setze globalen Cooldown auf {0}.".format( TimePrettyFormatString(int( cooldownTime ) ) ) )
            
        self.Logger.WriteLog( command + ": Setze globalen Cooldown auf {0}.".format( TimePrettyFormatString(int( cooldownTime ) ) ) )
        
        return

    def AddUserCooldown( self, scriptname, command, user, cooldownTime ):
        '''Cooldown für User setzen'''
        thisActionName = "AddUserCooldown"
        UserDisplayName = self.Parent.GetDisplayName( user )
        
        self.Parent.AddUserCooldown( scriptname, command.lower(), user, int(cooldownTime) )
        
        if ( self.Debug ):
            self.Logger.WriteDebug( command, "Setze Cooldown für User '{0}' ({1}).".format(UserDisplayName, TimePrettyFormatString(int( cooldownTime ) ) ) )
        
        self.Logger.WriteLog( command + ": Setze Cooldown für User '{0}' ({1}).".format(UserDisplayName, TimePrettyFormatString(int( cooldownTime ) ) ) )
        
        return
    
    def GetUserCooldownDuration( self, scriptname, command, user ):
        ''' Zeit für Cooldown '''
        thisActionName = "GetUserCooldownDuration"
        seconds = self.Parent.GetUserCooldownDuration( scriptname, command, user )
        
        return seconds

    def GetCooldownDuration( self, scriptname, command ):
        ''' Zeit für Cooldown '''
        thisActionName = "GetUserCooldownDuration"
        seconds = self.Parent.GetCooldownDuration( scriptname, command )
        
        return seconds

#------------------------------------------------------
# Klasse
#------------------------------------------------------
class ChatbotMessages( object ):
    ''' Schreibt definierte Nachrichten in den Twitch-Chat '''
    def __init__( self, parent, logger, cooldown, debug = False ):
        self.ClassName = "ChatbotMessages"
        thisActionName = "__init__"
        self.Parent = parent
        self.ScriptName = ""
        self.CoolDown = cooldown
        self.Logger = logger
        self.Debug = debug
        self.CurrencyName = self.Parent.GetCurrencyName()
    
        self.Logger.WriteLog( " - '{0}' geladen".format(self.ClassName))
    
    def WriteChatMessage_UserCooldownDuration( self, scriptname, user, command, commandName = False ):
        ''' Schreibe eine Nachricht bezüglich des Cooldowns in den Chat '''
        thisActionName = "WriteChatMessage_UserCooldownDuration"
        
        if commandName:
            self.CommandName = commandName
        else:
            self.CommandName = command
        
        self.ScriptName = scriptname
        UserDisplayName = self.Parent.GetDisplayName( user )
        CoolDownDuration = str( TimePrettyFormatString( self.CoolDown.GetUserCooldownDuration( self.ScriptName, command, user ) ) )
        
        self.Parent.SendStreamMessage( "/me : 💤 {0}, du musst noch {1} warten bis du das Kommando '{2}' erneut aufrufen kannst. 💤".format( UserDisplayName, CoolDownDuration, self.CommandName ) )
        return
    
    def WriteChatMessage_GlobalCooldownDuration( self, scriptname, user, command, commandName = False ):
        ''' Schreibe eine Nachricht bezüglich des Cooldowns in den Chat '''
        thisActionName = "WriteChatMessage_GlobalCooldownDuration"
        
        # auf Grund Kompatibilität
        if commandName:
            self.CommandName = commandName
        else:
            self.CommandName = command
        
        self.ScriptName = scriptname
        UserDisplayName = self.Parent.GetDisplayName( user )
        CoolDownDuration = str( TimePrettyFormatString( self.CoolDown.GetCooldownDuration( self.ScriptName, command ) ) )
        
        self.Parent.SendStreamMessage( "/me : 💤 {0}, das Kommando '{2}' ist noch für {1} im Cooldown. 💤".format(UserDisplayName, 
                                                                                                                   CoolDownDuration, 
                                                                                                                   self.CommandName ) )
        
        return

    def WriteChatMessage_NoPermission( self, user, command, commandName = False ):
        ''' Schreibe eine Nachricht bezüglich mangelnder Zugriffsrechte in den Chat '''
        thisActionName = "WriteChatMessage_NoPermission"
        UserDisplayName = self.Parent.GetDisplayName( user )
        
        # auf Grund Kompatibilität
        if commandName:
            self.CommandName = commandName
        else:
            self.CommandName = command
        
        self.Parent.SendStreamMessage( "/me : ⛔ {0}, du hast nicht die erforderlichen Rechte für das Kommando '{1}'. ⛔".format(UserDisplayName, 
                                                                                                                                  self.CommandName ) )
        
        
        return
    
    def WriteChatMessage_NotEnoughPoints( self, user, gameCost, command, commandName = False ):
        ''' Schreibe eine Nachricht bezüglich mangelnder Punkte in den Chat '''
        thisActionName = "WriteChatMessage_NotEnoughPoints"
        thisUserDisplayName = self.Parent.GetDisplayName( str.lower( user ) )
        thisUserCurrentPoints = int( self.Parent.GetPoints( str.lower( user ) ) )
        
        
        # auf Grund Kompatibilität
        if commandName:
            self.CommandName = commandName
        else:
            self.CommandName = command
        
        self.Parent.SendStreamMessage( "/me : 😟 Tut mir Leid {0}, aber du hast nicht die erforderlichen {2} {3} für das Kommando '{1}'. 😟".format(thisUserDisplayName, 
                                                                                                                                                     self.CommandName,
                                                                                                                                                     gameCost,
                                                                                                                                                     self.CurrencyName ) )
        
        
        return

#------------------------------------------------------
# Weitere Funktionen
#------------------------------------------------------    
def CheckUserPermission( parent, user ):
    ''' Liefere Informationen zu der User Berechtigung '''
    thisActionName = "CheckUserPermission"
    
    if parent.HasPermission( user, "Caster", ""):
        return "64"
    
    if parent.HasPermission( user, "Editor", ""):
        return "32"
    
    if parent.HasPermission( user, "Moderator", ""):
        return "16"
    
    if parent.HasPermission( user, "VIP", ""):
        return "8"
    
    if parent.HasPermission( user, "Subscriber", ""):
        return "4"
    
    if parent.HasPermission( user, "Regular", ""):
        return "2"
    
    else:
        return "1"
    
def StreamIsLive( parent ):
    thisActionName = "StreamIsLive"
    thisResponse = False
    
    if parent.IsLive():
        thisResponse = True
        
    return thisResponse

def CheckIfInteger( toCheck ):
    thisActionName = "CheckIfInteger"
    thisResponse = False
    
    try:
        integer = int(toCheck)
        thisResponse = True
    except Exception as e:
        thisResponse = False
    
    return thisResponse

# ---------------------------------------------
# Tausender Trennzeichen
# ---------------------------------------------  
def TransformLocale_Decimals( Number ):
    locale.setlocale(locale.LC_ALL, '')
    return locale.format('%d', Number, 1)

# ---------------------------------------------
# Ersetzen von Rechts
# ---------------------------------------------     
def ReplaceFromRight( source, target, replacement, replacements=None ):
    return replacement.join( source.rsplit( target, replacements ) )

# ---------------------------------------------
# Daten in/von Text-Dateien
# ---------------------------------------------     
def ReadDatafromFile( file ):
    ''' Auslesen von Daten aus einer Datei '''
    thisActionName = "ReadDatafromFile"

    try:
        with codecs.open( file, encoding="utf-8", mode="r") as f:
            text = f.read()
            f.close()
    except:
        return False

    return text
  
def WriteDataToFile( file, text ):
    ''' Schreibe Text in eine Datei und überschreibe den bestehenden Inhalt '''
    thisActionName = "WriteDataToFile"

    try:
        with codecs.open( file, encoding="utf-8", mode="w") as f:
            text = f.write( str( text ) )
            f.close()
    except:
        return False

    return True

def AppendDataToFile( file, text ):
    ''' Füge Text in eine Datei am Ende hinzu '''
    thisActionName = "AppendDataToFile"

    try:
        with codecs.open( file, encoding="utf-8", mode="a") as f:
            text = f.write( str( text ) + os.linesep )
            f.close()
    except:
        return False

    return True
        