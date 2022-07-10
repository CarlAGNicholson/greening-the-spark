# Greening the Spark Grid Control System
# Application: Main Sim App
# Version 1.0
# Date: 21/09/2021
# Author Carl Nicholson

# Housekeeping #
#==============#
# To do list - search for "TBD"
app = "MSA"
procedure = "main"

# Import standard libraries
import sys
import time as t
import datetime as dt
import keyboard

print("§ MSA: starting MainSimApp.")

# Set GTS filepath 
if sys.platform == 'win32':
    gts_filepath = "D:\Projects\Greening the Spark\GTS" #WindowsPC

else:
    gts_filepath = r'/home/pi/Desktop/GTS' # set RPi pathname

sys.path.append(gts_filepath) # Windows

# Import GTS libraries
import gts_lib
#print("§ MSA: importing logbook.")
import gts_lib.logbook as logbook
import gts_lib.gts_maths as maths

logbook.writeLog("Info", app, procedure, "Importing globals.")
from gts_lib.gts_globals import * # treated as local variables & methods by all modules
logbook.writeLog("Info", app, procedure, "Importing stmods.")
import gts_lib.static_models as stmods
logbook.writeLog("Info", app, procedure, "Importing dymods.")
import gts_lib.dynamic_models as dymods
logbook.writeLog("Info", app, procedure, "Importing gridmod.")
import gts_lib.grid_model as gridmod
import gts_lib.gts_utilities as utils

DEBUG = True
DEBUGLOOP = False

DUMP = True


# Define local and methods
#=====================

def runSim(): # Main sim loop
    procedure = "runSim"
    
    # Define local methods
    def handleKBInterrupt():
        print("§ MSL simulation paused")
        t.sleep(0.5)
        wait = True
        while wait:
            if keyboard.is_pressed(" "):
                print("§ MSL simulation resumed")
                t.sleep(0.1)
                wait = False
        # end handleKBInterrupt()

    def updateModels():

        procedure = "updateModels"
        #print()
        message = "Sim time: " + sim_time.strftime("%H:%M:%S") + " real time (s): " + "{:.2f}".format(wait_start_time) + "; sample = " + str(sample) + " frame = " + str(frame)

        #logbook.writeLog("Info", app, procedure, message)
        #if DEBUGLOOP:
        print("§ MSL Sim time: " + sim_time.strftime("%H:%M:%S") + " real time (s): " + "{:.2f}".format(wait_start_time) + "; sample = " + str(sample) + " frame = " + str(frame))
        #wait_end_time = wait_start_time + frame_interval

              
        # Run grid model
        #===============
        if DEBUGLOOP:
            print("§ MSL running grid model with telemetry:")
            print("§ MSL ", GRID_CONTROL_LAW, stmods.Wind.telemetry, stmods.Solar.telemetry, stmods.Demand.telemetry, dymods.Fossil_fuels.telemetry, dymods.Nuclear.telemetry, dymods.Batteries.telemetry, dymods.Hydro.telemetry)

        wind_telecommand, solar_telecommand, demand_telecommand, fossil_fuels_telecommand, nuclear_telecommand, batteries_telecommand, hydro_telecommand = \
            gridmod.runGridControlModel(GRID_CONTROL_LAW, sim_time, sample, frame, stmods.Wind.telemetry, stmods.Solar.telemetry, stmods.Demand.telemetry, \
            dymods.Fossil_fuels.telemetry, dymods.Nuclear.telemetry, dymods.Batteries.telemetry, dymods.Hydro.telemetry)                

        if DEBUGLOOP:
            print("§ MSL runGridModel sent telecommands:")
            print("§ MSL ", )

        # Run static models
        #==================        
        if DEBUGLOOP:
            print("§ MSL running static models.")
            print("§ MSL update Models sample, frame ", sample, frame)
            print("§ MSL update Models wind_telecommand ", wind_telecommand)
            print("§ MSL update Models solar_telecommand ", solar_telecommand)
            print("§ MSL update Models demand_telecommand ", demand_telecommand)
            
        stmods.Wind.runModel(sample, frame, stmods.wind_timeline, wind_telecommand)
        stmods.Solar.runModel(sample, frame, stmods.solar_timeline, solar_telecommand)
        stmods.Demand.runModel(sample, frame, stmods.demand_timeline, demand_telecommand)   

        # Run dynamic models
        #===================
        if DEBUGLOOP:
            print("§ MSL running dynamic models.")
            print("§ MSL telecommands: ", fossil_fuels_telecommand, nuclear_telecommand, batteries_telecommand, hydro_telecommand)

        dymods.Fossil_fuels.runModel(dymods.Fossil_fuels.power, fossil_fuels_telecommand)
        dymods.Nuclear.runModel(dymods.Nuclear.power, nuclear_telecommand)
        dymods.Batteries.runModel(batteries_telecommand)
        dymods.Hydro.runModel(hydro_telecommand)
                    
        return # end updateModels

    
    # Initialising main sim loop
    logbook.writeLog("Info", app, procedure, "Initialising state vector and telecommands.")

    if DEBUG:
        utils.printDictionary("MSA initial conditions", InitialConditions)

    # Set up loop timing parameters       
    sim_start_time = dt.datetime(2000,1,1,0,0,0)
    sim_time = sim_start_time

    
    # Run main loop   
    procedure = "runSim-MSL"
    logbook.writeLog("Info", app, procedure, "Starting main sim loop.")
    #wait_start_time = t.process_time()
    wait_start_time = t.perf_counter()
        
    
    for sample in range(TOTAL_SAMPLES-1):
    #for sample in range(2): # temporary test value
        
        for frame in range(FRAMES_PER_SAMPLE_INTERVAL):
        #for frame in range(2): # temporary test value

            # simulation pause & resume logic
            if keyboard.is_pressed(" "):

                # Keyboard interrupt handling
                handleKBInterrupt()
                
            else:
                wait_end_time = wait_start_time + FRAME_INTERVAL
                #time_before = t.process_time()
                time_before = t.perf_counter()
                updateModels()
                #time_after = t.process_time()
                time_after = t.perf_counter()
                processing_time = time_after - time_before
                loop_slack_per_cent = 100 * (wait_end_time - time_after)/FRAME_INTERVAL
                #processing_time = t.process_time - wait_start_time
                print("§ Time to update models = {:.4f}, loop slack % = {:.2f}, frame interval = {:.2f}".format(processing_time, loop_slack_per_cent, FRAME_INTERVAL))
                print("§ wait end time {:.4f}".format(wait_end_time))
                print("§ time before idling", t.perf_counter())
                #while t.process_time() < wait_end_time:
                while t.perf_counter() < wait_end_time:
                    #pass
                    #print("§ idling now", t.process_time())
                    print("§ idling now", t.perf_counter())
                #print("§ time at end of idle period", t.process_time())
                print("§ time at end of idle period", t.perf_counter())
                sim_time += CYCLE_INTERVAL_DT
                wait_start_time = wait_end_time

    return # stateMatrix
    # end runSim()

def shutdown(stateMatrix):
    procedure = "shutdown"

    if DUMP:
        if type(stateMatrix) == str:
            logbook.writeLog("Info", app, procedure, stateMatrix)
        else:
            utils.writeDumpFile(stateMatrix)
    
    logbook.writeLog("Info", app, procedure, "Shutdown procedure completing...")
    logbook.closeLog()
    # end shutDown()

# Main program---------------------------------------------------------

try:
    runSim()
    logbook.writeLog("Info", app, procedure, "Simulation complete; initiating shutdown procedure.")

except KeyboardInterrupt:
    #stateMatrix = "StateMatrix not returned due to ctrl <c> termination."
    #print()
    logbook.writeLog("Info", app, procedure, "Simulation aborted; initiating shutdown procedure.")
    shutdown(gridmod.stateMatrix)
    sys.exit(0)

print()
#maths.print2DasCSV("§ MSA final stateMatrix", gridmod.stateMatrix)
#shutdown(gridmod.stateMatrix)

# End main program------------------------------------------------------
# That's it!


