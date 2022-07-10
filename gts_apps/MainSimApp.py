# Greening the Spark Grid Control System
# Application: Main Sim App
# Version 2.0
# Date: 03/03/2022
# Author Carl Nicholson

# Change log
# 27/01/22 Release of V2 for development

# To do list - search for "TBD"

app = "MSA"
procedure = "main"
DEBUG = False
DEBUGLOOP = False


# Import standard libraries
import sys
import time as t
import datetime as dt
import traceback

print("§ MSA: starting MainSimApp.")

# Set GTS filepath; must be set independently (otherwise couldn't load globals)
if sys.platform == 'win32':
    gts_filepath = "D:\Projects\Greening the Spark\GTS" #WindowsPC

else:
    gts_filepath = r'/home/pi/Desktop/GTS' # RPi#

sys.path.append(gts_filepath) # this is the only place this is necessary 

# Import GTS libraries
import gts_lib
import gts_lib.logbook as logbook
import gts_lib.gts_maths as maths
import gts_lib.gts_utilities as utils
from gts_lib.gts_globals import * # treated as local variables & methods by all modules
import gts_lib.static_models as stamods
import gts_lib.dynamic_models as dymods
import gts_lib.storage_models as stomods
import gts_lib.grid_model as gridmod
import gts_lib.reports as reports
import gts_lib.supervisor as supervisor
if not HARDWARE: import gts_lib.control_panel_GUI as ctrpan
logbook.writeLog("Info", "MSA", "init", "Main sim app initialised.")

# MainSimApp ================================================================================================


def upDateModels(sim_time):
    #if DEBUGLOOP:
    #print("§ MSA: sim_time", sim_time)
    procedure = "updateModels"
    
    if DEBUGLOOP:
        for element in STATIC_MODELS:
            print("§ MSA: upDateModels -", element, sim_time, stamods.StaticModels[element].telemetry)
        for element in DYNAMIC_MODELS:
            print("§ MSA: upDateModels -", element, sim_time, dymods.DynamicModels[element].telemetry)         
        for element in STORAGE_MODELS:
            print("§ MSA: upDateModels -", element, sim_time, stomods.StorageModels[element].telemetry)

    # collect telemetry
    telemetry = {}
    for element in STATIC_MODELS:
        telemetry[element] = stamods.StaticModels[element].telemetry
    for element in DYNAMIC_MODELS:
        telemetry[element] = dymods.DynamicModels[element].telemetry
    for element in STORAGE_MODELS:
        telemetry[element] = stomods.StorageModels[element].telemetry

    # run models
    telecommands = gridmod.GTSGrid.runGridControlModel(GRID_CONTROL_LAW, sim_time, telemetry) 
    for element in STATIC_MODELS:     
        stamods.StaticModels[element].runModel(sim_time, telecommands[element])
        if DEBUGLOOP: print("§ MSA: upDateModels - element, sim time, TC", element, sim_time, telecommands[element])
    for element in DYNAMIC_MODELS:
        dymods.DynamicModels[element].runModel(sim_time, telecommands[element])
        if DEBUGLOOP:
            print("§ MSA: upDateModels - element, sim time, TC", element, sim_time, telecommands[element])
    for element in STORAGE_MODELS:
        stomods.StorageModels[element].runModel(sim_time, telecommands[element])
        if DEBUGLOOP: print("§ MSA: upDateModels - element, sim time, TC", element, sim_time, telecommands[element])  

def rolloverTimelines(sim_time):
    # regenerate timelines
    print("§ MSA: regenerating static model timelines for midnight rollover at " + sim_time.strftime("%Y-%m-%d %H:%M") + ".")
    #print("§ static models: renewing operational timelines for midnight rollover.")
    OperationalTimelines.renewTimelines()
    for static_model in STATIC_MODELS:
        stamods.StaticModels[static_model].updateTimelines(OperationalTimelines.Timelines_regenerated[static_model])

    #print("§ static models: renewing forecast timelines for midnight rollover.")
    ForecastTimelines.renewTimelines()
    for static_model in STATIC_MODELS:
        gridmod.GTSGrid.ForecastModels[static_model].updateTimelines(ForecastTimelines.Timelines_regenerated[static_model])
    
    # TBD add to configuration log
    logbook.writeLog("Info", app, procedure, "Timelines renewed after midnight rollover.")

def handleKeyboardInterupt():
    key = "0"
    if GTS_PLATFORM == "PC": # do keyboard interupt handling
        if REAL_TIME:
            while t.perf_counter() < wait_end_time_seconds:
                name, key = supervisor.handleKeyboardInterrupt()
                if key == "x":  return key
                else:
                    if name == "FOSSIL_FUELS_READING":
                        ctrpan.FOSSIL_FUELS_READING = key
                        power = key * P("scale_factors", "fossil_fuels.power") /100
                        print("§ MSA: fossil fuels power set to {:.2f}".format(power))
                        logbook.writeLog("Info", app, procedure, "Fossil fuels power set to {:.2f}".format(power))
                    if name == "NUCLEAR_READING":
                        ctrpan.NUCLEAR_READING = key
                        power = key * P("scale_factors", "nuclear.power") /100
                        print("§ MSA: nuclear power set to {:.2f}".format(power))
                        logbook.writeLog("Info", app, procedure, "Nuclear power set to {:.2f}".format(power))
                    key = "c"
        else:
            name, key = supervisor.handleKeyboardInterrupt()
            if name == "FOSSIL_FUELS_READING":
                ctrpan.FOSSIL_FUELS_READING = key
                power = key * P("scale_factors", "fossil_fuels.power") /100
                print("§ MSA: fossil fuels power set to {:.2f}".format(power))
                logbook.writeLog("Info", app, procedure, "Fossil fuels power set to {:.2f}".format(power))
                
            elif name == "NUCLEAR_READING":
                ctrpan.NUCLEAR_READING = key
                power = key * P("scale_factors", "nuclear.power") /100
                print("§ MSA: nuclear power set to {:.2f}".format(power))
                logbook.writeLog("Info", app, procedure, "Nuclear power set to {:.2f}".format(power))
        
        if key == "x": return key
    elif GTS_PLATFORM == "RPi":
        if REAL_TIME:
            while t.perf_counter() < wait_end_time_seconds:
                pass # TBD do the switch thing
    else:
        logbook.writeLog("ERROR", app, procedure, "Invalid platform " + GTS_PLATFORM + ".")
    

def shutdown():
    if DEBUG: print("§ MSA: Closing dump file")
    logbook.writeLog("Info", app, procedure, "Closing dump file") 
    gridmod.GTSGrid.closeDumpFile()
    print("§ MSA: Writing report")
    reports.printSimulationReport(SIM_START_TIME, SIM_END_TIME, SIM_RUN_TIME, stamods.StaticModels, \
                    dymods.DynamicModels, stomods.StorageModels, gridmod.GTSGrid, ParameterTypes, DIFFICULTY)
    
    print("§ MSA: Closing logbook")
    logbook.closeLog()
    print("§ MSA: Simulation complete. Goodbye!")

# Start of MSA code
logbook.writeLog("Info", app, procedure, "Writing configuration logfile.")
reports.writeConfigurationLogFile(ParameterTypes, OperationalTimelines, ForecastTimelines)

# Initialise sim loop
wait_start_time_seconds = t.perf_counter()
wait_end_time_seconds = wait_start_time_seconds
sim_time = SIM_START_TIME
last_sim_time_day = SIM_START_TIME.day

print("§")
print("§ MSA: simulation running... configuration {}, start time {}, run time {}, time factor {:.0f}, difficulty level {:.0f}."\
      .format(configuration_file, SIM_START_TIME.strftime("%Y-%m-%d %H:%M:%S"), SIM_RUN_TIME, TIME_FACTOR, DIFFICULTY))
if GTS_PLATFORM == "PC":
    print("§ MSA: press <spacebar> for runtime options")
else:
    pass # print("§ MSA: press <pause> button for runtime options")
print("§")

# main sim loop
while sim_time <= SIM_END_TIME:
    
    if sim_time.day != last_sim_time_day: 
        rolloverTimelines(sim_time)
        reports.appendConfigurationLogFileTimelines(sim_time, OperationalTimelines, ForecastTimelines)
        last_sim_time_day = sim_time.day

    upDateModels(sim_time) # TBD update to as below when all working
    
    '''
    try:
        upDateModels(sim_time)
    except Exception as GTSerror:
        print("§ Simulation aborted, exception raised - see logs for details")
        logbook.writeLog("Info", app, procedure, "Simulation aborted, exception raised; initiating shutdown procedure.")
        GTSTraceback = traceback.format_exc()
        globals_as_lines = utils.formatCSVasLines(str(globals()), ITEMS_PER_LINE)
        logbook.writeLog("Info", app, procedure, globals_as_lines)
        logbook.writeLog("Info", app, procedure, str(GTSerror))
        logbook.writeLog("Info", app, procedure, GTSTraceback)
        shutdown()
        sys.exit(0)
    '''
    
    sim_time += SIM_CYCLE_INTERVAL
    wait_end_time_seconds += FRAME_INTERVAL_SECONDS

    key = handleKeyboardInterupt()
    if key == "x": break
 
    wait_start_time_seconds = wait_end_time_seconds
    
shutdown()

# end MainSimApp ============================================================================================


    

    


    







