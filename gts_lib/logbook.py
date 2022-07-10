# Greening the Spark Grid Control System
# Module: Logbook
# Version 2.0
# Date: 03/03/2022
# Author Carl Nicholson
#
# Change log
# 27/01/22 Release of V2 for development
#
# To do list - search for "TBD"
#
# Usage
# syntax: writeLog(level, app, procedure, message)
# example:
# writeLog("ERROR", "Logbook", "Usage", "Test message2") - will abort the sim
# close logfile before exiting app with closeLog()

# Import standard libraries
import time
import datetime
import sys

# Set GTS filepaths; must be set independently because cannot load globals
if sys.platform == 'win32':
    gts_filepath = "D:\Projects\Greening the Spark\GTS" #WindowsPC
    logbook_settings_filepath = gts_filepath + "\\gts_databases\\logbook_settings\\"
    logbook_filepath = gts_filepath + "\\gts_databases\\logs\\"
    import winsound
else:
    gts_filepath = r'/home/pi/Desktop/GTS' # set RPi pathname
    logbook_settings_filepath = gts_filepath + r'/gts_databases/logbook_settings/'
    logbook_filepath = gts_filepath + r'/gts_databases/logs/'

# Import GTS libraries
import gts_lib

app = "logbook"
procedure = "init"
DEBUG = False

# reporting level
levels = {"NONE": 0, "ERROR" : 1, "Warning" : 2, "Info" : 3, "ALL" : 5}
logs_level_screen = levels["Warning"]
logs_level_file = levels["Warning"]
logs_screen = logs_level_screen > 0
logs_file = logs_level_file > 0

print("§ Logbook: starting logbook; initial settings screen:", logs_level_screen, "file:",  logs_level_file)

def resetLogfileSettings(screen, file):
    globals()["logs_level_screen"] = levels[screen]
    globals()["logs_level_file"] = levels[file]
    globals()["logs_screen"] = logs_level_screen > 0
    globals()["logs_file"] = logs_level_file > 0
    if DEBUG: print("§ Logbook: resetting logbook settings to", screen, file)

if DEBUG: print("§ Logbook: level values for screen and file set to", logs_level_screen, logs_level_file)

timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
#print(timestamp)

if logs_file:
    logfile = logbook_filepath + timestamp + ".log"
#print(logfile)

logfile_entry = "[Log " + timestamp + "] <Info> <Logbook> <init> Logbook initialised."

if logs_level_screen < levels["Warning"]: # screen
    print(logfile_entry)
        
if logs_level_file > 0: # file
    if logs_level_screen < levels["Warning"]: # screen
        print("§ logbook: opening logfile")
    f = open(logfile, "a")

if logs_level_file < levels["Warning"]:
    logfile_entry += "\n"
    f.write(logfile_entry)

def beeps():
    if sys.platform == 'win32':
        winsound.Beep(440,100)
        time.sleep(0.2)
        winsound.Beep(440,100)
        time.sleep(0.1)
        winsound.Beep(440,100)
        time.sleep(0.1)

    else:
        print('\a')
        time.sleep(0.2)
        print('\a')
        time.sleep(0.1)
        print('\a')
        time.sleep(0.1)

def writeLog(message_type, from_app, from_procedure, message):
    
    procedure = "writeLog"
    now = datetime.datetime.now()
    logfile_entry = "[Log " + now.strftime("%Y/%m/%d %X") + "] <" + message_type + "> <" + from_app + "> <" + from_procedure +"> " + message

    if message_type == "Info":
        level = levels["Info"]
    elif message_type == "ERROR":
        level = levels["ERROR"]
    elif message_type == "Warning":
        level = levels["Warning"]
    else:
        message_type = "unknown"
        level = levels["Warning"]

    #print("§ logs: level, logs_level_screen", level, logs_level_screen)
    if level <= logs_level_screen: # screen
        print(logfile_entry)
    
    if level <= logs_level_file: # file
        logfile_entry += "\n"
        f.write(logfile_entry)
        
    if message_type == "Warning":
        choice = input("§ Warning issued, continue (y) or abort (any other character)? ")
        if choice == "y":
            writeLog("Info", app, procedure, "Warning overridden, sim resuming.")
        else:
            writeLog("Info", app, procedure, "Warning heeded, sim aborted.")
            closeLog()
            sys.exit() 

    elif message_type == "ERROR":
        writeLog("Info", app, procedure, "Fatal error, sim aborted.")
        closeLog()        
        beeps()
        sys.exit()   
        
    elif message_type == "unknown":
        writeLog("Warning", app, procedure, "Unknown error type, sim aborted.")
        closeLog()
        sys.exit()

def closeLog():
    if logs_file: #file
        print("§ logbook: closing logfile")
        writeLog("Info", "logbook", "closeLog", "Closing logfile. That's all folks - don't forget to turn out the lights!")
        f.close()
        print("§ Logbook: simulation shutdown successful.")

