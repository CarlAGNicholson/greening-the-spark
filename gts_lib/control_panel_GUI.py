# Greening the Spark Grid Control System
# Module: grid control panel
# Version 2.0
# Date: 01/03/2022
# Author Carl Nicholson

# Change log
# 27/01/22 Release of V2 for development

# To do list - search for "TBD"

# Import standard libraries
#import time as t
#import datetime
import sys
#import copy

app = "ctrlPan"
procedure = "init"

# Import GTS libraries
import gts_lib
import gts_lib.logbook as logbook
from gts_lib.gts_globals import * # treated as local variables & methods by all modules
import gts_lib.gts_maths as maths
import gts_lib.static_models as stmods

# Initialisation
DEBUGLOOP = False
DEBUG = False
logbook.writeLog("Info", app, procedure, "Control panel initialised.")

FOSSIL_FUELS_READING = 0
NUCLEAR_READING = 0

# Class and method definitions
#=============================

class Gauge():

    display_type = "gauge"

    def __init__(self, element, gauge_type, zero_position, max_position):
        
        self.element = element
        self.gauge_type = gauge_type
        self.zero_position = zero_position
        self.max_position = max_position

    def description(self):

        print("§ Gauges - type = {}; element = {}; zero position = {}; max position = {}".format(self.gauge_type, self.element, self.zero_position, self.max_position))
    
    def writeGauge(self, value, max_value):
        
        if DEBUGLOOP:
            self.description()
            print("§ writeGa setting gauge value & max value: ", self.gauge_type, self.element, value, max_value)
        '''
        # gauge model code here        
        if value > max_value * 1.1: value = max_value * 1.1
        position = maths.lfit(value, 0, self.zero_position, max_value, self.max_position)
        dd.setGauge(self.element, self.gauge_type, position)
        '''
        return

class Control():

    control_type = "potentiometer"

    def __init__(self, element, control_type, zero_position, max_position):
        
        self.element = element
        self.control_type = control_type
        self.zero_position = zero_position
        self.max_position = max_position

    def description(self):
        print("§ Control - type = {}; element = {}; zero position = {}; max position = {}".format(self.control_type, self.element, self.zero_position, self.max_position))

    def getControl(self, element, control_type, max_power):
        DEBUGLOOP = False
        if DEBUGLOOP:
            print("§ getCtrl getting control: ", element, control_type)
 
        if element == "fossil_fuels":
            reading = FOSSIL_FUELS_READING
            #print("§ getCtrl pot reading: ", element, reading)
            power = reading * P("scale_factors", "fossil_fuels.power") /100
        
        elif element == "nuclear":
            reading = NUCLEAR_READING
            #print("§ getCtrl pot reading: ", element, reading)
            power = reading * P("scale_factors", "nuclear.power") / 100
       
        if DEBUGLOOP: print("§ getControl % and power: ", reading, element, power)

        return power
    
    # M&C panel update code here ---------------------------------------

def readControlPanel(element):
    #print("§ GUI readCtrlPan")
    #if element == "fossil_fuels":

    power_control = PowerControl[element].getControl(element, "potentiometer", P("scale_factors", element + ".power"))
    #elif element == "nuclear": power_control = Nuclear_power_control.getControl("nuclear", "potentiometer", P("scale_factors", "nuclear.power"))
    return power_control

def writeNumericHeader(mode_switch, \
                       sim_time, \
                       frequency, \
                       total_CO2, \
                       total_cost, \
                       total_wind_energy, \
                       total_solar_energy, \
                       total_fossil_fuels_energy, \
                       total_nuclear_energy):
    procedure = "writeNumHead"

    def formatSciNumber(number):
        #blinking = 0
        sci_format = f"{number:.1e}"
        
        if sci_format[4] == "+":
            number_string = sci_format[:2] + sci_format[2:4] + sci_format[6]
            #decimal_point = 1
            #colon = 0

        elif sci_format[4] == "-":
            number_string = sci_format[:2] + sci_format[2:3] + "-" + sci_format[6]
            #decimal_point = 1
            #colon = 0
        else:
            logbook.writeLog("ERROR", app, procedure, "Formatting error in sign field " + sci_format[4])
            #print("ERROR - Formatting error in sign field " + sci_format[4])
              
        return number_string

    def formatPositiveNumber4digit(number):
        procedure = "fmtPosNum"
        #x = 1/0 # exception handling test
        blinking = 0
        colon = 0
        if number < 1.0e-9:
            number_string = "0.000"
        elif number < 0.01:
            number_string = formatSciNumber(number)
        elif number < 0.1:
            number_string = f"{number:1.3f}"
        elif number < 1.0:
            number_string = f"{number:2.3f}"
        elif number < 10:
            number_string = f"{number:1.3f}"
        elif number < 100:
            number_string = f"{number:2.2f}"
        elif number < 1000:
            number_string = f"{number:3.1f}"
        elif number < 10000:
            number_string = f"{number:4.0f}"
        elif number < 1.0e10:
            number_string = formatSciNumber(number)
        else:
            number_string = "9999"
            blinking = 1
            logbook.writeLog("Info", app, procedure, "Number out of range (>= 10^10)")
        return (number_string, colon, blinking)


    def formatFrequency(number):
        real_format = f"{number:2.2f}"
        if real_format[2] != "." or len(real_format) != 5:
            #print("Invalid frequency format", real_format)
            logbook.writeLog("ERROR", app, procedure, "Invalid frequency format.")
        else:
            number_string = real_format
            #decimal_point = 2
            colon = 0
            blinking = 0
          
        return (number_string, colon, blinking)

    def formatSimClock(sim_time):
        number_string = sim_time.strftime("%H") + sim_time.strftime("%M")
        #decimal_point = 0
        colon = 1
        blinking = 0
          
        return(number_string, colon, blinking)
    
    # format data strings
    if mode_switch == 0:
        header_strings[0] = formatSimClock(sim_time)
        header_strings[1] = formatFrequency(frequency)
        header_strings[2] = formatPositiveNumber4digit(total_CO2)
        #print("§ writeNH CO2: ", total_CO2)
        header_strings[3] = formatPositiveNumber4digit(total_cost)
    elif mode_switch == 1: 
        header_strings[0] = formatPositiveNumber4digit(total_wind_energy)
        header_strings[1] = formatPositiveNumber4digit(total_solar_energy)
        header_strings[2] = formatPositiveNumber4digit(total_fossil_fuels_energy)
        header_strings[3] = formatPositiveNumber4digit(total_nuclear_energy)
    else:
        logbook.writeLog("ERROR", app, procedure, "Invalid mode switch position " + int(mode_switch))

    if DEBUGLOOP: print("§ write Header_strings", header_strings)

    dd.setNumericHeader(header_strings)

def updateControlPanel(wind_power, \
                       solar_power, \
                       demand_power, \
                       fossil_fuels_power, \
                       nuclear_power, \
                       wind_forecast, \
                       wind_forecast_max, \
                       solar_forecast, \
                       solar_forecast_max, \
                       demand_forecast, \
                       demand_forecast_max, \
                       batteries_level_percent, \
                       hydro_level_percent, \
                       grid_status):

    print("§ GUI updateCtrlPan (power) - wind: {:.2f}, solar: {:.2f}, demand: {:.2f}, fossil_fuels: {:.2f}, nuclear: {:.2f}, batteries %: {:.2f}, hydro %: {:.2f}".format( \
                                    wind_power, solar_power, demand_power, fossil_fuels_power, nuclear_power, batteries_level_percent, hydro_level_percent))
    #print()
    '''
    # Update gauges
    Wind_power_gauge.writeGauge(wind_power, wind_max_power)
    Solar_power_gauge.writeGauge(solar_power, solar_max_power)
    Demand_power_gauge.writeGauge(demand_power, demand_max_power)

    #print("§ CTRL P", wind_forecast_max, solar_forecast_max, demand_forecast_max)
    
    Wind_forecast_gauge.writeGauge(wind_forecast, wind_forecast_max)
    Solar_forecast_gauge.writeGauge(solar_forecast, solar_forecast_max)
    Demand_forecast_gauge.writeGauge(demand_forecast, demand_forecast_max)

    Fossil_fuels_power_gauge.writeGauge(fossil_fuels_power, fossil_fuels_max_power)
    Nuclear_power_gauge.writeGauge(nuclear_power, nuclear_max_power)

    # Update status indicators
    Batteries_status_indicator.writeStorageStatusIndicator(batteries_level_percent)
    Hydro_status_indicator.writeStorageStatusIndicator(hydro_level_percent)
    if DEBUGLOOP: print("§ updateControlPanel levels %", batteries_level_percent, hydro_level_percent)
    # ... grid status indicators
    Grid_status_indicator.writeGridStatusIndicator(grid_status)
    #writeClock(clock_time)
    '''

def updateNumericHeader(sim_time, \
                       frequency, \
                       total_CO2, \
                       total_cost, \
                       total_wind_energy, \
                       total_solar_energy, \
                       total_fossil_fuels_energy, \
                       total_nuclear_energy):
    print("§ GUI updateNumHead - time {}, frequency: {:.2f}, CO2: {:.2f}, cost: {:.2f}, (energies) - wind: {:.2f}, solar: {:.2f}, fossil_fuels: {:.2f}, nuclear: {:.2f}".format( \
                                sim_time, frequency, total_CO2, total_cost, total_wind_energy, total_solar_energy, total_fossil_fuels_energy, total_nuclear_energy))
    print("§")
    '''
    # get switch position
    mode_switch = int(dd.MODE_SWITCH_PIN.value)
    # write numneric header
    writeNumericHeader(mode_switch,\
                       sim_time, \
                       frequency, \
                       total_CO2, \
                       total_cost, \
                       total_wind_energy, \
                       total_solar_energy, \
                       total_fossil_fuels_energy, \
                       total_nuclear_energy)
    '''

# End M&C panels update code -----------------------------------------

            
class StorageStatusIndicator():
    
    def __init__(self, name):
        self.name = name
        self.indicator_type = "10 segment LED bar array"
        
    def description(self):
        print("§ SSI indicator - type = {}; instance = {}".format(self.indicator_type, self.name))
    
    def writeStorageStatusIndicator(self, level):
        procedure = "writeSSI"
        if DEBUGLOOP: print("§ writeSSI writing status indicator", self.indicator_type, self.name, "with value %.2f" % (level))
        if 0 <= level <= 100:
            dd.setStorageStatusIndicator(self.name, level)
        else:
            logbook.writeLog("ERROR", app, procedure, "Invalid storage status " + str(level) + ", must be in range 0 - 100%")
        
    
class GridStatusIndicator():

    def __init__(self):
        self.name = "grid status indicator"
        self.indicator_type = "grid status indicator - 3 leds"

    def description(self):
        print("§ GSI indicator - type =", self.indicator_type)

    def writeGridStatusIndicator(self, value):
        procedure = "writeGSI"
        pass
    
        '''
        if DEBUGLOOP: print("§ writeGSI writing status indicator", self.name, "with value" , value)

        if value == "surplus":   
            dd.setGridStatusIndicator("RED", OFF)
            dd.setGridStatusIndicator("GREEN", OFF)
            dd.setGridStatusIndicator("AMBER", ON)
        elif value == "nominal":   
            dd.setGridStatusIndicator("RED", OFF)
            dd.setGridStatusIndicator("GREEN", ON)
            dd.setGridStatusIndicator("AMBER", OFF)
        elif value == "shortfall":   
            dd.setGridStatusIndicator("RED", ON)
            dd.setGridStatusIndicator("GREEN", OFF)
            dd.setGridStatusIndicator("AMBER", OFF)
        else:
            logbook.writeLog("ERROR", app, procedure, "Invalid grid status " + value)
        '''

    
# Control panel main code
#========================
procedure = "init"
logbook.writeLog("Info", app, procedure, "Loading control panel.")

# Initialise gauges
PowerGaugeType = {}
for element in STATIC_MODELS + DYNAMIC_MODELS:
    PowerGaugeType[element] = "min_zero" # get from model parameters tbd

# wind?
#solar_power_gauge_type = "min_zero" # get from model parameters tbd
#demand_power_gauge_type = "min_zero" # get from model parameters tbd
#fossil_fuels_power_gauge_type = "min_zero" # get from model parameters tbd
#nuclear_power_gauge_type = "min_zero" # get from model parameters tbd

if FORECAST_MODE == "changes":
    gauge_type = "centre_zero"
elif FORECAST_MODE == "normal":
    gauge_type = "min_zero"
else:
    logbook.writeLog("Warning", app, procedure, "Unknown forecast mode " + FORECAST_MODE + ", settting to default (changes).")
    gauge_type = "centre_zero"

ForecastGaugeType = {}
for element in STATIC_MODELS:
    ForecastGaugeType[element] = gauge_type # get from model parameters tbd
    
#wind_forecast_gauge_type = forecast_gauge_type
#solar_forecast_gauge_type = forecast_gauge_type
#demand_forecast_gauge_type = forecast_gauge_type

# Get calibration values

# obsolete
'''
wind_power_servo_zero =  P("calibrations", "wind.power.servo_zero")
wind_power_servo_max =  P("calibrations", "wind.power.servo_max")
wind_forecast_servo_zero =  P("calibrations", "wind.forecast.servo_zero")
wind_forecast_servo_max =  P("calibrations", "wind.forecast.servo_max")
solar_power_servo_zero =  P("calibrations", "solar.power.servo_zero")
solar_power_servo_max =  P("calibrations", "solar.power.servo_max")
solar_forecast_servo_zero =  P("calibrations", "solar.forecast.servo_zero")
solar_forecast_servo_max =  P("calibrations", "solar.forecast.servo_max")
demand_power_servo_zero =  P("calibrations", "demand.power.servo_zero")
demand_power_servo_max =  P("calibrations", "demand.power.servo_max")
demand_forecast_servo_zero =  P("calibrations", "demand.forecast.servo_zero")
demand_forecast_servo_max =  P("calibrations", "demand.forecast.servo_max")
fossil_fuels_power_servo_zero =  P("calibrations", "fossil.fuels_power.servo_zero")
fossil_fuels_power_servo_max =  P("calibrations", "fossil.fuels_power.servo_max")
nuclear_power_servo_zero =  P("calibrations", "nuclear.power.servo_zero")
nuclear_power_servo_max =  P("calibrations", "nuclear.power.servo_max")

ff_power_control_pot_zero =  P("calibrations", "fossil_fuels.power.control_pot.zero")
ff_power_control_pot_max =  P("calibrations", "fossil_fuels.power.control_pot.max")
nuclear_power_control_pot_zero =  P("calibrations", "nuclear.power.control_pot.zero")
nuclear_power_control_pot_max =  P("calibrations", "nuclear.power.control_pot.max")
'''
# Get scale factors for non-standardised displays)
#wind_scale_factor =  P("scale_factors", "wind"]
#solar_scale_factor =  P("scale_factors", "solar"]
#temperature_scale_factor =  P("scale_factors", "temperature"]
#demand_scale_factor = P("scale_factors", "demand"]
#fossil_fuels_scale_factor =  P("scale_factors", "fossil_fuels"]
#nuclear_scale_factor =  P("scale_factors", "nuclear"]
#grid_frequency =  P("scale_factors", "grid_frequency"]
#standardised_power =  P("scale_factors", "standardised_power"]
batteries_capacity =  P("scale_factors", "batteries.capacity")
hydro_capacity =  P("scale_factors", "hydro.capacity")

''' use in real panel:
if GAUGES_STANDARDISED_POWER:
    if DEBUG: print("§ M&C panel setting scales to standardised power level.")
    logbook.writeLog("Info", app, "init", "M&C panel setting scales to standardised power level.")
    wind_max_power = P("scale_factors", "power_gauges.fsd")
    solar_max_power = P("scale_factors", "power_gauges.fsd")
    demand_max_power = P("scale_factors", "power_gauges.fsd")
    fossil_fuels_max_power = P("scale_factors", "power_gauges.fsd")
    nuclear_max_power = P("scale_factors", "power_gauges.fsd")
else:
    if DEBUG: print("§ M&C panel setting scales to individual power levels")
    logbook.writeLog("Info", app, "init", "M&C panel setting scales to individual power levels")
    wind_max_power = P("scale_factors", "wind")
    solar_max_power = P("scale_factors", "solar")
    demand_max_power = P("scale_factors", "demand")
    fossil_fuels_max_power = P("scale_factors", "fossil_fuels")
    nuclear_max_power = P("scale_factors", "nuclear")
'''

# Instantiate controls
PowerControl = {}
for element in DYNAMIC_MODELS:
    PowerControl[element] = Control(element, "potentiometer", P("calibrations", element + ".power.control_pot.zero"), P("calibrations", element + ".power.control_pot.max"))

    #Fossil_fuels_power_control = Control("fossil_fuels", "potentiometer", ff_power_control_pot_zero, ff_power_control_pot_max)

# Instantiate gauges
PowerGauge = {}
for element in STATIC_MODELS + DYNAMIC_MODELS:
    PowerGauge[element] = Gauge(element, PowerGaugeType[element], P("calibrations", element + ".power.servo_zero"), P("calibrations", element + ".power.servo_max"))

#Solar_power_gauge = Gauge("solar", solar_power_gauge_type, solar_power_servo_zero, solar_power_servo_max)
#Demand_power_gauge = Gauge("demand", demand_power_gauge_type, demand_power_servo_zero, demand_power_servo_max)
#Fossil_fuels_power_gauge = Gauge("fossil_fuels", fossil_fuels_power_gauge_type, fossil_fuels_power_servo_zero, fossil_fuels_power_servo_max)
#Nuclear_power_gauge = Gauge("nuclear", nuclear_power_gauge_type, nuclear_power_servo_zero, nuclear_power_servo_max)

ForecastGauge = {}
for element in STATIC_MODELS:
    ForecastGauge[element] = Gauge(element + "_forecast", ForecastGaugeType[element], P("calibrations", element + ".forecast.servo_zero"), P("calibrations", element + ".forecast.servo_max"))


#Solar_forecast_gauge = Gauge("solar_forecast", solar_forecast_gauge_type, solar_forecast_servo_zero, solar_forecast_servo_max)
#Demand_forecast_gauge = Gauge("demand_forecast", demand_forecast_gauge_type, demand_forecast_servo_zero, demand_forecast_servo_max)

# Instantiate status indicators
StatusIndicator = {}
for element in STORAGE_MODELS:
    StatusIndicator[element] = StorageStatusIndicator(element)

#Hydro_status_indicator = StorageStatusIndicator("hydro")

Grid_status_indicator = GridStatusIndicator()

header_strings = ["","","",""]

# Check instantiations
DEBUG = True
if DEBUG:
    for element in DYNAMIC_MODELS:
        PowerControl[element].description
    for element in STATIC_MODELS + DYNAMIC_MODELS:
        PowerGauge[element].description
    for element in STATIC_MODELS:
        ForecastGauge[element].description
    for element in STORAGE_MODELS:
        StatusIndicator[element].description
    Grid_status_indicator.description

'''    
    Wind_power_gauge.description()
    Solar_power_gauge.description()
    Demand_power_gauge.description()
    
    Wind_forecast_gauge.description()
    Solar_forecast_gauge.description()
    Demand_forecast_gauge.description()

    Fossil_fuels_power_control.description()
    Nuclear_power_control.description()
    Fossil_fuels_power_gauge.description()
    Nuclear_power_gauge.description()
     
    Batteries_status_indicator.description()
    Hydro_status_indicator.description()
    Grid_status_indicator.description()
'''
        
#if __name__ == "__main__":
#    start()

# End control panel module main code ===============================================
