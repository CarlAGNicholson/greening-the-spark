# Greening the Spark Grid Control System
# Application: Storage models
# Version 2.0
# Date: 09/03/2022
# Author Carl Nicholson
# Change log
# 27/01/22 Release of V2 for development

# To do list - search for "TBD"

# Import standard libraries
import time as t
import datetime
import sys
import copy

# Import GTS libraries
import gts_lib
import gts_lib.logbook as logbook
from gts_lib.gts_globals import * # treated as local variables & methods by all modules
import gts_lib.gts_maths as maths

app = "StorageModels"
procedure = "init"
DEBUG = False
DEBUGLOOP = False
logbook.writeLog("Info", app, procedure, "Dynamic models initialised.")

# Class and method definitions
#=============================

class StorageModel():

    element_type = "storage model"

    def __init__(self, element, max_power, capacity, initial_power, initial_level):      
        self.element = element
        self.capacity = capacity
        self.inv_capacity = 1 / self.capacity
        self.max_power = max_power
        self.power = initial_power
        self.level = initial_level
        self.level_percent = self.level * self.inv_capacity * 100
        self.status = "startup"
        self.telemetry = {"status" : self.status, "power" : self.power, "level" : self.level, "level_percent" : self.level_percent}

    def description(self):
        print("§ Storage models - type = {}; element = {}, max power = {}, capacity = {}, initial power = {}, initial level = {}, status = {}".\
              format(self.element_type, self.element, self.max_power, self.capacity, self.power, self.level, self.status))
    
    def runModel(self, sim_time, telecommand): # storage model

        app = "storageModels"
        procedure = "runModel"
                
        if DEBUGLOOP:
            print("§ Running storage model: ", self.element)
            self.description()
            print("§ Control value ", telecommand)
        
        # Storage model code here -------------------------------------------

        def updateStorage(self):
            self.energy = self.power * SIM_CYCLE_INTERVAL_HRS # transferred to grid
            self.level = self.level - self.energy
            if self.level > self.capacity:
                self.level = self.capacity
                self.status = "full"
            elif self.level < 0:
                self.level = 0
                self.status = "empty"
            else:
                pass
            if self.status == "full" and self.power < 0 or self.status == "empty" and self.power > 0:
                self.power = 0
            self.level_percent = self.level * self.inv_capacity * 100
            return self   
        
        # Interpret and execute telecommand
        if type(telecommand["control"]) == float or type(telecommand["control"]) == int:
            
            self.power = telecommand["control"]
            if self.power > self.max_power:
                self.power = self.max_power
                self.status = "max power in"
            elif self.power < -self.max_power:
                self.power = -self.max_power
                self.status = "max power out"
            else:
                self.status = "nominal"
            self = updateStorage(self)
                  
        elif telecommand["control"] == "continue":
            # carry on without any changes
            self = updateStorage(self)
            
        elif telecommand["control"] == "offline":
            # take offline
            self.power = 0
            self.status = "offline"          
                        
        elif telecommand["control"] == "online":
            # take offline
            self.power = 0
            self.status = "online"          
                        
        elif telecommand["control"] == "test":
            # test mode
            self.status = "test mode"
            self.power = 3.14159
            self.level = 2.71818
        else:
            self.power = None
            self.level = None
            self.status = "error"
            message = "Unknown telecommand " + str(telecommand["control"]) + " for " + self.element + "."
            logbook.writeLog("ERROR", app, procedure, message)

        # End storage model code -------------------------------------------

        # Generate telemetry
        self.telemetry = {"status" : self.status, \
                          "power" : self.power, \
                          "level" : self.level, \
                          "level_percent" : self.level_percent}
    
# Dynamic models module main code
#================================
procedure = "main"

# Initialisation
#===============
   
# Set initial values (no temperatures or derivatives yet)

InitialValues = {} # InitialConditions scaled by scale factors

if INITIAL_CONDITIONS_MODE == "balanced":
    message = "Assigning storage models initial conditions for mode: " + INITIAL_CONDITIONS_MODE
    logbook.writeLog("Info", app, procedure, message)

    InitialValues["batteries_level"] = 0.5 * P("scale_factors", "batteries_capacity")
    InitialValues["batteries_power"] = 0
   
    InitialValues["hydro_level"] = 0.5 * P("scale_factors", "hydro_capacity")
    InitialValues["hydro_power"] = 0

    
elif INITIAL_CONDITIONS_MODE == "clean start":
    message = "Assigning storage models initial conditions for mode: " + INITIAL_CONDITIONS_MODE
    logbook.writeLog("Info", app, procedure, message)

    InitialValues["batteries_power"] = 0
    InitialValues["batteries_level"] = 0

    InitialValues["hydro_power"] = 0
    InitialValues["hydro_level"] = 0
    
elif INITIAL_CONDITIONS_MODE == "custom":
    message = "Assigning storage models initial conditions for mode: " + INITIAL_CONDITIONS_MODE
    logbook.writeLog("Info", app, procedure, message)
    
    InitialValues["batteries_level"] = P("initial_conditions", "batteries.level") * P("scale_factors", "batteries.capacity")
    InitialValues["batteries_power"] = 0    
    InitialValues["hydro_level"] = P("initial_conditions", "hydro.level") * P("scale_factors", "hydro.capacity")
    InitialValues["hydro_power"] = 0
    
else:
    message = "Unknown storage models initialisation mode: " + P("initial_conditions", "mode") + ". Check file for allowed values."
    logbook.writeLog("ERROR", app, procedure, message)


# Main storage models code
# Instantiate storage models
procedure = "main"
DEBUG = False

StorageModels = {}
for storage_model in STORAGE_MODELS:
    StorageModels[storage_model] = StorageModel(storage_model, P("scale_factors", storage_model+".power"), P("scale_factors", storage_model+".capacity"), \
            InitialValues[storage_model+"_power"], InitialValues[storage_model+"_level"])
    if DEBUG: StorageModels[storage_model].description()

# End main storage models code  

def start():
    pass
    
if __name__ == "__main__":
    start()

