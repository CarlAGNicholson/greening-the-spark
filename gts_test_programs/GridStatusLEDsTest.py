# Greening the Spark Grid Control System
# Application: Grid status indicators test program
# Version 1.0
# Date: 09/08/2021
# Author Carl Nicholson

# Housekeeping #
#==============#
# To do list - search for "TBD"

# Import standard libraries
import time
import sys


# Set GTS filepath
if sys.platform == 'win32':  #Windows PC
    gts_filepath = "D:\Projects\Greening the Spark\GTS"
    
else:                        # RPi
    gts_filepath = r'/home/pi/Desktop/GTS'

sys.path.append(gts_filepath)

import gts_lib 

# Import device drivers
if sys.platform == 'win32':  #Windows PC
    import gts_lib.device_drivers_dummy as dd # PC version
    
else:                        # RPi
    import gts_lib.device_drivers as dd # PC version

import gts_lib.logbook as log
#import gts_lib.control_panel as ctrpan

# Initialise process
app = "GSITP"
procedure = "main"
DEBUG = True
DEBUGLOOP = False

ON = 1
OFF = 0

# Define local variables and methods

# Start main program------------------------------------------------------

# Status LEDs test

def LEDTest(name, speed):

    if name == "cycle":
        #set all LEDs to off
        dd.setGridStatusIndicator("RED", OFF)
        dd.setGridStatusIndicator("AMBER", OFF)
        delay = 1 / speed
        for i in range(2*speed):
            #set red LED on
            print("§ GSITP setting red LED on")
            dd.setGridStatusIndicator("RED", ON)
            time.sleep(delay)
            #set red LED off
            print("§ GSITP setting red LED off")
            dd.setGridStatusIndicator("RED", OFF)
            
            #set green LED on
            print("§ GSITP (not) setting green LED on")
            time.sleep(delay)
            #set green LED off
            print("§ GSITP (not) setting green LED off")
            
            #set amber LED on
            print("§ GSITP setting amber LED on")
            dd.setGridStatusIndicator("AMBER", ON)
            time.sleep(delay)
            #set amber LED off
            print("§ GSITP setting amber LED off")
            dd.setGridStatusIndicator("AMBER", OFF)
            
                        #set green LED on
            print("§ GSITP (not) setting green LED on")
            time.sleep(delay)
            #set green LED off
            print("§ GSITP (not) setting green LED off")
            
    else:
        print("§ GSITP error: no such test", name)
            

def start():
    log.writeLog("Info",app,procedure,"Starting grid status indicators test program.")
    LEDTest("cycle",1)
    LEDTest("cycle",5)
    LEDTest("cycle",10)
    LEDTest("cycle",50)
    LEDTest("cycle",100)

def end():
    log.writeLog("Info",app,procedure,"App terminated successfully.")

try:
    start()

except KeyboardInterrupt:
    end()
    sys.exit(0)

# End main program------------------------------------------------------
# That's it!


