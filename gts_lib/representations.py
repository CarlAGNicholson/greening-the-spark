# Greening the Spark Grid Control System
# Application: Main Sim App
# Version 2.0
# Date: 09/03/2022
# Author Carl Nicholson

# Change log
# 27/01/22 Release of V2 for development

# To do list - search for "TBD"

# Import standard libraries

#import time as t
#import datetime
import sys
#import copy

app = "Representations"
procedure = "init"

# Import GTS libraries
import gts_lib
import gts_lib.logbook as logbook
from gts_lib.gts_globals import * # treated as local variables & methods by all modules
import gts_lib.gts_maths as maths

if GTS_PLATFORM == "PC":  #Windows PC
    import gts_lib.device_drivers_PC as dd    
elif GTS_PLATFORM == "RPi":  # RPi
    import gts_lib.device_drivers as dd
else:
    logbook.writeLog("ERROR", app, procedure, "Invalid platform " + GTS_PLATFORM + ".")

DEBUGLOOP = False
DEBUG = False

# Initialisation
logbook.writeLog("Info", app, procedure, "Representations initialised.")

# Class and method definitions
#=============================

class Representation():

    class_name = "representation"

    def __init__(self, element, representation_type):
        '''Definitions. source: wind, solar etc.; type: zero_min, zero_centre; properties: hardware mapping, calibrations etc.'''
        self.element = element
        self.type = representation_type
        
    def description(self):

        print("Representation description: class = {}; type: {}; properties {}".format(Representation.class_name, self.element, self.type))
        

    def runRepresentation(self, element, source):

        def calibrateRepresentation(name, source):
            procedure = "calRep"
            
            if name == "wind":
                if P("calibrations", "wind.speed.stall") <= source <= P("calibrations", "wind.speed.max"):
                    control_value = maths.lfit(source, P("calibrations", "wind.speed.stall"), P("calibrations", "motor.speed.stall.12V"), P("calibrations", "wind.speed.max"), P("calibrations", "motor.speed.max.12V"))
                else:
                    control_value = 0
                    
            elif name == "solar":
                control_value = source * source * P("calibrations", "sunlamp.max_value") / (P("calibrations", "sun.max_intensity") * P("calibrations", "sun.max_intensity"))
   
            else:
                logbook.writeLog("ERROR", app, procedure, "Unknown representation type " + name + ".")

            return control_value
        
        if source > P("calibrations", "sun.max_intensity"):
            effective_source = P("calibrations", "sun.max_intensity")
        else:
            effective_source = source
        control_value = calibrateRepresentation(element, effective_source)

        #DEBUGLOOP = True

        if HARDWARE:
            dd.setRepresentation(control_value, element)
        if DEBUGLOOP: print("§ calRep {} source value {:.2f} control value {:.2f}".format(element, source, control_value))

        return

# Representations module main code
#=================================

# Initialisation
#===============
#representation = {}
#representation["wind"] = "model wind turbine"
#representation["solar"] = "LED array"
#representation["demand"] = "none"

# Get representations properties

# Instantiate representations
#============================

Representations = {}
RepresentationTypes = {"wind": "wind farm", "solar": "sun lamp"}
#print("§ reps main representations", RepresentationTypes)
for element in REPRESENTATIONS:
    Representations[element]= Representation(element, RepresentationTypes[element])
    #Representations[element].description()

#WindTurbine = Representation(representation["wind"], "TBD")
#SunLamp = Representation(representation["solar"], "TBD") 

# Check instantiations
if DEBUG:
    WindTurbine.description()
    SunLamp.description()
        
#if __name__ == "__main__":
#    start()

