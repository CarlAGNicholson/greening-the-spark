# Greening the Spark Grid Control System
# Application: Main Sim App
# Version 2.0
# Date: 14/03/2022
# Author Carl Nicholson       

# Change log
# 27/01/22 Release of V2 for development

# To do list - search for "TBD"

# Import standard libraries
import time as t
import sys

# Import GTS libraries
import gts_lib
import gts_lib.logbook as logbook
import gts_lib.gts_maths as maths
from gts_lib.gts_globals import * # treated as local variables & methods by all modules
import gts_lib.reports as reports
if GTS_PLATFORM == "RPi":
    import gts_lib.control_panel as ctrpan
else:
    import gts_lib.control_panel_GUI as ctrpan
import gts_lib.static_models as stmods # used for forecasts only

# Initialisation
procedure = "main"
app = "GridModel"
DEBUG = False
DEBUGLOOP = False

logbook.writeLog("Info", app, procedure, "Grid model initialised.")

# Class and method definitions
#=============================

def runStorageManagement(telecommand, telemetry): # TBD to be generalised in V3, not V2
    DEBUGLOOP = False # local debugging
    
    power_requested = telecommand["control"]
    
    # storage management code
    if DEBUGLOOP: print("§ runSMS telemetry ", telemetry)
        
    # for clarity only
    batteries_power = telemetry["batteries"]["power"]
    batteries_status = telemetry["batteries"]["status"]
    hydro_power = telemetry["hydro"]["power"]
    hydro_status = telemetry["hydro"]["status"]

    batteries_level = telemetry["batteries"]["level"]
    batteries_level_percent = telemetry["batteries"]["level_percent"]
    hydro_level = telemetry["hydro"]["level"]
    hydro_level_percent = telemetry["hydro"]["level_percent"]
    
    average_level_percent = 100 * (batteries_level + hydro_level) / (P("scale_factors", "batteries.capacity") + P("scale_factors", "hydro.capacity"))
    total_storage_power = P("scale_factors", "batteries.power") + P("scale_factors", "hydro.power")
    power_delivered = batteries_power + hydro_power
    
    if power_requested < 0: # charging (power is -ve)
        # DEBUGLOOP = True # local debugging
        if average_level_percent < 0.000000001: # exact arithmetic doesn't work
            status = "empty"
            batteries_coefficient = P("scale_factors", "batteries.power") / total_storage_power
            hydro_coefficient = P("scale_factors", "hydro.power") / total_storage_power
        
        elif average_level_percent > 99.999999999: # exact arithmetic doesn't work
            status = "full"
            batteries_coefficient = 0.0
            hydro_coefficient = 0.0
            
        else:
            # weight by percentage empty
            sum_100_minus_level_percent = (100-batteries_level_percent) + (100-hydro_level_percent)
            if DEBUGLOOP: print("§ SMS average level%, sum 100-level% (charging)", average_level_percent, sum_100_minus_level_percent)
            batteries_coefficient = (100-batteries_level_percent) / sum_100_minus_level_percent
            hydro_coefficient = (100-hydro_level_percent) / sum_100_minus_level_percent
            if DEBUGLOOP: print("§ SMS levels% and % weighted coefficients (charging) ", batteries_level_percent, hydro_level_percent, batteries_coefficient, hydro_coefficient)
            status = "nominal"
            
        SMS_batteries_power = batteries_coefficient * power_requested
        SMS_hydro_power = hydro_coefficient * power_requested
        
        # maximise use of power if not sufficient       
        if batteries_power <= -P("scale_factors", "batteries.power"):
            SMS_batteries_power = -P("scale_factors", "batteries.power")
            SMS_hydro_power = max(-P("scale_factors", "hydro.power"), power_requested - SMS_batteries_power)
        
        if hydro_power <= -P("scale_factors", "hydro.power"):
            SMS_hydro_power = -P("scale_factors", "hydro.power")
            SMS_batteries_power = max(-P("scale_factors", "batteries.power"), power_requested - SMS_hydro_power)
            
    else: # power_requested >= 0; discharging (power is +ve)

        if average_level_percent == 0.0:
            status = "empty"
            batteries_coefficient = 0.0 
            hydro_coefficient = 0.0

        elif average_level_percent == 100.0:
            status = "full"
            batteries_coefficient = P("scale_factors", "batteries.power") / total_storage_power
            hydro_coefficient = P("scale_factors", "hydro.power") / total_storage_power
            
        else:
            # weight by percentage full
            sum_level_percent = batteries_level_percent + hydro_level_percent
            if DEBUGLOOP: print("§ SMS average level%, sum level% (discharging)", average_level_percent, sum_level_percent)
            batteries_coefficient = batteries_level_percent / sum_level_percent
            hydro_coefficient = hydro_level_percent / sum_level_percent
            if DEBUGLOOP: print("§ SMS levels% and % weighted coefficients (discharging)", batteries_level_percent, hydro_level_percent, batteries_coefficient, hydro_coefficient)
            status = "nominal"

        SMS_batteries_power = batteries_coefficient * power_requested
        SMS_hydro_power = hydro_coefficient * power_requested
            
        # maximise use of power if not sufficient       
        if batteries_power >= P("scale_factors", "batteries.power"):
            SMS_batteries_power = P("scale_factors", "batteries.power")
            SMS_hydro_power = min(P("scale_factors", "hydro.power"), power_requested - SMS_batteries_power)
        
        if hydro_power >= P("scale_factors", "hydro.power"):
            SMS_hydro_power = P("scale_factors", "hydro.power")
            SMS_batteries_power = min(P("scale_factors", "batteries.power"), power_requested - SMS_hydro_power)
        
    power_commanded = SMS_batteries_power + SMS_hydro_power
    if DEBUGLOOP: print("§ SMS bat del, hyd del, req, bat, hydr, com, ", batteries_power, hydro_power, power_requested, SMS_batteries_power, SMS_hydro_power, power_commanded)  
      
    # end storage management code
    
    telemetry = {"power_commanded" : power_commanded, \
                 "average_level_percent" : average_level_percent, \
                 "status" : status, \
                 "SMS_batteries_power" : SMS_batteries_power, \
                 "SMS_hydro_power" : SMS_hydro_power}
    
    return telemetry

def runNonrenewablesManagement(telecommand):
    DEBUGLOOP = False # local debugging
    
    # non-renewables management code here

    if telecommand["control"] == "manual":
        
        fossil_fuels_power = telecommand["fossil_fuels_power"]
        nuclear_power = telecommand["nuclear_power"]
        power_supplied = fossil_fuels_power + nuclear_power
        status = "nominal"

    elif telecommand["control"] == "easiest": # supplements renewables to satisfy demand
        NRM_scale_factors_sum = P("scale_factors","fossil_fuels.power") + P("scale_factors","nuclear.power") 
        fossil_fuels_power = telecommand["non_renewables_required"] * P("scale_factors","fossil_fuels.power") / NRM_scale_factors_sum
        nuclear_power = telecommand["non_renewables_required"] * P("scale_factors","nuclear.power") / NRM_scale_factors_sum
        power_supplied = fossil_fuels_power + nuclear_power
        status = "nominal"

    elif telecommand["control"] == "optimal": # as easiest, but also keeps storage devices close to 50%
        NRM_scale_factors_sum = P("scale_factors","fossil_fuels.power") + P("scale_factors","nuclear.power")
        storage_charge_rate = (50 - telecommand["average_level_percent"]) * TOTAL_STORAGE / (100 * P("models", "storage.charging_timescale"))
        #print("§ grid average_level_percent {:.2f}, charge rate {:.2f}".format(telecommand["average_level_percent"], storage_charge_rate))
        fossil_fuels_power = (telecommand["non_renewables_required"] * P("scale_factors","fossil_fuels.power") + storage_charge_rate) / NRM_scale_factors_sum
        nuclear_power = (telecommand["non_renewables_required"] * P("scale_factors","nuclear.power") + storage_charge_rate) / NRM_scale_factors_sum
        power_supplied = fossil_fuels_power + nuclear_power
        status = "nominal"

    
    elif telecommand["control"] == "cleanest": # minimum carbon emissions TBD
        NRM_scale_factors_sum = P("scale_factors","fossil_fuels.power") + P("scale_factors","nuclear.power")
        fossil_fuels_power = telecommand["non_renewables_required"] * P("scale_factors","fossil_fuels.power") / NRM_scale_factors_sum
        nuclear_power = telecommand["non_renewables_required"] * P("scale_factors","nuclear.power") / NRM_scale_factors_sum
        power_supplied = fossil_fuels_power + nuclear_power
        status = "nominal"

    elif telecommand["control"] == "cheapest": # lowest cost TBD
        NRM_scale_factors_sum = P("scale_factors","fossil_fuels.power") + P("scale_factors","nuclear.power")
        fossil_fuels_power = telecommand["non_renewables_required"] * P("scale_factors","fossil_fuels.power") / NRM_scale_factors_sum
        nuclear_power = telecommand["non_renewables_required"] * P("scale_factors","nuclear.power") / NRM_scale_factors_sum
        power_supplied = fossil_fuels_power + nuclear_power
        status = "nominal"
    

    else:
        power_supplied = 0
        fossil_fuels_power = 0
        nuclear_power = 0
        status = "Unknown NRM mode " + telecommand["control"]
        logbook.writeLog("ERROR", app, procedure, status)
    
    # end non-renewables management code
    
    telemetry = {"power_supplied" : power_supplied, "status" : status, "NRM_fossil_fuels_power" : fossil_fuels_power, "NRM_nuclear_power" : nuclear_power}
    return telemetry


class GridModel():
    grid_type = "national grid"
    
    def __init__(self, name):     
        DEBUG = False
        self.name = name
        self.forecast_max = {}
        self.ForecastModels = {}
        self.next_dump_time = SIM_START_TIME

        #Instantiate forecast static models
        for static_model in STATIC_MODELS:
            if static_model == "temperature":
                parameter_name = static_model + ".temperature"
            else:
                parameter_name = static_model + ".power"
            if FORECAST_MODE == "changes":
                #print("§ gridmod forecast timeline:", ForecastTimelines.Timelines_changes[static_model])
                self.ForecastModels[static_model] = stmods.StaticModel(static_model, "forecast", ForecastTimelines.Timelines_changes[static_model], P("scale_factors", parameter_name))
                self.forecast_max[static_model] = maths.maxabs(ForecastTimelines.Timelines_changes[static_model])          
            elif FORECAST_MODE == "normal":
                self.ForecastModels[static_model] = stmods.StaticModel(static_model, "forecast", ForecastTimelines.Timelines_regenerated[static_model], P("scale_factors", parameter_name))        
            else:
                message = "Unknown forecast mode " + FORECAST_MODE
                logbook.writeLog("ERROR", app, procedure, message)  

        #print("§ CTRL P", wind_forecast_max, solar_forecast_max, demand_forecast_max)

        # Set 'previous' values for grid status indication
        self.renewables_previous = 0
        self.non_renewables_previous = 0
        self.demand_previous = 0

        # Initialise variables
        self.cumulative_surplus = 0
        self.cumulative_shortfall = 0
        self.scheduler = 0 # cycles though 0 - 2; 0 = fossil fuels power input, 1 = nuclear, 2 = update panels

        self.power_control = {}
        for element in NON_RENEWABLES:
            self.power_control[element] = ctrpan.readControlPanel(element)
        
        # Check instantiations
        if DEBUG:
            for static_model in STATIC_MODELS:
                self.ForecastModels[static_model].description()

        # Initialise state matrix
        if DUMP:
            if DEBUG: print("§ grid init opening dump file & initialising header")
            logbook.writeLog("Info", app, procedure, "Opening dump file & initialising header.")
            self.dump_file = reports.openDumpFile()
            
            # Append header
            header = "sim_time"
            for element in STATIC_MODELS + NON_RENEWABLES + STORAGE_MODELS:
                header += "," + element + ".power"
            for element in STORAGE_MODELS:
                header += "," + element + ".level"
            header += ",frequency"
            for element in NON_RENEWABLES:
                header += "," + element + ".energy"
                header += "," + element + ".cost"
                header += "," + element + ".CO2"
            header += ",grid.surplus"
            for element in STATIC_MODELS:
                header += "," + element + "_forecast"
            
            reports.appendDumpFile(self.dump_file, header)        
            
    def description(self):
        print("§ Grid model - type {}, instance {}".format(self.grid_type, self.name))
        
        
# end class stuff ---------------------------------------------------------------

    # MCS code start ----------------------------------------------

    def runGridControlModel(self, GRID_CONROL_LAW, sim_time, telemetry):
        TIMER = False
        DEBUGLOOP = False # local debugging
        procedure = "runGridModel"

        #x = 1/0 # !! exception test code
        
        #scheduler = globals()["scheduler"]
        if DEBUGLOOP: print("§ grid scheduler: ", self.scheduler)
        
        # Grid control laws ---------------------------------------

        # Get weather & demand forecasts
        if TIMER: start_time = t.perf_counter()

        for static_model in STATIC_MODELS:
            self.ForecastModels[static_model].runModel(sim_time, {"control" : "continue"})

        if DEBUGLOOP:
            line = ""
            for element in STATIC_MODELS + NON_RENEWABLES + STORAGE_MODELS:
                line += str(telemetry[element]["power"])
            print("§ runGrid SMS powers w-s-d-f-n-b-h" , line) 

        if TIMER: get_forecasts_time = t.perf_counter() - start_time

        #if DEBUGLOOP: print("§ grid forecasts: ", )    

        # Get control inputs - hardware dependent, so no loops here
        if TIMER: start_time = t.perf_counter()

        if not HARDWARE:
        
            #print("§ grid: not running scheduler", self.scheduler)
            #self.power_control["fossil_fuels"]= ctrpan.readControlPanel("fossil_fuels")
            #self.power_control["nuclear"] = ctrpan.readControlPanel("nuclear")
            self.power_control["fossil_fuels"]= 0
            self.power_control["nuclear"] = 0
            
        else:
            #print("§ grid: running scheduler", self.scheduler)
            if self.scheduler == 1:
                self.power_control["fossil_fuels"] = ctrpan.readControlPanel("fossil_fuels") 
            elif self.scheduler == 2:
                self.power_control["nuclear"] = ctrpan.readControlPanel("nuclear")
        
        if TIMER: get_control_inputs_time = t.perf_counter() - start_time

    # Calculate derived values
        if TIMER: start_time = t.perf_counter()
        renewables_power = 0
        non_renewables_power = 0
        storage_power = 0
        for element in RENEWABLES:
            renewables_power += telemetry[element]["power"]
        for element in NON_RENEWABLES:
            non_renewables_power += telemetry[element]["power"]
        for element in STORAGE_MODELS:
            storage_power += telemetry[element]["power"]
        
        #grid_status_input = renewables_power + non_renewables_power + storage_power - globals()["demand_previous"]
        grid_status_input = self.renewables_previous + self.non_renewables_previous + storage_power - self.demand_previous
        if DEBUGLOOP: print("{:.2f},{:.2f},{:.2f},{:.2f},{:.6f}".format(renewables_power, non_renewables_power, storage_power, demand_power, grid_status_input))

        total_generated_power = renewables_power + non_renewables_power
        total_grid_power = total_generated_power + storage_power
        non_renewables_required = telemetry["demand"]["power"] - renewables_power
        generation_shortfall = telemetry["demand"]["power"] - total_generated_power
        generation_surplus = total_generated_power - telemetry["demand"]["power"]
        grid_surplus = generation_surplus + storage_power
        
        self.demand_previous = telemetry["demand"]["power"]
        self.renewables_previous = renewables_power
        self.non_renewables_previous = non_renewables_power
        if TIMER: get_derived_values_time = t.perf_counter() - start_time
        
        # Generate telecommands
        if TIMER: start_time = t.perf_counter()
        if GRID_CONTROL_LAW == "default":               
            # Basic default operation
            
            # renewables
            telecommands = {}
            for element in STATIC_MODELS:
                telecommands[element] = {"control":"continue"}
            
            # storage              
            SMS_telemetry = runStorageManagement({"control" : generation_shortfall}, telemetry)
            if DEBUGLOOP: print("§ runGrid SMS status: ", SMS_telemetry["status"])
            telecommands["batteries"] = {"control" : SMS_telemetry["SMS_batteries_power"]}
            telecommands["hydro"] = {"control" : SMS_telemetry["SMS_hydro_power"]}

            # non renewables
            NRM_telemetry = runNonrenewablesManagement({"control" : P("models", "NRM.mode"), "fossil_fuels_power" : self.power_control["fossil_fuels"], \
                            "nuclear_power" : self.power_control["nuclear"], "non_renewables_required": non_renewables_required, "average_level_percent": SMS_telemetry["average_level_percent"]})
            
            #if P("models", "NRM.mode") == "manual":
            #    NRM_telemetry = runNonrenewablesManagement({"control" : "manual", "fossil_fuels_power" : self.power_control["fossil_fuels"], "nuclear_power" : self.power_control["nuclear"]})
            #else:
            #    NRM_telemetry = runNonrenewablesManagement({"control" : P("models", "NRM.mode"), "non_renewables_required" : non_renewables_required})

            if DEBUGLOOP: print("§ runGrid NRM status: ", NRM_telemetry["status"])
            telecommands["fossil_fuels"] = {"control" : NRM_telemetry["NRM_fossil_fuels_power"]}
            telecommands["nuclear"] = {"control" : NRM_telemetry["NRM_nuclear_power"]}
            
            # Set grid status for control panel indicators
            if abs(grid_status_input) < MAX_POWER * 0.0001:
                grid_status = "nominal"
            elif grid_status_input > 0:
                grid_status = "surplus"
            else: 
                grid_status = "shortfall"

            if DEBUGLOOP: print("§ runGrid grid status", grid_status)

        #elif GRID_CONTROL_LAW == "auto":
        #    pass # for now

        else:
            message = "Unknown grid control law: " + GRID_CONTROL_LAW + ". Check file for allowed values."
            logbook.writeLog("ERROR", app, procedure, message)

        if TIMER: control_law_time = t.perf_counter() - start_time
        # End grid control laws -------------------------------------------

        if DEBUGLOOP:
            print("§ grid surplus, batteries & hydro TCs ", grid_surplus, batteries_telecommand["control"], hydro_telecommand["control"])
            print("§ runGrid batteries level {:.2f}, hydro level {:.2f}".format(batteries_level, hydro_level))

        # update cumulative surplus and shortfall
        if TIMER: start_time = t.perf_counter()
        if grid_status_input > 0:
            self.cumulative_surplus += grid_status_input * SIM_CYCLE_INTERVAL_HRS
        elif grid_status_input < 0:
            self.cumulative_shortfall -= grid_status_input * SIM_CYCLE_INTERVAL_HRS
        #if DEBUGLOOP: print("§ grid cumulative surplus {:.2f} and shortfall {:.2f}".format(self.cumulative_surplus, self.cumulative_shortfall))

        # Mains frequency model - is a useful indicator of how bad surplus or shortfall is
        if total_generated_power == 0:
            surplus_ratio = 0
        else:
            surplus_ratio = grid_status_input / total_generated_power
        FUDGE_FACTOR = 0.04
        tolerance = 0.2
        if -tolerance < surplus_ratio < tolerance :
            correction = MAINS_STANDARD_FREQUENCY * surplus_ratio * FUDGE_FACTOR
        else:
            surplus_ratio = tolerance * surplus_ratio / abs(surplus_ratio)
            correction = MAINS_STANDARD_FREQUENCY * surplus_ratio * FUDGE_FACTOR
        if DEBUGLOOP: print("§ grid mains frequency: grid surplus, power, ratio, correction", grid_surplus, total_generated_power, surplus_ratio, correction)
        frequency = MAINS_STANDARD_FREQUENCY + correction

        # Calculate costs
        total_CO2 = 0
        total_cost = 0
        for element in NON_RENEWABLES:
            total_CO2 = telemetry[element]["total_CO2"]
            total_cost = telemetry[element]["total_cost"]
            
        #if DEBUGLOOP:
        #    print("§ grid model FF: energy {:.2f}, CO2 {:.2f}, cost {:.2f}".format(fossil_fuels_total_energy,fossil_fuels_cumulative_carbon_footprint,fossil_fuels_cumulative_cost))
        #    print("§ grid model Nu: energy {:.2f}, CO2 {:.2f}, cost {:.2f}".format(nuclear_total_energy,nuclear_cumulative_carbon_footprint,nuclear_cumulative_cost))
        #    print("§ grid model total CO2 {:.2f},  total cost {:.2f}".format(total_CO2, total_cost))
        
        #if DEBUGLOOP: print("§ grid total CO2 {:.2f} total cost {:.2f}".format(total_CO2, total_cost))
        
        if DEBUGLOOP: print("§ runGrid cumulative values ff: E {:.2f}, $ {:.2f}, CO2 {:.2f}, nuc: E {:.2f}, $ {:.2f}, CO2 {:.2f}".format( \
        fossil_fuels_total_energy, fossil_fuels_cumulative_cost, fossil_fuels_cumulative_carbon_footprint, nuclear_total_energy, nuclear_cumulative_cost, nuclear_cumulative_carbon_footprint))
        if TIMER: housekeeping_time = t.perf_counter() - start_time

        # Update control panels
        if TIMER: start_time = t.perf_counter()

        #print("§ grid runGrid scheduler", self.scheduler) 
        if self.scheduler == 0 : ctrpan.updateControlPanel(
                                    telemetry["wind"]["power"],
                                    telemetry["solar"]["power"],
                                    telemetry["demand"]["power"],
                                    telemetry["fossil_fuels"]["power"],
                                    telemetry["nuclear"]["power"],
                                    self.ForecastModels["wind"].source_value,
                                    self.forecast_max["wind"],
                                    self.ForecastModels["solar"].source_value,
                                    self.forecast_max["solar"],
                                    self.ForecastModels["demand"].source_value,
                                    self.forecast_max["demand"],
                                    telemetry["batteries"]["level_percent"],
                                    telemetry["hydro"]["level_percent"],
                                    grid_status)
        
        if P("simulation", "NUM_HD_CUM_PWR_DISP") == "total":
            if self.scheduler == 0 : ctrpan.updateNumericHeader(sim_time, \
                                        frequency, \
                                        total_CO2, \
                                        total_cost, \
                                        telemetry["wind"]["total_energy"], \
                                        telemetry["solar"]["total_energy"], \
                                        telemetry["fossil_fuels"]["total_energy"], \
                                        telemetry["nuclear"]["total_energy"])
        
        elif P("simulation", "NUM_HD_CUM_PWR_DISP") == "average":

            average_energy = {}
            if telemetry["demand"]["total_energy"] == 0:
                for element in STATIC_MODELS + NON_RENEWABLES:
                    average_energy[element] = 0
                average_CO2 = 0
                average_cost = 0
            else:
                for element in STATIC_MODELS + NON_RENEWABLES:
                    average_energy[element] = telemetry[element]["total_energy"] / telemetry["demand"]["total_energy"] 
                average_CO2 = total_CO2 / telemetry["demand"]["total_energy"]
                average_cost = total_cost / telemetry["demand"]["total_energy"]
        
            if self.scheduler == 0 : ctrpan.updateNumericHeader(sim_time, \
                                       frequency, \
                                       average_CO2, \
                                       average_cost, \
                                       average_energy["wind"], \
                                       average_energy["solar"], \
                                       average_energy["fossil_fuels"], \
                                       average_energy["nuclear"])
            
        else:
            
            message = "Unknown numeric header display mode " + NUM_HD_CUM_PWR_DISP
            logbook.writeLog("ERROR", app, procedure, message)
            

        if TIMER: update_control_panels_time = t.perf_counter() - start_time

        # Update state matrix (state vector = snapshot in GTS terminology)     
        if TIMER: start_time = t.perf_counter()
        if DUMP:
            if sim_time >= self.next_dump_time:
                sim_time_string = sim_time.strftime("%H:%M:%S")       
                state_vector = sim_time_string
                for element in STATIC_MODELS:
                    state_vector += "," + str(telemetry[element]["power"])
                for element in NON_RENEWABLES + STORAGE_MODELS:
                    state_vector += "," + str(telemetry[element]["power"])              
                for element in STORAGE_MODELS:
                    state_vector += "," + str(telemetry["batteries"]["level"])
                state_vector += ",frequency"
                for element in NON_RENEWABLES:
                    state_vector += "," + str(telemetry[element]["total_energy"])
                    state_vector += "," + str(telemetry[element]["total_cost"])
                    state_vector += "," + str(telemetry[element]["total_CO2"])
                state_vector += ",grid.surplus"
                for element in STATIC_MODELS:
                    state_vector += "," + str(self.ForecastModels[element].source_value)
                
                reports.appendDumpFile(self.dump_file, state_vector)
                #print("§ runGrid: sim status report at", sim_time_string)
                self.next_dump_time += DUMP_INTERVAL
                
            #stateVector_forecast = [sim_time_string, wind_forecast, solar_forecast, demand_forecast]
            DEBUGLOOP = True
            if DEBUGLOOP:
                pass
                #print("§ runGrid stateVector {}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}".format(*stateVector))
                #print("§ runGrid forecast    {}, {:.2f}, {:.2f}, {:.2f}".format(*stateVector_forecast))
        
        if TIMER: update_matrices_time = t.perf_counter() - start_time
        
        if TIMER:
            print("§ grid model times: read_tm {:.6f}, forecasts {:.6f}, inputs {:.6f}, derived {:.6f}"\
                        .format(read_telemetry_time, \
                        get_forecasts_time, \
                        get_control_inputs_time, \
                        get_derived_values_time))

            print("§ grid model times: ctrl law {:.6f}, admin {:.6f}, panels {:.6f}, matrices {:.6f}"\
                        .format(control_law_time, \
                        housekeeping_time, \
                        update_control_panels_time, \
                        update_matrices_time))
        
        if DUMP: self.scheduler = (self.scheduler + 1) % SCHEDULER_CYCLES # only for GUI - trap for zero dump interval

        return telecommands

    def closeDumpFile(self):
        reports.closeDumpFile(self.dump_file)

        # End MCS code

# Grid module main code
#==========================================================================

# grid model instantiation        
GTSGrid = GridModel("GTS")
if DEBUG: GTSGrid.description()

# End grid module main code ===============================================

# using the grid model

#if __name__ == "__main__":
#    start()
