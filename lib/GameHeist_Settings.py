#!/usr/bin/python2
# -*- coding: utf-8 -*-
# pylint: disable=all

#------------------------------------------------------
# Import der Libraries
#------------------------------------------------------
import os
import codecs
import json

#------------------------------------------------------
# Klasse
#------------------------------------------------------
class CustomSettings(object):
    ''' Die für das Skript notwendigen Einstellungen laden und speichern '''
    
    def __init__(self, settingsfile=None):
        self.ScriptName = "Settings"
        try:
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
                self.__dict__ = json.load(f, encoding="utf-8")
        except:

            # Global
            self.ActivateExtention = True
            self.OnlyLive = False
            # Game
            self.Game_Command = "!run"
            self.Game_Command_Permission = "Everyone"
            # Game-Settings
            self.Game_Settings_MinStake = int(1)
            self.Game_Settings_MaxStake = int(50000)
            self.Game_Result_Multiplier = float(2.0)
            self.Game_Cooldown_Time = int(300)
            self.Game_UntilStart_Time = int(300)
            self.Game_Min_Participant = int(1)
            # Log
            self.ActivateLog = False

        
        return
            
    def Reload(self, jsondata):
        """ Reload settings from Streamlabs user interface by given json data. """
        self.__dict__ = json.loads(jsondata, encoding="utf-8",
                          ensure_ascii=False)

        return

    def Save(self, settingsfile):
        """ Save settings contained within to .json and .js settings files. """
        try:
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="w+") as f:
                json.dump(self.__dict__, f, encoding="utf-8",
                          ensure_ascii=False)
            with codecs.open(settingsfile.replace("json", "js"), encoding="utf-8-sig", mode="w+") as f:
                f.write("var settings = {0};".format(json.dumps(
                    self.__dict__, encoding='utf-8', ensure_ascii=False)))
        except:
            Parent.Log(self.ScriptName, "Failed to save settings to file.")