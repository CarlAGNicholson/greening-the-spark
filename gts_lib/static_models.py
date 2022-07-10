# Greening the Spark Grid Control System
# Module: Static models
# Version 2.0
# Date: 27/01/2022
# Author Carl Nicholson

# Change log
# 27/01/22 Release of V2 for development

# To do list - also search for "TBD"sample
# TBD turn off representations at shutdown

# Import standard libraries
import sys

# Import GTS libraries
import gts_lib
import gts_lib.logbook as logbook
from gts_lib.gts_globals import * # treated as local variables & methods by all modules
import gts_lib.gts_maths as maths
import gts_lib.gts_utilities as utils
import gts_lib.representations as reps

app = "StaticModels"
procedure = "init"
DEBUG = False
DEBUGLOOP = False
logbook.writeLog("Info", app, procedure, "Static models initialised.")

# Class and method definitions #
#===============================

def getSampleNumber(sim_time):
    sim_time_elapsed = sim_time - (utils.getTodayMidnight() + FIRST_SAMPLE_TIME)
    sample_number = int(sim_time_elapsed.total_seconds() // SAMPLE_INTERVAL.total_seconds())
    sample_number = sample_number % TOTAL_SAMPLES
    if DEBUGLOOP:
        print("§ stMods getSampleNumber", sample_number)
    return sample_number

def getSourceValue(samples, sim_time):
    sample_number1 = getSampleNumber(sim_time)
    value1 = samples[sample_number1]
    sample_number2 = getSampleNumber(sim_time + SAMPLE_INTERVAL)
    value2 = samples[sample_number2]
    sim_time_elapsed = sim_time - (utils.getTodayMidnight() + FIRST_SAMPLE_TIME)
    w = sim_time_elapsed.total_seconds() % SAMPLE_INTERVAL.total_seconds() / SAMPLE_INTERVAL.total_seconds()
    value = maths.linterpolate(value1, value2, w)
    #if DEBUGLOOP:
    #print("§ stmods: sim_time {}, sample1 {}, sample2 {}, value1 {:.2f}, value2 {:.2f}, value {:.4f}".format(sim_time, sample_number1, sample_number2, value1, value2, value))
    return value

class StaticModel:
    element_type = "static"
    def __init__(self, name, static_model_type, source_timeline, scale_factor):
        self.name = name
        self.static_model_type = static_model_type
        self.source_timeline = source_timeline
        self.scale_factor = scale_factor
        self.source_value = getSourceValue(source_timeline, SIM_START_TIME)
        self.total_energy = 0.0
        self.status = "startup"
        self.power_value = self.calibrateStaticModel(self.name, self.source_value, self.scale_factor)
        self.telemetry = {"status" : self.status, "source": self.source_value, "power" : self.power_value, "total_energy" : self.total_energy}

    def updateTimelines(self, source_timeline):
        self.source_timeline = source_timeline
                         
    def description(self):
        if DEBUG: print("§ Static models sources - type = {}, name = {}, type = {}, scale = {}, data = {}, init source = {}".\
            format(self.element_type, self.name, self.static_model_type, self.scale_factor, self.source_timeline, self.source_value))

    def runModel(self, sim_time, telecommand):
        app = "StaticModel"
        procedure = "runModel"
        
        #x = 1/0 # !! exception test
        
        if DEBUGLOOP:
            print("§ runModel Running static model: ", self.name)
            self.description()
            print("§ runModel Executing telecommand", telecommand)

        # Interpret and execute telecommand
        if DEBUGLOOP:
            message = "Commanding static model " + self.name + " " + telecommand["control"]
            logbook.writeLog("Info", app, procedure, message)
        
        if telecommand["control"] == "continue":
            # continue nominal operation
            self.status = "continue"
            self.source_value = getSourceValue(self.source_timeline, sim_time)
            self.power_value = self.calibrateStaticModel(self.name, self.source_value, self.scale_factor)            
          
        elif telecommand["control"] == "offline":
            # take offline
            self.status = "offline"
            self.source_value = getSourceValue(self.source_timeline, sim_time)
            self.power_value = 0
              
        elif telecommand["control"] == "online":
            # put online
            self.status = "online"
            self.source_value = getSourceValue(self.source_timeline, sim_time)
            self.power_value = self.calibrateStaticModel(self.name, self.source_value, self.scale_factor) 
            
        elif telecommand["control"] == "test":
            # test mode
            self.status = "e and pi"
            self.source_value = 2.71828
            self.power_value = 3.14159
                
        else:
            self.power_value = -1
            self.source_value = -1
            message = "Unknown telecommand " + str(telecommand["control"]) + " for " + self.name + "."
            logbook.writeLog("ERROR", app, procedure, message)

        # Update representations
        if DEBUGLOOP: print("§ stmods runModel setting representation {} to power {:.2f}".format(self.name, self.power_value))
        if self.static_model_type == "operational" and self.name != "demand":
            reps.Representations[self.name].runRepresentation(self.name, self.source_value)
        
        # Generate telemetry
        self.telemetry = {"status" : self.status, "source" : self.source_value, "power" : self.power_value, "total_energy" : self.total_energy}    
        return

        # end runModel()

    def calibrateStaticModel(self, element, source_value, scale_factor):
        procedure = "calStMod"
        if element == "wind":
            if DEBUGLOOP: print("§ calStMod using wind power calibration formula.")    
            procedure = "calWind"
            #wind.speed.stall = P("calibrations", "wind.speed.stall")
            #wind.speed.max = P("calibrations", "wind.speed.max")
            #wind.power.min = 0
            #wind.power.max = P("scale_factors", "wind.power")  * wind.speed.max
                
            if P("calibrations", "wind.speed.stall") <= source_value <= P("calibrations", "wind.speed.max"):
                power_value = maths.lfit(source_value, P("calibrations", "wind.speed.stall"), 0, \
                            P("calibrations", "wind.speed.max"), P("scale_factors", "wind.power")  * P("calibrations", "wind.speed.max"))
            else:
                power_value = 0
                
        elif element == "solar":
            procedure = "calSol"
            if DEBUGLOOP: print("§ calStMod using solar power calibration formula.")
            power_value = source_value * P("scale_factors", "solar.power")
                 
        elif element == "temperature":
            power_value = source_value # straight through
            
        elif element == "demand":
            if DEBUGLOOP: print("§ calStEl using demand power calibration formula.")    
            procedure = "calDem"
            power_value = source_value * P("scale_factors", "demand.power")
                
        elif element == "wind_forecast":
            power_value = 0.0 # dummy value, not used
                
        elif element == "solar_forecast":
            power_value = 0.0 # dummy value, not used
                
        elif element == "temperature_forecast":
            power_value = source_value # straight through
            
        elif element == "demand_forecast":
            power_value = source_value * P("scale_factors", "demand.power")         

        else:
            print("§ calStEl unknown element for static model calibration ", element)
        self.power = power_value
        self.total_energy += self.power * SIM_CYCLE_INTERVAL_HRS
        return power_value


# Static models module main code #
#=================================
procedure = "main"
DEBUG = False

if DEBUG:
    print("§ stmods main, operational regenerated timelines:")
    print(OperationalTimelines.Timelines_regenerated)

#wind_timeline = OperationalTimelines.Timelines_regenerated["wind"]
#solar_timeline = OperationalTimelines.Timelines_regenerated["solar"]
#demand_timeline = OperationalTimelines.Timelines_regenerated["demand"]


# Set models properties (none)

# Instantiate models

StaticModels = {}
for static_model in STATIC_MODELS:
    if static_model == "temperature":
        parameter_name = static_model + ".temperature"
    else:
        parameter_name = static_model + ".power"
    StaticModels[static_model] = StaticModel(static_model, "operational", OperationalTimelines.Timelines_regenerated[static_model], P("scale_factors", parameter_name))
    if DEBUG: StaticModels[static_model].description()

#Wind = StaticModel("wind", wind_timeline, wind_scale_factor)
#Solar = StaticModel("solar", solar_timeline, solar_scale_factor)
#Demand = StaticModel("demand", demand_timeline, demand_scale_factor)

#if DEBUG:
#    Wind.description()
#    Solar.description()
#    Demand.description()
   
# Main loop code (as example for MSA)
#====================================

def start():

    pass

if __name__ == "__main__":
    start()


