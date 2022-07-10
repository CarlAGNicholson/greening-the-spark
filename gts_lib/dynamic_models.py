# Greening the Spark Grid Control System
# Application: Dynamic models
# Version 2.0
# Date: 14/03/2022
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
if HARDWARE:
    import gts_lib.control_panel as ctrpan
else:
    import gts_lib.control_panel_GUI as ctrpan

app = "DynamicModels"
procedure = "init"
DEBUG = False
DEBUGLOOP = False
logbook.writeLog("Info", app, procedure, "Dynamic models initialised.")

# Class and method definitions
#=============================

class DynamicModel():
    element_type = "dynamic model"

    def __init__(self, element, power, scale_factor, cost, CO2, ramp_up, ramp_down):    
        self.element = element
        self.power = power
        self.scale_factor = scale_factor
        self.cost = cost
        self.CO2 = CO2
        self.ramp_up = ramp_up
        self.ramp_down = ramp_down
        self.ramp_up_delta = scale_factor * SIM_CYCLE_INTERVAL_SECS / ramp_up
        self.ramp_down_delta = scale_factor * SIM_CYCLE_INTERVAL_SECS / ramp_down
        self.status = "startup"
        self.total_energy = 0.0
        self.total_CO2 = 0.0
        self.total_cost = 0.0 
        self.telemetry = {"status" : self.status, "power" : self.power, "total_energy" : self.total_energy, "total_cost" : self.total_cost, "total_CO2" : self.total_CO2}

    def description(self):
        print("§ Dynamic models - type = {}; element = {}; scale factor = {:.2f}; cost = {:.2f}; CO2 = {:.2f}; ramp_up time = {:.2f}; ramp_down time = {:.2f}, initial_power = {:.2f}".\
              format(self.element_type, self.element, self.scale_factor, self.cost, self.CO2, self.ramp_up, self.ramp_down, self.power))

    def runModel(self, sim_time, telecommand): # generator model
        # uses GRID_CONTROL_LAW from globals     
        app = "dynamicModels"
        procedure = "runModel"
        
        #x = 1/0 # !! test exception
        
        if DEBUGLOOP:
            print("§ Running dynamic model: ", self.element)
            self.description()
            print("§ Executing telecommand", telecommand)

        def ramp(power, power_requested, max_power, ramp_up_delta, ramp_down_delta):
            ''' Provides ramp up/down behaviour for controlled generators. '''
            
            def ramp_up(power, power_requested, ramp_up_delta):
                if power < power_requested - ramp_up_delta:
                    power += ramp_up_delta
                else:
                    power = power_requested      
                return power

            def ramp_down(power, power_requested, ramp_down_delta):
                if power > ramp_down_delta:
                    power -= ramp_down_delta
                else:
                    power = 0
                return power

            # recalibrate if necessary
            if power_requested > max_power:
                power_requested = max_power
            elif power_requested < 0:
                power_requested = 0
                
            # call relevant ramp law
            if power_requested > power:
                power_supplied = ramp_up(power, power_requested, ramp_up_delta)
            elif power_requested < power:
                power_supplied = ramp_down(power, power_requested, ramp_down_delta)
            else:
                power_supplied = power_requested
            return power_supplied     

        # Dynamic model code here -------------------------------------------
        # Interpret and execute telecommand      
        if type(telecommand["control"]) == float or type(telecommand["control"]) == int:
            # simple model
            #if telecommand["control"] < self.scale_factor:
            #    self.power = telecommand["control"]
            #else:
            #    self.power = self.scale_factor
            
            # ramp model
            self.power = ramp(self.power, telecommand["control"], self.scale_factor, self.ramp_up_delta, self.ramp_down_delta)
            
            self.status = "nominal"
        elif telecommand["control"] == "continue":
            # nominal operation
            # power unchanged - simplest model...
            self.status = "nominal"
        elif telecommand["control"] == "offline":
            # take offline
            self.status = "offline"
        elif telecommand["control"] == "online":
            # put online
            self.status = "nominal"

        elif telecommand["control"] == "test":
            # test mode
            status = "test mode"
            logbook.writeLog("Info", app, procedure, "Commanding dynamic model in test mode.")
            
        else:
            power = None
            message = "Unknown telecommand " + str(telecommand["control"]) + " for " + self.element + "."
            logbook.writeLog("ERROR", app, procedure, message)

        self.total_energy += self.power * SIM_CYCLE_INTERVAL_HRS
        self.total_CO2 = self.total_energy * self.CO2
        self.total_cost = self.total_energy * self.cost
        if DEBUGLOOP: print("§ dynamic model {}: energy {:.2f}, CO2 {:.2f}, cost {:.2f}".format(self.element,self.total_energy,self.total_CO2,self.total_cost))

        # End dynamic model code -------------------------------------------
        #print("§ dymods test:", self.element, self.power)
        
        # Generate telemetry
        self.telemetry = {"status" : self.status, "power" : self.power, "total_energy" : self.total_energy, "total_cost" : self.total_cost, "total_CO2" : self.total_CO2}
        return
    
# Dynamic models module main code
procedure = "main"
DEBUG = False

# Instantiate dynamic models
DynamicModels = {}

for element in NON_RENEWABLES:
    if HARDWARE and P("models", "NRM.mode") == "manual":
        initial_power = ctrpan.readControlPanel(element) # from control panel
    else:
        initial_power = P("initial_conditions", element+".power") * P("scale_factors", element+".power") # from initial conditions file
    
    DynamicModels[element] = DynamicModel(element, initial_power, P("scale_factors", element+".power"), P("scale_factors", element+".cost"), \
                P("scale_factors", element+".carbon_footprint"), P("models", element+".ramp_up_time"), P("models", element+".ramp_down_time"))
    if DEBUG: DynamicModels[element].description()

# End dynamic models module main code

def start():
    pass

if __name__ == "__main__":
    start()

