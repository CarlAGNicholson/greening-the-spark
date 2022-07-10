# Greening the Spark Grid Control System
# Module: grid control panel
# Version 1.0
# Date: 14/10/2021
# Author Carl Nicholson

# Housekeeping #
#==============#

# Import standard libraries
import time as t
import datetime
import sys

# Set GTS filepath
if sys.platform == 'win32':  #Windows PC
    gts_filepath = "D:\Projects\Greening the Spark\GTS"
    
else:                        # RPi
    gts_filepath = r'/home/pi/Desktop/GTS'

sys.path.append(gts_filepath)

# Import GTS library
import gts_lib.device_drivers as dd

start_time = t.perf_counter()

while True:
    start_time = t.perf_counter()
    ff = dd.readControl("fossil_fuels", "don't know")
    ff_input_control__time = t.perf_counter() - start_time
    start_time = t.perf_counter()
    nuc = dd.readControl("nuclear", "don't know")
    nuc_input_control__time = t.perf_counter() - start_time
    print("§ Input times: ff {:.6f}, nuc {:.6f}, values ff {:.2f}, nuc {:.6f}"\
          .format(ff_input_control__time, nuc_input_control__time,ff, nuc))
