# Greening the Spark Grid Control System
# Module: Suopervisor interface
# Version 2.0
# Date: 10/03/2022
# Author Carl Nicholson

# Change log
# 27/01/22 Release of V2 for development

# To do list - also search for "TBD"s

# Import standard libraries
#import sys
#import csv
from os import path, listdir
#from dataclasses import dataclass, field
#from typing import List
#from math import pi, sin
#from random import uniform
import datetime as dt
import time as t
import keyboard

# Set GTS filepath & platform
#if sys.platform == 'win32':
#    GTS_FILEPATH = "D:\Projects\Greening the Spark\GTS" # Set windows PC pathname
#    GTS_PLATFORM = "PC"
#else:
#    GTS_FILEPATH = r'/home/pi/Desktop/GTS' # set RPi pathname
#    GTS_PLATFORM = "RPi"

# Import GTS libraries
import gts_lib
import gts_lib.logbook as logbook
import gts_lib.gts_maths as maths
import gts_lib.gts_utilities as utils
import gts_lib.device_drivers as dd
#from gts_lib.gts_globals import * # treated as local variables & methods by all modules

DEBUG = False
app = "super"
procedure = "init"

# Set variables & constants
procedure = "superVIF"

# Methods

def getConfiguration(GTS_FILEPATH):   
    # get configuration

        config_dir = path.join(GTS_FILEPATH, "gts_databases", "configurations")
        config_files = listdir(config_dir)
        print("§ Choose configuration from one of the following: ")
        for file_number in range(len(config_files)):
            print("§    " + str(file_number+1) + ": " + config_files[file_number])
        file_number = utils.intRangeCheck("Type number required: ", [1, len(config_files)]) # interactive mode
        # file_number = 1  # autostart mode
        # print("§ File choice set to 1 by autostart.")
        configuration_file = config_files[file_number-1]
        logbook.writeLog("Info", app, procedure, "Configuration file set to " + configuration_file + ".")
        return configuration_file
    
def getDifficulty(AUTO_SUPERVISOR, AUTO_SUPERVISOR_DIFFICULTY, MAX_DIFFICULTY):
        # get difficulty level
        #print("§ getDiff", P)
        #print("§ getDiff <simulation>", P["simulation"])
        #print("§ getDiff <simulation><AUTO_SUPERVISOR>", P["simulation"].parameters["AUTO_SUPERVISOR"])
        if AUTO_SUPERVISOR:
            difficulty = AUTO_SUPERVISOR_DIFFICULTY
        else:
            difficulty = utils.intRangeCheck("Choose difficulty level: ", [0, MAX_DIFFICULTY])
        logbook.writeLog("Info", app, procedure, "Difficulty level set to " + str(difficulty) + ".")
        return difficulty

def getSimStartTime(AUTO_SUPERVISOR, AUTO_SUPERVISOR_START_TIME_OPTION, TODAY_MIDNIGHT, FIRST_SAMPLE_TIME, LAST_SAMPLE_TIME):
    # choose when to start in the timeline
    today = dt.datetime.today()
        #TOTAL_SAMPLES = len(TimeLine)
        #FIRST_SAMPLE_TIME = OperationalTimelines.Timelines_baseline["time"][0]
        #print("§ supervisor: first sample time", FIRST_SAMPLE_TIME)
        #LAST_SAMPLE_TIME = OperationalTimelines.Timelines_baseline["time"][TOTAL_SAMPLES-1]

    if AUTO_SUPERVISOR:
        start_time_choice = AUTO_SUPERVISOR_START_TIME_OPTION
    else:            
        start_time_choice = utils.intRangeCheck("Choose start time: beginning = 0, now = 1, any time = 2: ", [0,2])       
    if start_time_choice == 0:      # at the beginning
        sim_start_time = TODAY_MIDNIGHT + FIRST_SAMPLE_TIME
    elif start_time_choice == 1:    # or the actual time of day
        sim_start_time = dt.datetime.now()
    elif start_time_choice == 2:    # or time of choice
        print("§ Times between", FIRST_SAMPLE_TIME, "and", LAST_SAMPLE_TIME)
        start_time_hour = utils.intRangeCheck("Choose hour (0-23): ", [0, 23])
        start_time_minute = utils.intRangeCheck("Choose minute (0-59): ", [0, 59])
        time_of_day = dt.timedelta(hours = start_time_hour, minutes = start_time_minute)
            
        if (FIRST_SAMPLE_TIME <= time_of_day <= LAST_SAMPLE_TIME):
            sim_start_time = TODAY_MIDNIGHT + time_of_day
        else:
            print("Invalid start time", str(time_of_day), "(last chance!), select times between", str(FIRST_SAMPLE_TIME), "and", str(LAST_SAMPLE_TIME))
            start_time_hour = utils.intRangeCheck("Choose hour (0-23): ", [0, 23])
            start_time_minute = utils.intRangeCheck("Choose minute (0-59): ", [0, 59])        
            time_of_day = dt.timedelta(hours = start_time_hour, minutes = start_time_minute)
            if (FIRST_SAMPLE_TIME <= time_of_day <= LAST_SAMPLE_TIME):
                sim_start_time = TODAY_MIDNIGHT + time_of_day
            else:
                logbook.writeLog("ERROR", app, procedure, "Invalid simulation start time " + str(sim_start_time) + ", simulation aborted.")    
                
    logbook.writeLog("Info", app, procedure, "Simulation start time set to " + str(sim_start_time))
    return sim_start_time
        
def getSimRunTime(P, SIM_START_TIME):
    # choose how long the sim runs for
    if P("simulation", "AUTO_SUPERVISOR"):
        sim_run_time_days = P("simulation", "AUTO_SUPERVISOR_RUN_TIME_DAYS")
        sim_run_time_hours = P("simulation", "AUTO_SUPERVISOR_RUN_TIME_HOURS")
        sim_run_time_minutes = P("simulation", "AUTO_SUPERVISOR_RUN_TIME_MINUTES")
    else:
        sim_run_time_days = utils.intRangeCheck("§ Set number of days sim will run for (0-364): ", [0, 364])
        sim_run_time_hours = utils.intRangeCheck("§ Set further hours sim will run for (0-23): ",  [0, 23])
        sim_run_time_minutes = utils.intRangeCheck("§ Set further minutes sim will run for (0-59): ",  [0, 59])
        
    logbook.writeLog("Info", app, procedure, "Simulation run time set to " + str(sim_run_time_days) + " days " + str(sim_run_time_hours) + " hours and " + str(sim_run_time_minutes) + " minutes.")
    sim_run_time = dt.timedelta(days = sim_run_time_days,hours = sim_run_time_hours, minutes = sim_run_time_minutes)
    sim_end_time = SIM_START_TIME + sim_run_time
    logbook.writeLog("Info", app, procedure, "Simulation end time set to " + str(sim_end_time))
    return sim_run_time, sim_end_time

    if DEBUG:
        print("FRAME_INTERVAL_SECONDS {}, SIM_CYCLE_INTERVAL {}".format(FRAME_INTERVAL_SECONDS, SIM_CYCLE_INTERVAL))
        print ("§ SIM_START_TIME", SIM_START_TIME.strftime("%Y-%m-%d %H:%M:%S"), "SIM_END_TIME", SIM_END_TIME.strftime("%Y-%m-%d %H:%M:%S"))


def handleKeyboardInterrupt():
    key = "none"
    name = "none"
    if keyboard.is_pressed(57):
        print()
        print("§ supervisor: Run time menu options")
        print("§ ")
        print("§          0: End simulation")
        print("§          1: Change fossil fuels power output")
        print("§          2: Change nuclear power output")
        #print("§ 2: second option")

        choice = input("§ supervisor: Type required option: ")       

        if choice == "1":
            name = "FOSSIL_FUELS_READING"
            key = float(input("§ Change fossil_fuels power output (as %) to : "))
            #print("§ supervisor: Fossil fuels output changed to", str(key))
            print("§ supervisor: Resuming simulation...  (press <spacebar> for runtime options)")

        elif choice == "2":
            name = "NUCLEAR_READING"
            key = float(input("§ Change nuclear power output (as %) to: "))
            #print("§ supervisor: Nuclear power output changed to", str(key))
            print("§ supervisor: Resuming simulation...  (press <spacebar> for runtime options)")

        else :
            print("§ supervisor: Ending simulation.")
            name = "key"
            key = "x" 

    elif keyboard.is_pressed("x"):
        print("§ supervisor: Ending simulation.")
        name = "x"
        key = "x"
    return name, key
        
# Main code

procedure = "main"
    
if __name__ == "__main__":
    logbook.closeLog()
