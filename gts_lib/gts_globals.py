# Greening the Spark Grid Control System
# Module: Globals
# Version 2.0
# Date: 14/03/2022
# Author Carl Nicholson

# Change log
# 27/01/22 Release of V2 for development

# To do list - also search for "TBD"s
# TBD Make reports a class

# Import standard libraries
import sys
import csv
from os import path, listdir
from dataclasses import dataclass, field
from typing import List
from math import pi, sin
from random import uniform
import datetime as dt
import time as t

# Set GTS filepath, platform and hardware
if sys.platform == 'win32':
    GTS_FILEPATH = "D:\Projects\Greening the Spark\GTS" # Set windows PC pathname
    GTS_PLATFORM = "PC"
else:
    GTS_FILEPATH = r'/home/pi/Desktop/GTS' # set RPi pathname
    GTS_PLATFORM = "RPi"
    
# Import GTS libraries
import gts_lib
import gts_lib.logbook as logbook
import gts_lib.gts_maths as maths
import gts_lib.gts_utilities as utils
import gts_lib.supervisor as supervisor
#import reports

DEBUG = False
app = "globals"
procedure = "init"
logbook.writeLog("Info", app, procedure, "Platform set to: " + GTS_PLATFORM + ".")

# Set project global variables & constants
ON = 1
OFF = 0

ITEMS_PER_LINE = 4 # for traceback dump formatting
CONFIGURATION_TYPES = ["timelines", "configurations", "logbook_settings", "simulation", "models", "calibrations", "scale_factors", "initial_conditions", "reports"]
STATIC_MODELS = ("wind","solar","demand")
DYNAMIC_MODELS = ("fossil_fuels", "nuclear")
STORAGE_MODELS = ("batteries", "hydro")
RENEWABLES = ("wind", "solar")
NON_RENEWABLES = ("fossil_fuels", "nuclear")
REPRESENTATIONS = ("wind","solar")
TODAY_MIDNIGHT = utils.getTodayMidnight()
if DEBUG: print("§ globs init today midnight 1:", TODAY_MIDNIGHT)
FORECAST_MODELS = {}
for static_model in STATIC_MODELS:  
    FORECAST_MODELS[static_model] = static_model + "_forecast"

# General methods

# File related data classes =================================================

# Parameter files: methods and classes
def P(parameter_type, parameter_name):
    ''' Shorthand for full parameter syntax:
    "ParameterTypes["<parameter type>"].parameters["<parameter name>]" ''' 
    return ParameterTypes[parameter_type].parameters[parameter_name]

@dataclass
class Parameters:
    parameter_type : str
    file_name : str
    parameters : dict = field(init = False) # Dictionary of parameter names and values

    def loadParameters(self):
        procedure = "loadParameters"
        message = "Loading " + self.parameter_type + " parameters from " + self.file_name +"."
        logbook.writeLog("Info", app, procedure, message)
        parameters = utils.loadCSVasDictionary(self.pathname)
        return parameters

    def description(self):
        print("§ globMain: Parameters for", self.parameter_type, "file", self.file_name, "are:")
        print(self.parameters)
        print()

    def __post_init__(self):           
        self.pathname = path.join(GTS_FILEPATH, "gts_databases", self.parameter_type, self.file_name) #parameters_filename
        self.parameters = self.loadParameters()
        if DEBUG: self.description()

# Timeline files: methods and classes

@dataclass
class TimeLines:
    #__slots__ = ["name"]
    name : str
    timelines_type : str
    coefficients : dict
    Timelines_baseline : list = field(init = False)
    Timelines_regenerated : list = field(init = False)
    Timelines_changes : list  = field(init = False)
    Timelines_baseline_string : str = field(init = False)
    Timelines_regenerated_string : str = field(init = False)
    Timelines_changes_string : str  = field(init = False)  
    number_of_samples : int = field(init = False)
    rms_values : dict  = field(init = False)

    def description(self):
        print()
        print("§", self.timelines_type, "timelines from", self.name)
        print()
        print("§ 1. Baseline...")
        print(self.Timelines_baseline_string)
        #print()            
        print("§ 2. Regenerated...")
        print(self.Timelines_regenerated_string)
        #print()            
        print("§ 3. Changes...")
        print(self.Timelines_changes_string)

        
    def loadTimelines(self):
        # Get matrix from file
        procedure = "loadTLs"
        self.timelines_filepath = path.join(GTS_FILEPATH, "gts_databases", "timelines", self.name)
        message = "Loading timelines file " + self.name + "."
        logbook.writeLog("Info", app, procedure, message)
        timelines_matrix = utils.loadCSVasList(self.timelines_filepath)
        Head = timelines_matrix[0]
        Body = timelines_matrix[1:]
        timelines = maths.transpose2D(Body)

        # get "time" timeline
        self.Timelines_baseline = {}
        time_slots = []
        if DEBUG: logbook.writeLog("Info", app, procedure, "Converting time timeline to delta times.")
        for time_slot in timelines[0]:
            hours = int(time_slot[0:2])
            minutes = int(time_slot[3:5])
            seconds = int(time_slot[6:8])
            time_slot_value = dt.timedelta(hours = hours, minutes = minutes, seconds = seconds)
            time_slots.append(time_slot_value)
        self.Timelines_baseline["time"] = time_slots
        self.number_of_samples = len(self.Timelines_baseline["time"])
        self.timeline_pi_factor = pi / self.number_of_samples
        # get remaining timelines
        row = 1
        for source in Head[1:]:
            self.Timelines_baseline[Head[row]] = timelines[row]
            row += 1

        if DEBUG:
            for key in self.Timelines_baseline.keys():
                print("§ loadTLs:", key, self.Timelines_baseline[key])

    def checkTimelines(self):      
        samples_number_ok = True
        procedure = "chkTLs"
        if DEBUG: print("§ TimeLines =", self.Timelines_baseline)
        for source in self.Timelines_baseline:
            # check for equal numbers of samples
            if DEBUG: print("§ source =", source, "TimeLines =", self.Timelines_baseline[source])
            if len(self.Timelines_baseline[source])!= self.number_of_samples:     
                samples_number_ok = False
                message = "Operation aborted - source TimeLines '" + source + "' not compatible with TimeLines length."
                logbook.writeLog("ERROR", app, procedure, message)                  
            # check for forbidden negative values
            if source != "time" and source != "Temperature" and not(utils.allPositive(self.Timelines_baseline[source])):
                message = "Operation aborted - forbidden negative value in TimeLines '" + source + "' found."
                logbook.writeLog("ERROR", app, procedure, message)
            # check for increasing time values & uniform sampling
            if source == "time":
                if not utils.allIncreasing(self.Timelines_baseline["time"]):
                    message = "Operation aborted - times must be in increasing order."
                    logbook.writeLog("ERROR", app, procedure, message)
                if not utils.uniformSampling(self.Timelines_baseline["time"]):
                    message = "Non-uniform sampling detected."
                    logbook.writeLog("Warning", app, procedure, message)      
        logbook.writeLog("Info", app, procedure, "Timelines " + self.name + " " + self.timelines_type + " checked out ok.")

    def regenerateTimelines(self):
        ''' Regenerates timelines from baseline according to difficulty level '''
        app = "regenTLs"
        message = "Generating " + self.timelines_type + " timelines file from " + self.name + "."
        logbook.writeLog("Info", app, procedure, message)
        
        timelines_regenerated = {}
        self.rms_values = {}
        for key in self.Timelines_baseline.keys():
            timelines_regenerated["time"] = self.Timelines_baseline["time"]
            if key != "time":
                timelines_regenerated[key] = []               
                DC_level_random_number = uniform(-1,1)
                half_wave_random_number = uniform(-1,1)

                for sample in self.Timelines_baseline[key]:
                    #print("§ mystery investigation sample: ", sample)
                    sample_angle = (sample) * self.timeline_pi_factor
                    sample_level_random_number = uniform(-1,1)
                    randomise_factor = DIFFICULTY * (self.coefficients["DC_level"] * DC_level_random_number + \
                                        self.coefficients["half_wave"] * half_wave_random_number * sin(sample_angle) + \
                                        self.coefficients["sample_level"] * sample_level_random_number)

                    if randomise_factor > 0:
                        timelines_regenerated[key].append(sample * (1 + randomise_factor))
                    else:
                        timelines_regenerated[key].append(sample / (1 - randomise_factor))

                self.rms_values[key] = maths.rmsDiff1D(self.Timelines_baseline[key], timelines_regenerated[key])

        self.Timelines_regenerated = timelines_regenerated
        if DEBUG:
            for key in timelines_regenerated.keys():
                print("§ regenTLs:", key, timelines_regenerated[key])

    def getChangesTimelines(self):
        self.Timelines_changes = {}
        for timeline in self.Timelines_regenerated:
            self.Timelines_changes[timeline] = maths.getChangesWrap(self.Timelines_regenerated[timeline])
    
    def formatTimelines(self):
        self.Timelines_baseline_string = utils.formatTimelines(self.Timelines_baseline)
        self.Timelines_regenerated_string = utils.formatTimelines(self.Timelines_regenerated)
        self.Timelines_changes_string = utils.formatTimelines(self.Timelines_changes)
        #print(formatTimelines(timelines))

    def renewTimelines(self):
        self.regenerateTimelines() # add random factors
        self.getChangesTimelines() # for changes mode
        self.formatTimelines() # for configuration logfile TBD append renewed
        
    def __post_init__(self):
        self.loadTimelines()
        self.checkTimelines() # consistency checks
        self.regenerateTimelines() # add random factors
        self.getChangesTimelines() # for changes mode
        self.formatTimelines() # for configuration logfile
        #print("§ globs getChanges - ", self.Timelines_changes)

        
# Main global app code

procedure = "main"
# Instantiate configuration parameters
configuration_file = supervisor.getConfiguration(GTS_FILEPATH)
Configuration = Parameters("configurations", configuration_file)
configuration_files = Configuration.parameters
if DEBUG: Configuration.description()

# Instantiate remaining parameters
ParameterTypes = {}
ParameterTypes["configurations"] = Configuration
if DEBUG:
    print("§ globs instantiate remaining...")
    print(ParameterTypes)
    print(ParameterTypes["configurations"])
    print("Configuration file name:", ParameterTypes["configurations"].file_name)

for parameter_type in CONFIGURATION_TYPES[2:]:
    #print("§ globs parameter type:", parameter_type)
    ParameterTypes[parameter_type] = Parameters(parameter_type, configuration_files[parameter_type])

# Logbook settings temporary values
LOGBOOK_SCREEN = P("logbook_settings", "logs_level_screen") 
LOGBOOK_FILE = P("logbook_settings", "logs_level_file")
logbook.resetLogfileSettings(LOGBOOK_SCREEN, LOGBOOK_FILE)

# Extract useful parameters
#MAX_DIFFICULTY =  P("simulation", "MAX_DIFFICULTY")
DIFFICULTY = supervisor.getDifficulty(P("simulation", "AUTO_SUPERVISOR"), P("simulation", "AUTO_SUPERVISOR_DIFFICULTY"), P("simulation", "MAX_DIFFICULTY"))
REAL_TIME = P("simulation", "REAL_TIME")
TIME_FACTOR = P("simulation", "TIME_FACTOR")
FRAME_RATE = P("simulation", "FRAME_RATE")
MAINS_STANDARD_FREQUENCY = P("scale_factors", "grid_frequency")

# Coefficients for randomised timelines
coefficients_operational_timeline = {"DC_level": P("models", "timeline.operational.coefficients.DC_level"), "half_wave": P("models", "timeline.operational.coefficients.half_wave"), "sample_level": P("models", "timeline.operational.coefficients.sample_level")}
coefficients_forecast_timeline = {"DC_level": P("models", "timeline.forecast.coefficients.DC_level"), "half_wave": P("models", "timeline.forecast.coefficients.half_wave"), "sample_level": P("models", "timeline.forecast.coefficients.sample_level")}
 
if GTS_PLATFORM == "RPi":
    HARDWARE = P("simulation", "REAL_TIME")
else:
    HARDWARE = False
    
#print("§ globs platform, hardware", GTS_PLATFORM, HARDWARE)
    
logbook.writeLog("Info", app, procedure, "Hardware set to: " + str(HARDWARE) + ".")

# Instantiate timelines
DEBUG = False
timeline_file = configuration_files["timelines"]

OperationalTimelines = TimeLines(timeline_file, "operational", coefficients_operational_timeline)
if DEBUG: 
    print(configuration_files)
    print(timeline_file)
    OperationalTimelines.description()

ForecastTimelines = TimeLines(timeline_file, "forecast", coefficients_forecast_timeline)
if DEBUG: 
    print(configuration_files)
    print(timeline_file)
    ForecastTimelines.description()

# Derived parameters
TOTAL_SAMPLES = OperationalTimelines.number_of_samples
FIRST_SAMPLE_TIME = OperationalTimelines.Timelines_baseline["time"][0]
LAST_SAMPLE_TIME = OperationalTimelines.Timelines_baseline["time"][TOTAL_SAMPLES-1]
TIMELINE_DURATION = LAST_SAMPLE_TIME - FIRST_SAMPLE_TIME
SIM_START_TIME = supervisor.getSimStartTime(P("simulation", "AUTO_SUPERVISOR"), P("simulation", "AUTO_SUPERVISOR_START_TIME_OPTION"), TODAY_MIDNIGHT, FIRST_SAMPLE_TIME, LAST_SAMPLE_TIME)
SIM_RUN_TIME, SIM_END_TIME = supervisor.getSimRunTime(P, SIM_START_TIME)
SAMPLE_INTERVAL = TIMELINE_DURATION / (TOTAL_SAMPLES-1)
FRAME_INTERVAL_SECONDS = 1 / FRAME_RATE
SIM_CYCLE_INTERVAL = dt.timedelta(seconds = TIME_FACTOR / FRAME_RATE)
SIM_CYCLE_INTERVAL_SECS = TIME_FACTOR / FRAME_RATE
SIM_CYCLE_INTERVAL_HRS = SIM_CYCLE_INTERVAL_SECS / 3600

MAX_POWER = 0
for element in STATIC_MODELS:
    if element != "temperature":
        MAX_POWER = max(MAX_POWER, P("scale_factors", element + ".power"))
for element in DYNAMIC_MODELS:
    MAX_POWER = max(MAX_POWER, P("scale_factors", element +".power"))
for element in STORAGE_MODELS:
    MAX_POWER = max(MAX_POWER, P("scale_factors", element +".power"))

MAX_STORAGE = 0
TOTAL_STORAGE = 0
for element in STORAGE_MODELS:
    MAX_STORAGE = max(MAX_STORAGE, P("scale_factors", element + ".capacity"))
    TOTAL_STORAGE += P("scale_factors", element + ".capacity")

# Useful parameters (compatible with V1 code)
INITIAL_CONDITIONS_MODE = P("initial_conditions", "mode")
FORECAST_MODE = P("models", "forecast.mode")
GAUGES_STANDARDISED_POWER = P("scale_factors", "standardised_power")
GRID_CONTROL_LAW = P("models", "grid.control_law")

# Warnings for incompatible parameter values
# NRM modes
if P("models", "NRM.mode") == "manual" and not REAL_TIME:
    logbook.writeLog("ERROR", app, procedure, "Manual non-renewables control can only be with real time operation.")

# Dumps
SNAPSHOT_INTERVAL = P("simulation", "SNAPSHOT_INTERVAL")
if SNAPSHOT_INTERVAL > TIME_FACTOR / FRAME_RATE:
    DUMP = True
    DUMP_INTERVAL = dt.timedelta(seconds = SNAPSHOT_INTERVAL)
else:
    DUMP = False
if HARDWARE:
    SCHEDULER_CYCLES = 3
else:
    SCHEDULER_CYCLES = max(int(SNAPSHOT_INTERVAL * FRAME_RATE / TIME_FACTOR),1)
if SCHEDULER_CYCLES == 1: 
    logbook.writeLog("Warning", app, procedure, "Snapshot time very short at one per frame.")

DEBUG = False

# End code for globals ============================


def test_rms():
    print("rms_values for difficulty level", DIFFICULTY)
    print(OperationalTimelines.rms_values)
    OperationalTimelines.regenerateTimelines()
    print(OperationalTimelines.rms_values)
    OperationalTimelines.regenerateTimelines()
    print(OperationalTimelines.rms_values)
    OperationalTimelines.regenerateTimelines()
    print(OperationalTimelines.rms_values)
    OperationalTimelines.regenerateTimelines()

def test_simtimes():
    print("SIM_START_TIME", SIM_START_TIME.strftime("%Y-%m-%d %H:%M:%S"))
    print("SIM_RUN_TIME", SIM_RUN_TIME)
    print("SIM_END_TIME", SIM_END_TIME.strftime("%Y-%m-%d %H:%M:%S"))
    
if __name__ == "__main__":
    #test_rms()
    #test_simtimes()
    logbook.closeLog()
