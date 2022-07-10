#Python 3.7.3 (v3.7.3:ef4ec6ed12, Mar 25 2019, 22:22:05) [MSC v.1916 64 bit (AMD64)] on win32
#Type "help", "copyright", "credits" or "license()" for more information.

# Initialisation
from dataclasses import dataclass, field
from typing import List
import sys

def allPositive(array):
    all_positive = True
    for value in array:
        all_positive &= value >= 0 
    return all_positive

def allIncreasing(array):
    increasing = True
    for index in range (1, len(array)):
        increasing &= array[index] > array[index - 1]
    return increasing

# Runtime data related data classes =================================================
@dataclass
class Telecommand:
    __slots__ = ["sim_time", "TC"]
    time : int # will be time
    command : dict = field(metadata = "Dictionary of command types and arguments")

@dataclass
class Telemetry:
    __slots__ = ["sim_time", "TM"]
    time : int # will be time
    data : dict = field(metadata = "Dictionary of telemetry types and values")
    
# File related data classes =================================================
# Input files
@dataclass
class Parameters:
    #__slots__ = ["parameters"]
    parameter_type : str
    name : str 
    parameters : dict = field(init = False) # Dictionary of parameter names and values

    def __post_init__(self):
        # load file contents into data dictionary
        if self.name == "configuration":
            self.parameters = 

@dataclass
class TimeLines:
    #__slots__ = ["name"]
    name : str 
    #description: str
    Timelines : list = field(init = False)

    def loadTimeLines(self):

        print("Loading Timelines", self.name)
        self.Timelines = {}
        self.Timelines["time"] = [1,2,4,6,8]
        self.Timelines["wind"] = [1,2,3,4,5]
        self.Timelines["solar"] = [5,6,7,8,9]
        self.Timelines["temperature"] = [12,13,14,15,16]
        self.Timelines["demand"] = [10,20,30,40,50]

    def checkTimeLines(self):     
        # check array lengths
        DEBUG = True
        samples_number_ok = True
        if DEBUG: print("§ TimeLines =", self.Timelines)
        for source in self.Timelines:
            if DEBUG: print("§ source =", source, "TimeLines =", self.Timelines[source])
            if len(self.Timelines["time"]) != len(self.Timelines[source]):     
                samples_number_ok = False
                culprit = source
                print("§ ERROR: Operation aborted - source TimeLines " + "'" + culprit + "'", "not compatible with TimeLines length.")
                sys.exit()
        # check for forbidden negative values
            if source != "time" and source != "temperature" and not(allPositive(self.Timelines[source])): 
                #all_positive = allPositive(self.Timelines[source])
                culprit = source
                print("§ ERROR: Operation aborted - forbidden negative value in TimeLines " + "'" + culprit + "'", "found.")
                sys.exit()
        # check for increasing time values
            #if source != "time":
            if not allIncreasing(self.Timelines[source]):
                print("§ ERROR: Operation aborted - times must be in increasing order.")
                sys.exit()                    
        # warning - uniform sampling not verified
        print("§ Warning: uniform sampling not verified.")
        print("§ Info : sources checked out ok.")   
        
    def __post_init__(self): # consistency checks
        self.loadTimeLines()
        self.checkTimeLines()

# Output files
@dataclass
class Configuration:
    __slots__ = ["configuration", "parameters", "TimeLines", "configuration_report"]
    name : str     # name of overall configuration file (.cfg)
    parameter_files : list = field(init = False)     # list of parameter files (.csv)
    Timelines : TimeLines = field(init = False)     # TimeLines file (.csv)

    def __post_init__(self):
        ''' Concatenate parameter files and TimeLines and save as configuration report'''

        

        # Concatenate and save
        self.configuration_report = self.configuration + "\n" + str(self.parameters) + "\n" + self.Timelines

        # Extract data and create TimeLines and parameter data dictionaries
        # 1. Instantiate parameter files   
        # 2. Get parameters
        # 3. Instantiate TimeLines file
        # 4. Create TimeLines and samples lists


# Test area

#myConfig = Configuration("exhibition", ["p1","p2","p3","p4","p5"], "storm")

#print(myConfig)
#print("§ Config report") 
#print(myConfig.configuration_report)

STATIC_MODELS = ["wind", "solar", "temperature", "demand"]

# Load parameters
# Get main configuration file & create configuration files list
# List configuration directory & choose config
Folder = {}
Folder["configuration" : ["Exhibit", "Game", "Test"]
Configuration = {}
Configuration["exhibit"] = {"simulation" : "sim_nominal", "models" : "mod_small"}
Sim_nominal = {"s_p1": 10, "s_p2" : 20, "s_p3" : 30}

print("§ Setting configuration file to 'exhibit'")
configuration_name = configuration_folder[0]
Configuration = Parameters("configuration", configuration_name)

configuration_files = Configuration.parameters
print("§ Configuration files for", configuration_name, " are:", configuration_files)

f1 = Parameters("f1")
f1_parameters = f1.parameters
print("§ f1", f1_parameters) 
                

# get TimeLines data into this form:
#TimeLines_name = "Exhibit" # name of TimeLines file
#exhibit_TimeLines = TimeLines(TimeLines_name)

#print(allPositive([1,2,-3,4]))

#print(allIncreasing([1,2,3]))


#print("§ TimeLines:", TimeLines_name)
#for source in exhibit_TimeLines.TimeLines:
#    print(source, TimeLines[source])


    
