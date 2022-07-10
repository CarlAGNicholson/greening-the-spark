# Greening the Spark Grid Control System
# Module: Utilities
# Version 2.0
# Date: 06/02/2022
# Author Carl Nicholson

# Change log
# 27/01/22 Release of V2 for development

# To do list - search "TBD"

# Import standard libraries
import sys
import csv
import datetime
import time
import math as m

# Set GTS filepath; must be set independently because cannot load globals
if sys.platform == 'win32':
    gts_filepath = "D:\Projects\Greening the Spark\GTS" #WindowsPC
else:
    gts_filepath = r'/home/pi/Desktop/GTS' # set RPi pathname

# Import GTS libraries
import gts_lib
import gts_lib.logbook as logbook

app = "utils"
procedure = "Init"
logbook.writeLog("Info", app, procedure, "Utilities initialised.")

def loadCSVasDictionary(filename):
    '''Loads CSV file as dictionary. Comment lines are ignored.
    Comments may also be put on a line after the data.
    Dependencies: requires function loadCSVasList().'''
    
    procedure = "loadCSVasDictionary"
    message = "File " + filename + " loading."
    #logbook.writeLog("Info", app, procedure, message)

    CSV_list = loadCSVasList(filename)
    #print("§ list = ", CSV_list)
    
    try:
        CSV_dictionary = {CSV_list[0]:CSV_list[1]}
    except:
        
        for entry in CSV_list:
            #print("§ entry = ", entry)
            if len(entry) != 2:
                return "Multiple entry failure, must return name-value pairs."
        CSV_dictionary = {}
        for entry in CSV_list:
            CSV_dictionary.update({entry[0]:entry[1]})
    
    return(CSV_dictionary)


def loadCSVasList(filename):
    '''Reads CSV file with comments delineated by the # character.
    Comments can be either whole lines or after the data.
    Converts integers to integer and floats to float; strings remain as strings.
    Whitespace tolerant for numbers. Returns a list of lists, except for a one-liner.
    '''
    procedure = "loadCSVasList"
    message = "csv file " + filename + " loading." 
    #logbook.writeLog("Info", app, procedure, message)
    
    with open (filename) as file:
        contents = file.readlines()
        
    CSV = []
    for line in contents:
        line += "\n"
        fields = []
        current_field = ""

        if line[0] == "#":
            pass
        else:
            for character in line:

                if character == ",":
                    fields.append(current_field)
                    current_field = ""
                elif character == "#" or character == "\n":
                    fields.append(current_field)
                    current_field = ""
                    break
                else:
                    current_field += character

        for i in range(len(fields)):
            try:
                fields[i] = int(fields[i])
            except:
                try:
                    fields[i] = float(fields[i])
                except:
                    fields[i] = fields[i].strip()
                    if fields[i].lower() == "true":
                        fields[i] = True
                    elif fields[i].lower() == "false":
                        fields[i] = False

        if fields != []:
            CSV.append(fields)

    if len(CSV) == 1:
        CSV = CSV[0]

    return CSV


# Generate properties list with table of contents

def createProperties(*args):
    ''' Creates a list of 1D collections together with a table of contents in property[0].
        Arguments listed as name (string) and variable pairs, eg. (.."calibrations", calibrations..)
        Scalar types must added as a single member list, eg. (.."power", [20]..)
        Access is handled by the lookupProperties() function usinf both keys.'''
    
    index = 0
    properties = []
    TOC = {}
    TOC["TOC"] = index
    properties.append(TOC)
    index += 1
    arg_type = "name" # property name
    for arg in args:
        if arg_type == "name":
            if type(arg) == str:
                TOC[arg] = index
                arg_type = "variable" # property
            else:
                return "Name error, must be a string."
        else:
            if type(arg) == dict or type(arg) == list:
                properties.append(arg)
                index += 1
                arg_type = "name"
            else: return "Variable error, must be a dictionary or list."

    return properties
   
def lookupProperties(properties, key1, key2):
    ''' Accesses a list of collections created by the createProperties() function.'''
    
    try:
        value = properties[properties[0][key1]][key2]
    except:
        value = "lookup error, invalid dictionary, list item or key"

    return value


def writeListasCSV(list_arg, filepath):
    procedure = "writeListasCSV"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    filename = filepath + "listing " + timestamp + ".csv"
    logbook.writeLog("Info", app, procedure, "Writing list to csv file.")

    original_stdout = sys.stdout # Save a reference to the original standard output
    with open(filename, 'w') as f:
        sys.stdout = f # Change the standard output to the file we created.
        for row in list_arg:
            print(*row, sep = ",")
    sys.stdout = original_stdout # Reset the standard output to its original value
    
    f.close()
    message = "List saved to " + filename
    logbook.writeLog("Info", app, procedure, message)

def printDictionary(call, mydict):
    '''Prints dictionary key and value pairs on separate lines, identifying source. '''
    for item in mydict.keys():
        print("§", call, item, mydict[item])
            
def writeLine(text_string):
    line = text_string + "\n"
    return(line)

def formatCSVasLines(text,items_per_line):
    '''Takes acomma separated list and splits it into lines'''
    text_list = text.split(",")
    formatted_text = ""
    item_count = 1 
    for item in text_list:
        formatted_text += item
        item_count += 1
        if item_count > items_per_line:
            item_count = 1
            formatted_text += "\n"
        else:
            formatted_text += ","
        
    if formatted_text[len(formatted_text)-1] == ",":
        formatted_text = formatted_text[0:len(formatted_text)-1] + "\n"    
    return formatted_text

def isInteger(string_value):
    try:
        integer_value = int(string_value)
    except ValueError:
        return False
    return True

def intRangeCheck(text_prompt, valid_range):
    max_repeats = 4
    input_value = input("§ " + text_prompt)
    count = 0
    while count < max_repeats:
        count += 1
        if isInteger(input_value):
            input_value = int(input_value)            
            if input_value in range(valid_range[0],valid_range[1]+1):
                return input_value
        input_value = input("§ Invalid value " + str(input_value) + " , please enter an integer in the range " + str(valid_range) + " ")
    logbook.writeLog("ERROR", app, procedure, "Number of tries exceeded maximum allowed. Operation halted..")
    return(False)

def getTodayMidnight():   
    today_datetime = datetime.datetime.today()
    today_midnight = datetime.datetime(today_datetime.year, today_datetime.month, today_datetime.day, 0,0,0)
    return today_midnight

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

def uniformSampling(array):
    uniform = True   
    for index in range (1, len(array)):
        #print("§ uniform array after member type =", type(array[index]))
        interval = array[index] - array[index-1]        
        if index > 1:
            #print(previous_interval, interval)
            if previous_interval != interval:
                uniform = False
        previous_interval = interval
    return uniform

def filterDictionary(dictionary, field):
    ''' Filters a data dictionary with structured names <field1>["."<fieldn>].
    If the filter field is the same as the first field in the parameter name, then an abbreviated name
    without that field is returned. Can be used recursively.''' 
    dictionary_filtered = {}
    for entry in dictionary:
        levels = entry.split(".")
        if field in levels:
            name = ""
            if field == levels[0]:
                for level in levels[1:]:
                    if level == levels[1]:
                        name += level
                    else:
                        name += ("." + level)
            else:
                name = entry
            dictionary_filtered[name] = dictionary[entry]
    return dictionary_filtered

def formatTimelines(timelines):
    formatted_timelines = ""
    for timeline in timelines:
        timeline_string = ""
        for slot in timelines[timeline]:
            #timeline_string += "," + str(slot)
            if timeline == "time":
                timeline_string += "," + str(slot)
            else:
                timeline_string += "," + "{:.2f}".format(slot)
                
        timeline_string += "]"
        formatted_timelines += timeline + ": [" + timeline_string[1:] + "\n"
    return formatted_timelines

def start():
    pass

if __name__ == "__main__":
    start()
    
# finish up
procedure = "completion"
