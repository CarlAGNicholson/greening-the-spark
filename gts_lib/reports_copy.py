# Greening the Spark Grid Control System
# Module: Globals
# Version 2.0
# Date: 28/02/2022
# Author Carl Nicholson

# Change log
# 27/01/22 Release of V2 for development

# To do list - search for "TBD"

procedure = "reports"
app = "init"
DEBUG = False

# Import standard libraries
import sys
import math as m

# Import GTS libraries
#import gts_lib
import gts_lib.logbook as logbook
import gts_lib.gts_maths as maths
import gts_lib.gts_utilities as utils
from gts_lib.gts_globals import * # treated as local variables & methods by all modules

# Define reporting  parameters
# for ease & compatibility with V1, code left as was, parameters now from reports configuration file
best_comment = P("reports", "comment.best")
intermediate_comment = P("reports", "comment.intermediate")
worst_comment = P("reports", "comment.worst")

# efficiency constants
efficiency_weights = {"surplus": P("reports","efficiency.weights.surplus"), "shortfall": P("reports","efficiency.weights.shortfall"), "storage" : P("reports","efficiency.weights.storage")}
efficiency_comments_surplus_boundaries = {"best-intermediate" : P("reports","efficiency.comments.surplus_boundaries.best-intermediate"), "intermediate-worst" : P("reports","efficiency.comments.surplus_boundaries.intermediate-worst")}
efficiency_comments_shortfall_boundaries = {"best-intermediate" : P("reports","efficiency.comments.shortfall_boundaries.best-intermediate"), "intermediate-worst" : P("reports","efficiency.comments.shortfall_boundaries.intermediate-worst")}
efficiency_comments_storage_boundaries = {"best-intermediate" : P("reports","efficiency.comments.storage_boundaries.best-intermediate"), "intermediate-worst" : P("reports","efficiency.comments.storage_boundaries.intermediate-worst")}
efficiency_spark_boundaries = {"red-blue" : P("reports","efficiency.spark_boundaries.red-blue"), "blue-green" : P("reports","efficiency.spark_boundaries.blue-green")}
    
# eco parameters
eco_spark_boundaries = {"red-blue" : P("reports","eco.spark_boundaries.red-blue"), "blue-green" : P("reports","eco.spark_boundaries.blue-green")}
    
# economy parameters
economy_spark_boundaries = {"red-blue" : P("reports","economy.spark_boundaries.red-blue"), "blue-green" : P("reports","economy.spark_boundaries.blue-green")}

logbook.writeLog("Info", "reports", "init", "Reporting initialised.")

# Reporting methods
def getSpark(score, boundaries):
    ''' score to spark conversion, scores are 0 - 100
    boundaries are (0), red-blue, blue-green, (100)
    '''
    procedure = "getSpark"

    if score < 0:
        spark_colour = "!!red!!"
        comment = "--->oops!"
        logbook.writeLog("Info", app, procedure, "Score out of range 0 - 100, value = " + str(score))
    elif score < boundaries["red-blue"]:
        spark_colour = "!red! "
        comment = worst_comment
    elif score < boundaries["blue-green"]:
        spark_colour = "<blue> "
        comment = intermediate_comment
    elif score <= 100:
        spark_colour = "*green* "
        comment = best_comment
    else:
        spark_colour = "**green**"
        comment = "--->oops!"
        logbook.writeLog("Info", app, procedure, "Score out of range 0 - 100, value = " + str(score))    
    return spark_colour, comment

def getCostScore(actual_value, value_for_0, value_for_100):
    ''' gets score from 0 to 100 for a value between value_for_0 and value_for_100
        scores outside this range must trapped by the receiving program
    '''
    if value_for_0 != value_for_100:
        score = (value_for_0 - actual_value) * 100 / (value_for_0 - value_for_100)
    else:
        score = 100

    return score

def getMinMaxCost(energy_supplied, costs):
    min_cost = energy_supplied * min(costs)
    max_cost = energy_supplied * max(costs)
    return min_cost, max_cost

def getEfficiencyScore(cumulative_demand, cumulative_surplus, cumulative_shortfall, capacity, final_stored, storage_discrepancy):  
    DEBUG = False
    procedure = "getEffScore"
    if cumulative_demand <= 0:
        logbook.writeLog("ERROR", app, procedure, "Zero or negative cumulative demand.")
        
    cumulative_surplus_fraction = cumulative_surplus/cumulative_demand
    cumulative_shortfall_fraction = cumulative_shortfall/cumulative_demand
    storage_discrepancy_fraction = 2 * abs(capacity/2 - final_stored)/capacity
        
    # Calculate efficiency score & spark
    cumulative_surplus_rating = 200 * m.atan(cumulative_surplus_fraction) / m.pi  
    cumulative_shortfall_rating = cumulative_shortfall_fraction * 100
    storage_discrepancy_rating = storage_discrepancy_fraction * 100
    
    EWT = (efficiency_weights["surplus"], efficiency_weights["shortfall"], efficiency_weights["storage"])
    if min(EWT) < 0 or max(EWT) == 0:
        logbook.writeLog("ERROR", app, procedure, "Invalid efficiency weightings " + EWT)
    
    if sum(EWT) != 1.0:
        efficiency_weights["surplus"] /= sum(EWT)
        efficiency_weights["shortfall"] /= sum(EWT)
        efficiency_weights["storage"] /= sum(EWT)
        
    weighted_average_ratings = cumulative_surplus_rating * efficiency_weights["surplus"] + \
                               cumulative_shortfall_rating * efficiency_weights["shortfall"] + \
                               storage_discrepancy_rating * efficiency_weights["storage"]
    
    efficiency_score = 100 - round(weighted_average_ratings)
    
    if DEBUG:
        print("§ surp_frac {:.2f}, short_frac {:.2f}, stor_frac {:.2f}, \
surplus_rat {:.2f}, short_rat {:.2f}, store_rat {:.2f}, wtd ave {:.2f}, score {:.0f}" \
            .format(cumulative_surplus_fraction, cumulative_shortfall_fraction, \
            storage_discrepancy_fraction, cumulative_surplus_rating, \
            cumulative_shortfall_rating, storage_discrepancy_rating, \
            weighted_average_ratings, efficiency_score))
       
    # Get comments  
    def getComment(rating, boundaries):
        if rating < 0 or rating > 100:
            logbook.writeLog("ERROR", app, procedure, "Rating out of range (0 - 100): {:.2f}".format(rating))
        
        if rating < boundaries["best-intermediate"]:
            comment = best_comment
        elif rating < boundaries["intermediate-worst"]:
            comment = intermediate_comment
        else:
            comment = worst_comment
        if DEBUG: print("§ getComment rating {:.4f}, {}".format(rating, comment))
        return comment
    
    surplus_comment = getComment(cumulative_surplus_rating, efficiency_comments_surplus_boundaries)
    shortfall_comment = getComment(cumulative_shortfall_rating, efficiency_comments_shortfall_boundaries)
    storage_comment = getComment(storage_discrepancy_rating, efficiency_comments_storage_boundaries)

    return int(efficiency_score), surplus_comment, shortfall_comment, storage_comment
               
def getEfficiencySpark(efficiency_score, efficiency_spark_boundaries):
    if efficiency_score < efficiency_spark_boundaries["red-blue"]:
        efficiency_spark = " !red!  "
        efficiency_comment = worst_comment
    elif efficiency_score < efficiency_spark_boundaries["blue-green"]:
        efficiency_spark = " <blue>  "
        efficiency_comment = intermediate_comment
    else: 
        efficiency_spark = "*green* "
        efficiency_comment = best_comment
    return efficiency_spark, efficiency_comment

def printSimulationReport(start_time, end_time, run_time, StaticModels, DynamicModels, StorageModels, GTSGrid, ParameterTypes, difficulty):
    ''' prints simulation report to screen & file '''
    DEBUG = False
    procedure = "printSimRep"
    run_time_hrs = run_time.days * 24 + run_time.seconds / 3600
    if DEBUG: print("§ MSA runtime {}, run_time_hrs {:.4f}".format(run_time, run_time_hrs))

    # Get data
    cumulative_demand = StaticModels["demand"].total_energy
    if cumulative_demand <= 0:
        logbook.writeLog("ERROR", app, procedure, "Invalid cumulative demand (<= 0)" + "{:.2f}".format(cumulative_demand))
    cumulative_wind =  StaticModels["wind"].total_energy
    cumulative_solar =  StaticModels["solar"].total_energy
    cumulative_fossil_fuels = DynamicModels["fossil_fuels"].total_energy
    cumulative_nuclear = DynamicModels["nuclear"].total_energy
    total_conventional = cumulative_fossil_fuels + cumulative_nuclear
    total_generated = cumulative_wind + cumulative_solar + cumulative_fossil_fuels + cumulative_nuclear
    
    total_CO2 = DynamicModels["fossil_fuels"].total_CO2 + DynamicModels["nuclear"].total_CO2
    total_cost = DynamicModels["fossil_fuels"].total_cost + DynamicModels["nuclear"].total_cost

    fossil_fuels_utilisation = 100* DynamicModels["fossil_fuels"].total_energy / (P("scale_factors","fossil_fuels.power") * run_time_hrs)
    nuclear_utilisation = 100 * DynamicModels["nuclear"].total_energy / (P("scale_factors","nuclear.power") * run_time_hrs)
    
    if DEBUG: print("§ reporting: FF E {:.2f} Nu E {:.2f} conv {:.2f} total CO2 {:.2f}, total cost {:.2f}".format(cumulative_fossil_fuels,cumulative_nuclear,total_conventional,total_CO2,total_cost))

    cumulative_surplus = GTSGrid.cumulative_surplus
    cumulative_shortfall = GTSGrid.cumulative_shortfall
    
    # TBD sort out storage calculations!!
    initial_stored = ParameterTypes["initial_conditions"].parameters["batteries.level"] + \
                     ParameterTypes["initial_conditions"].parameters["hydro.level"]
    initial_stored_report = ParameterTypes["initial_conditions"].parameters["batteries.level"] * ParameterTypes["scale_factors"].parameters["batteries.capacity"]+ \
                     ParameterTypes["initial_conditions"].parameters["hydro.level"] * ParameterTypes["scale_factors"].parameters["hydro.capacity"]
    
    final_stored = StorageModels["batteries"].level + \
                   StorageModels["hydro"].level
    
    final_stored_report = StorageModels["batteries"].level * ParameterTypes["scale_factors"].parameters["batteries.capacity"] + \
                   StorageModels["hydro"].level * ParameterTypes["scale_factors"].parameters["hydro.capacity"]
    
    capacity = ParameterTypes["scale_factors"].parameters["batteries.capacity"] + \
               ParameterTypes["scale_factors"].parameters["hydro.capacity"]
    
    storage_discrepancy = abs(capacity/2 - final_stored)
    storage_discrepancy_report = abs(final_stored - initial_stored)
    
    efficiency_score, surplus_comment, shortfall_comment, storage_comment = getEfficiencyScore(cumulative_demand, cumulative_surplus, cumulative_shortfall, capacity, final_stored, storage_discrepancy)
    efficiency_spark, efficiency_comment = getEfficiencySpark(efficiency_score, efficiency_spark_boundaries)

    # Eco scoring
    min_CO2, max_CO2 = getMinMaxCost(total_conventional, (ParameterTypes["scale_factors"].parameters["fossil_fuels.carbon_footprint"], ParameterTypes["scale_factors"].parameters["nuclear.carbon_footprint"]))
    CO2_per_GWh = total_CO2 / cumulative_demand
    eco_score = getCostScore(total_CO2, max_CO2, min_CO2)
    eco_spark, eco_comment = getSpark(eco_score, eco_spark_boundaries)
    if DEBUG: print("§ printSimRep eco scoring: score {:.2f}, total CO2 {:.2f}, max CO2 {:.2f}, min CO2 {:.2f}" \
        .format(eco_score, total_CO2, max_CO2, min_CO2))
    
    # Economy scoring
    min_cost, max_cost = getMinMaxCost(total_conventional, (ParameterTypes["scale_factors"].parameters["fossil_fuels.cost"], ParameterTypes["scale_factors"].parameters["nuclear.cost"]))
    cost_per_GWh = total_cost / cumulative_demand
    economy_score = getCostScore(total_cost, max_cost, min_cost)
    economy_spark, economy_comment = getSpark(economy_score, economy_spark_boundaries)
    if DEBUG: print("§ printSimRep economy scoring: score {:.2f}, total cost {:.2f}, \
    max cost{:.2f}, min cost {:.2f}".format(economy_score, total_cost, max_cost, min_cost))

    if DEBUG: 
        print("§ printSimRep total_demand {:.2f}, generated {:.2f}, total CO2  {:.2f} total_cost {:.2f}" \
          .format(cumulative_demand, total_generated, total_CO2, total_cost))
        print("§ printSimRep min_CO2 {:.2f} max_CO2 {:.2f}" \
          .format(min_CO2, max_CO2))
        print("§ printSimRep min_cost {:.2f} max_cost {:.2f}" \
          .format(min_cost, max_cost))
        print("§ printSimRep efficiency score", efficiency_score, "eco_score", eco_score, "economy_score", economy_score)
    
    # Create and print simulation reports
    simulation_report = []
    timestamp = logbook.timestamp[:13] + ":" + logbook.timestamp[14:16] + ":" + logbook.timestamp[17:]
    configuration_file = ParameterTypes["configurations"].file_name
    print()
    print(" Simulation Report", timestamp)
    simulation_report.append("\nTime stamp," + timestamp)
    print(" =====================================")
    print()
    print(" Configuration file:", configuration_file)
    simulation_report.append("\nConfiguration_file," + configuration_file)
    print(" Simulation start time:\t", start_time.strftime("%Y-%m-%d %H:%M:%S"))
    simulation_report.append("\nSimulation start time," + start_time.strftime("%Y-%m-%d %H:%M:%S"))
    print(" Simulation end time:\t", end_time.strftime("%Y-%m-%d %H:%M:%S"))
    simulation_report.append("\nSimulation end time," + end_time.strftime("%Y-%m-%d %H:%M:%S")) 
    print(" Simulation run time:\t", str(run_time))
    simulation_report.append("\nSimulation run time," + str(run_time))
    print(" Difficulty level :\t", difficulty)
    simulation_report.append("\nDifficulty," + str(difficulty))
    print()
    print(" Energy totals (GWh) and comments")
    print(" --------------------------------")
    print(" Demand\t\t\t" + f"{cumulative_demand:,.2f}")
    print(" Wind\t\t\t" + f"{cumulative_wind:,.2f}")
    print(" Solar\t\t\t" + f"{cumulative_solar:,.2f}")
    print(" Fossil fuels\t\t" + f"{cumulative_fossil_fuels:,.2f}")
    print(" Nuclear\t\t" + f"{cumulative_nuclear:,.2f}")
    print(" Nuclear utilisation\t{:.2f}%".format(nuclear_utilisation))
    print(" Fossil fuels util~n\t{:.2f}%".format(fossil_fuels_utilisation))

    print(" Surplus\t\t" + f"{cumulative_surplus:,.2f}" + "\t" + surplus_comment)
    print(" Shortfall\t\t" + f"{cumulative_shortfall:,.2f}" + "\t" + shortfall_comment)
    print(" Initial stored\t\t" + f"{initial_stored_report:,.2f}")
    print(" Final stored\t\t" + f"{final_stored:,.2f}")
    print(" Storage discrepancy\t" + f"{storage_discrepancy:,.2f}" + "\t" + storage_comment)
    print(" Efficiency score\t{:.0f}\t{}".format(efficiency_score, efficiency_comment))
    print()
    
    simulation_report.append("\nDemand,{:.2f}".format(cumulative_demand))
    simulation_report.append("\nWind,{:.2f}".format(cumulative_wind))
    simulation_report.append("\nSolar,{:.2f}".format(cumulative_solar))
    simulation_report.append("\nFossil fuels,{:.2f}".format(cumulative_fossil_fuels))
    simulation_report.append("\nNuclear,{:.2f}".format(cumulative_nuclear))
    simulation_report.append("\nFossil fuels utilisation,{:.2f}".format(fossil_fuels_utilisation))
    simulation_report.append("\nNuclear utilisation %,{:.2f}".format(nuclear_utilisation))

    simulation_report.append("\nSurplus,{:.2f},{}".format(cumulative_surplus, surplus_comment))
    simulation_report.append("\nShortfall,{:.2f},{}".format(cumulative_shortfall, shortfall_comment))
    simulation_report.append("\nInitial stored,{:.2f}".format(initial_stored))
    simulation_report.append("\nFinal stored,{:.2f}".format(final_stored))
    simulation_report.append("\nStorage discrepancy,{:.2f},{}".format(storage_discrepancy, storage_comment))
    simulation_report.append("\nEfficiency score,{:.2f},{}".format(efficiency_score, efficiency_comment))
        
    print(" Carbon footprint and costs with scoring and comments")
    print(" -----------------------------------------------------")   
    print(" Total CO2 (tonnes)\t" + f"{total_CO2:,.2f}")
    print(" Total cost (£M)\t" + f"{total_cost:,.2f}")
    simulation_report.append("\nTotal CO2 (tonnes),{:.2f}".format(total_CO2))
    simulation_report.append("\nTotal cost (£M),{:.2f}".format(total_cost))

    print(" Ave CO2 (tonnes/GWh)\t" + f"{CO2_per_GWh:,.2f}" + "\t" + f"{eco_score:.0f}" + "\t" + eco_comment)
    print(" Ave cost (£M/GWh)\t" + f"{cost_per_GWh:,.2f}" + "\t" + f"{economy_score:.0f}" + "\t" + economy_comment)
    simulation_report.append("\nAverage CO2 (tonnes/GWh),{:.2f},{:.0f},{}".format(CO2_per_GWh, eco_score, eco_comment))
    simulation_report.append("\nAverage cost (£M/GWh),{:.2f},{:.0f},{}".format(cost_per_GWh, economy_score, economy_comment))
    print(" =======================================================")
    print(" Sparks earned:\t Efficiency\t Eco\t\t Economy")
    print(" \t\t", efficiency_spark, "\t", eco_spark, "\t", economy_spark)
    simulation_report.append("\nFinal rating,"+ \
                             "efficiency spark," + efficiency_spark + \
                             ",eco spark," + eco_spark + \
                             ",economy spark," + economy_spark)
    print(" =======================================================")
    print()
    writeSimulationReport(simulation_report)
    if DEBUG: print(simulation_report)

def writeConfigurationLogFile(parameters, operational_timelines, forecast_timelines):
    if DEBUG:
        print("§ reports writing config logfile")
        print("§ configlogfile:", parameters)
    procedure = "writeConfigLogFile"
    timestamp = logbook.timestamp
    config_logfile = logbook.logbook_filepath + timestamp + ".cfg"
    logbook.writeLog("Info", app, procedure, "Writing config logfile.")
    configuration_file = parameters["configurations"].file_name

    with open(config_logfile, 'w') as f:
        
        f.write("Full configuration listing for configuration file " + configuration_file + "\n")                   
        for parameter_type in parameters:
            line = "Parameter type: " + parameter_type
            f.write("\n")
            f.write(line+"\n")
            
            for parameter in parameters[parameter_type].parameters:
                line = parameter + " = " + str(parameters[parameter_type].parameters[parameter])
                f.write(line+"\n")                
        f.write("\n")
        f.write("Full timelines listing\n")
        f.write("\n")
        f.write("Baseline\n")
        f.write("\n")
        f.write(operational_timelines.Timelines_baseline_string)
        f.write("\n")  
        rms_values_string = "wind: {:.2f}, solar: {:.2f}, demand: {:.2f} temperature: {:.2f}".format(operational_timelines.rms_values["wind"], \
                            operational_timelines.rms_values["solar"], operational_timelines.rms_values["demand"], operational_timelines.rms_values["temperature"])        
        f.write("Operational - rms values - " + rms_values_string + "\n")
        f.write("\n")     
        f.write(operational_timelines.Timelines_regenerated_string)
        f.write("\n")
        rms_values_string = "wind: {:.2f}, solar: {:.2f}, demand: {:.2f} temperature: {:.2f}".format(forecast_timelines.rms_values["wind"], \
                            forecast_timelines.rms_values["solar"], forecast_timelines.rms_values["demand"], forecast_timelines.rms_values["temperature"])        
        f.write("Forecast - rms values - " + rms_values_string + "\n")
        f.write("\n")
        f.write(forecast_timelines.Timelines_changes_string)
        f.write("\n")
        f.write("End of configuration logfile listings")

        if DEBUG:
            print("Baseline:")
            print(operational_timelines.Timelines_baseline_string)
            print("Operational:")
            print(operational_timelines.Timelines_regenerated_string)
            print("Changes:")
            print(operational_timelines.Timelines_changes_string)

def appendConfigurationLogFileTimelines(sim_time, operational_timelines, forecast_timelines):
    if DEBUG: 
        print("§ reports writing config logfile")
        print("§ configlogfile:", parameters)
    procedure = "writeConfigLogFileTimelines"
    timestamp = logbook.timestamp
    sim_time_string = sim_time.strftime("%Y-%m-%d %H:%M:%S")
    config_logfile = logbook.logbook_filepath + timestamp + ".cfg"
    logbook.writeLog("Info", app, procedure, "Updating config logfile.")

    with open(config_logfile, 'a') as f:
                
        f.write("\n\n")
        f.write("Updated timelines listing " + sim_time_string + "\n")
        f.write("\n")       
        rms_values_string = "wind: {:.2f}, solar: {:.2f}, demand: {:.2f} temperature: {:.2f}".format(operational_timelines.rms_values["wind"], \
                            operational_timelines.rms_values["solar"], operational_timelines.rms_values["demand"], operational_timelines.rms_values["temperature"])        
        f.write("Operational - rms values - " + rms_values_string + "\n")
        f.write("\n")
        
        f.write(operational_timelines.Timelines_regenerated_string)
        f.write("\n")
        rms_values_string = "wind: {:.2f}, solar: {:.2f}, demand: {:.2f} temperature: {:.2f}".format(forecast_timelines.rms_values["wind"], \
                            forecast_timelines.rms_values["solar"], forecast_timelines.rms_values["demand"], forecast_timelines.rms_values["temperature"])        
        f.write("Forecast - rms values - " + rms_values_string + "\n")
        f.write("\n")
        f.write(forecast_timelines.Timelines_changes_string)
        f.write("\n")
        f.write("End of configuration logfile timeline update")

        if DEBUG:
            print("Baseline:")
            print(operational_timelines.Timelines_baseline_string)
            print("Operational:")
            print(operational_timelines.Timelines_regenerated_string)
            print("Changes:")
            print(operational_timelines.Timelines_changes_string)

def openDumpFile():
    procedure = "openDumpFile"
    timestamp = logbook.timestamp
    dump_file_name = logbook.logbook_filepath + timestamp + " Dump.csv"
    logbook.writeLog("Info", app, procedure, "Opening dump file.")
    dump_file = open(dump_file_name, "a")
    logbook.writeLog("Info", app, procedure, "Closing dump file.")
    return dump_file

def appendDumpFile(dump_file, line):
    procedure = "appendDumpFile"
    timestamp = logbook.timestamp
    #logbook.writeLog("Info", app, procedure, "Writing to dump file.")
    line += "\n"
    dump_file.write(line)

def closeDumpFile(dump_file):
    logbook.writeLog("Info", app, procedure, "Closing dump file.")
    dump_file.close()

def writeSimulationReport(simulation_report):
    procedure = "writeSimulationReport"
    timestamp = logbook.timestamp
    simulation_report_file = logbook.logbook_filepath + timestamp + " SimRep.csv"
    logbook.writeLog("Info", app, procedure, "Writing simulation report to file.")

    with open(simulation_report_file, 'w') as f:
        f.writelines("Simulation report")
        f.writelines(simulation_report)
    logbook.writeLog("Info", app, procedure, "Closing simulation report file.")
    f.close()

# End of reports code ====================================================================

# test routines
def test1(): # used for test purposes only
    print("§ test procedure Final Report test 1")
    for test_value in range(90, 170, 5):
        score = getCostScore(test_value, 100, 160)
        spark = getSpark(score, efficiency_spark_boundaries)
        print("§ test_value {:.0f}, score = {:.0f}, spark = {}".format(test_value, score, spark))

def test2(parameter): # used for test purposes only
    print("§ test procedure Final Report test 2")           
    cumulative_demand = 100
    cumulative_surplus = 0
    cumulative_shortfall = 0
    capacity = 1000
    final_stored = 500
    storage_discrepancy = abs(capacity/2 - final_stored)
    
    if parameter == 1:
        print("§ surplus")
        for cumulative_surplus in range(0, 116, 5):
            efficiency_score = getEfficiencyScore(cumulative_demand, cumulative_surplus, cumulative_shortfall, capacity, final_stored, storage_discrepancy)
            print("§ cumulative_surplus {:.2f}, efficiency_score {}".format(cumulative_surplus, efficiency_score))
            print()
    
    if parameter == 2:
        print("§ shortfall")
        for cumulative_shortfall in range(0, 116, 5):
            efficiency_score = getEfficiencyScore(cumulative_demand, cumulative_surplus, cumulative_shortfall, capacity, final_stored, storage_discrepancy)
            print("§ cumulative_shortfall {:.2f}, efficiency_score {}".format(cumulative_shortfall, efficiency_score))
            print()

    if parameter == 3:
        print("§ storage")
        for final_stored in range(0, 1001, 20):
            efficiency_score = getEfficiencyScore(cumulative_demand, cumulative_surplus, cumulative_shortfall, capacity, final_stored, storage_discrepancy)
            print("§ final_stored {:.2f}, efficiency_score {}".format(final_stored, efficiency_score))
            print()

def test3(parameter):
    energy_required = 50
    max_ffs = 50
    max_nuc = 30
    cost_factor_ffs = 5
    cost_factor_nuc = 2
    
    if parameter == 1:
        energy_supplied, min_cost = minCost(energy_required, max_ffs, max_nuc, cost_factor_ffs, cost_factor_nuc)
        print("§ energy_supplied {:.2f}, min_cost {:.2f}".format(energy_supplied, min_cost))

    if parameter == 2:
        energy_supplied, max_cost = maxCost(energy_required, max_ffs, max_nuc, cost_factor_ffs, cost_factor_nuc)
        print("§ energy_supplied {:.2f}, max_cost {:.2f}".format(energy_supplied, max_cost))

def test4():
    total_cost = 12829
    max_cost = 5311
    min_cost = 531
    
    score = getCostScore(total_cost, max_cost, min_cost)
    print("§ score ", score)

def test5(): # carbon footpring scoring
    total_CO2, max_CO2, min_CO2 = 50,100,0
    for total_CO2 in range(min_CO2, max_CO2+10, 10):
        eco_score = getCostScore(total_CO2, max_CO2, min_CO2)
        eco_spark, eco_comment = getSpark(eco_score, eco_spark_boundaries)
        print("§ test 5 CO2: total {:.0f}, max {:.0f}, min {:.0f}, score {:.0f}, spark {}, comment {}"\
        .format(total_CO2, max_CO2, min_CO2, eco_score, eco_spark, eco_comment))
    
def test6(): #cost scoring
    total_cost, max_cost, min_cost = 600,1000,0
    for total_cost in range(min_cost, max_cost+100, 100):
        economy_score = getCostScore(total_cost, max_cost, min_cost)
        economy_spark, economy_comment = getSpark(economy_score, economy_spark_boundaries)
        print("§ test 6 cost: total {:.0f}, max {:.0f}, min {:.0f}, score {:.0f}, spark {}, comment {}"\
        .format(total_cost, max_cost, min_cost, economy_score, economy_spark, economy_comment))

def test7(): # CO2 min/max
    total_conventional = 100
    SF_FF_CO2 = 2
    SF_N_CO2 = 0.2
    total_CO2 = 150
    cumulative_demand = 200
    
    min_CO2, max_CO2 = getMinMaxCost(total_conventional,(SF_FF_CO2, SF_N_CO2))
    print("§ test 7 CO2: conv power {:.0f}, SF_FF_CO2 {:.2f}, SF_N_CO2 {:.2f}, total {:.0f}, min {:.0f}, max {:.0f}"\
        .format(total_conventional, SF_FF_CO2, SF_N_CO2, total_CO2, min_CO2, max_CO2))
    
def test(test_number):
        if test_number == 1: test1()
        if test_number == 2: test2(1)
        if test_number == 3: test3(2)
        if test_number == 4: test4()
        if test_number == 5: test5()    
        if test_number == 6: test6()
        if test_number == 7: test7()
        if test_number == 8: test8()

if __name__ == "__main__":
    DEBUG = True  
    test(6)
