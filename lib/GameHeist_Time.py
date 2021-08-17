#!/usr/bin/python2
# -*- coding: utf-8 -*-
# pylint: disable=all

#------------------------------------------------------
# Import der Libraries
#------------------------------------------------------
from time import localtime, strftime, time
import datetime
from datetime import datetime as dt

#------------------------------------------------------
# Verschiedene Funktionen
#------------------------------------------------------
def TimeStamp():
    timestamp = str ( strftime('%H:%M:%S') )
    return timestamp

def TimeStampLog():
    timestamp = str ( strftime('%Y-%m-%d | %H:%M:%S') )
    return timestamp

def FileTimeStamp():
    timestamp = str ( strftime('%Y%m%d_%H%M%S') )
    return timestamp

def FileTimeStampDate():
    timestamp = str ( strftime('%Y%m%d') )
    return timestamp

def TimeStampDBEntry():
    timestamp = str ( strftime('%Y-%m-%d %H:%M:%S') )
    return timestamp

def TimeStampSubtractMinutes( minutes ):
    now = datetime.datetime.now()
    seconds = int( minutes ) * 60
    
    activeTime = now - datetime.timedelta(seconds=seconds)
    return activeTime.strftime('%Y-%m-%d %H:%M:%S')

def Time_UpdateTickMinutes( minutes ):
    now = datetime.datetime.now()
    timestamp = now - datetime.timedelta( minutes=minutes )
    return timestamp

def Time_UpdateTickMinutesUTC( minutes ):
    now = datetime.datetime.utcnow()
    timestamp = now - datetime.timedelta( minutes=minutes )
    return timestamp

def Time_UpdateTickSeconds( seconds ):
    now = datetime.datetime.now()
    timestamp = now - datetime.timedelta( seconds=seconds )
    return timestamp

def Time_TimestampInSecondsEpoch():
    ''' Zeitstempel in Sekunden '''
    return int(time())

def ChangeDateTimeFormat( timeStamp ):
    ''' Umwandeln des TimeDate Formates '''
    
    try:
        date_time_obj = dt.strptime(timeStamp, '%Y-%m-%d %H:%M:%S')
        newTimeStamp = date_time_obj.strftime('%d.%m.%Y %H:%M:%S')
    except:
        newTimeStamp = timeStamp
        
    return newTimeStamp

def ChangeDateTimeFormatShort( timeStamp ):
    ''' Umwandeln des TimeDate Formates '''
    
    try:
        date_time_obj = dt.strptime(timeStamp, '%Y-%m-%d %H:%M:%S')
        newTimeStamp = date_time_obj.strftime('%d.%m.%Y')
    except:
        newTimeStamp = timeStamp
        
    return newTimeStamp

def ChangeDateFormat( timeStamp ):
    ''' Umwandeln des TimeDate Formates '''
    
    try:
        date_time_obj = dt.strptime(timeStamp, '%Y-%m-%d %H:%M:%S')
        newTimeStamp = date_time_obj.strftime('%d.%m.%Y')
    except:
        newTimeStamp = timeStamp
        
    return newTimeStamp
    
def TimePrettyFormatString( seconds ):
    seconds = int(seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    
    if days == 1:
        strDays = "Tag"
    else:
        strDays = "Tage"
        
    if hours == 1:
        strHours = "Stunde"
    else:
        strHours = "Stunden"
    
    if minutes == 1:
        strMinutes = "Minute"
    else:
        strMinutes = "Minuten"
        
    if seconds == 1:
        strSeconds = "Sekunde"
    else:
        strSeconds = "Sekunden"
    
    if days > 0:        
        return '%d {0} %d {1} %d {2} %d {3}'.format(strDays, strHours, strMinutes, strSeconds) % (days, hours, minutes, seconds )
    elif hours > 0:
        return '%d {0} %d {1} %d {2}'.format(strHours, strMinutes, strSeconds) % (hours, minutes, seconds )
    elif hours > 0 and minutes > 0 and seconds == 0:
        return '%d {0} %d {1}'.format(strHours, strMinutes) % (hours, minutes )
    elif hours > 0 and minutes == 0 and seconds > 0:
        return '%d {0} %d {1}'.format(strHours, strSeconds) % (hours, seconds )
    elif hours > 0 and minutes == 0 and seconds == 0:
        return '%d {0}'.format(strHours) % (hours, )
    elif minutes > 0 and seconds == 0:
        return '%d {0}'.format(strMinutes) % (minutes,)
    elif minutes > 0:
        return '%d {0} %d {1}'.format(strMinutes, strSeconds) % (minutes, seconds )
    else:
        return '%d {0}'.format(strSeconds) % (seconds, )
    
#------------------------------------------------------
#	Helper Functinos
#--------------------------------------		
def ConvertDatetimeToEpoch( datetimeObject=datetime.datetime.now() ):
	# converts a datetime object to seconds in python 2.7
	return time.mktime(datetimeObject.timetuple())

def AddSecondsToDatetime( datetimeObject, seconds ):
	# returns a new datetime object by adding x seconds to a datetime object
	return datetimeObject + datetime.timedelta(seconds=seconds)

def ConvertEpochToDatetime( seconds=0 ):
	# 0 seconds as input would return 1970, 1, 1, 1, 0
	seconds = max(0, seconds)
	return datetime.datetime.fromtimestamp(seconds)

def ConvertDateToDayName( datetimeObject ):
    # Gibt den Namen des Tages aus dem übermittelten Datum zurück
    dayname = ""
    daynumber = int(datetimeObject.strftime("%w"))

    if daynumber == 0:
        dayname = "Sonntag"
    elif daynumber == 1:
        dayname = "Montag"
    elif daynumber == 2:
        dayname = "Dienstag"
    elif daynumber == 3:
        dayname = "Mittwoch"
    elif daynumber == 4:
        dayname = "Donnerstag"
    elif daynumber == 5:
        dayname = "Freitag"
    elif daynumber == 6:
        dayname = "Samstag"

    return dayname

