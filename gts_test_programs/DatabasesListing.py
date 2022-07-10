# Greening the Spark Grid Control System
# Application: Databases content listing
# Version 1.0
# Date: 29/05/2021
# Author Carl Nicholson

# Import standard libraries
import sys
import time as t
import datetime as dt
import os
#import keyboard

print("§ DBCL: starting databases content listing.")

# Set GTS filepath 
if sys.platform == 'win32':
    gts_filepath = "D:\Projects\Greening the Spark\GTS" #WindowsPC
    gts_databases_filepath = gts_filepath + "\gts_databases"
    slash = "\\"

else:
    gts_filepath = r'/home/pi/Desktop/GTS' # set RPi pathname
    gts_databases_filepath = gts_filepath + "/gts_databases"
    slash = "/"

sys.path.append(gts_filepath) # Windows


# Import GTS libraries
import gts_lib
import gts_lib.logbook as logbook
import gts_lib.gts_utilities as utils

app = "DBCL"
procedure = "main"

exceptions = ("dump_files", "logs", "scenarios")

print("§ DBCL listing contents of files in directory", gts_databases_filepath)
print()
gts_databases_listing = os.listdir(gts_databases_filepath)

database_contents_listing = [["Directory","File","Parameter","Value"]]

for directory in gts_databases_listing:

    if directory not in exceptions:
        directory_filepath = gts_databases_filepath + slash + directory       
        directory_listing = os.listdir(directory_filepath)
        
        for file_name in directory_listing:
                    
            full_filename = directory_filepath + slash + file_name
            current_file_list = utils.loadCSVasList(full_filename)        
            if type(current_file_list[0]) == str:
                current_file_list = [current_file_list]
                
            context = [directory, file_name]
            for entry in current_file_list:
                current_file_line = context + entry
                database_contents_listing.append(current_file_line)
 
for line in database_contents_listing:
    print(line)
print()

utils.writeListasCSV(database_contents_listing, gts_databases_filepath)
logbook.writeLog("Info", app, procedure, "Shutdown procedure completing...")
logbook.closeLog()

# That's it!


