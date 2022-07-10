# Greening the Spark Grid Control System
# Application: Seven segment LED using I2C bus test program
# Version 1.0
# Date: 08/09/2021
# Author Carl Nicholson

# Housekeeping #
#==============#
# To do list - search for "TBD"

# Import standard libraries
import time
import datetime
import sys
#import smbus

# Set GTS filepath
if sys.platform == 'win32':  #Windows PC
    gts_filepath = "D:\Projects\Greening the Spark\GTS"
    
else:                        # RPi
    gts_filepath = r'/home/pi/Desktop/GTS'

sys.path.append(gts_filepath)

import gts_lib 


# Import device drivers
'''
if sys.platform == 'win32':  #Windows PC
    import gts_lib.device_drivers_dummy as dd # PC version
    
else:                        # RPi
    import gts_lib.device_drivers as dd # PC version
'''


import gts_lib.logbook as log

sys.path.append(r'/home/pi/Adafruit')
#import HT16K33
import SevenSegment

# Initialise process
app = "I2CTP"
procedure = "main"

# Create display instance on default I2C address (0x70) and bus number.
#display = SevenSegment.SevenSegment()

# Alternatively, create a display with a specific I2C address and/or bus.

display3 = SevenSegment.SevenSegment(address=0x73, busnum=1)
display2 = SevenSegment.SevenSegment(address=0x72, busnum=1)
display1 = SevenSegment.SevenSegment(address=0x71, busnum=1)
display0 = SevenSegment.SevenSegment(address=0x70, busnum=1)

# On BeagleBone, try busnum=2 if IOError occurs with busnum=1
# display = SevenSegment.SevenSegment(address=0x74, busnum=2)

# Initialize the display. Must be called once before using the display.
display3.begin()
display2.begin()
display1.begin()
display0.begin()

# Keep track of the colon being turned on or off.

display3.clear()
display3.write_display()
display3.set_colon(True)
display3.write_display()

display2.clear()
display2.write_display()
display2.set_colon(True)
display2.write_display()

display1.clear()
display1.write_display()
display1.set_colon(True)
display1.write_display()

display0.clear()
display0.write_display()
display0.set_colon(True)
display0.write_display()

F0FF_string = "F0FF"
mode_switch = False

while True:
    if mode_switch:
        time_string = F0FF_string
    else:
        display_time = datetime.datetime.now()
        print(display_time)
        time_string = display_time.strftime("%H") + display_time.strftime("%M")
    
    
    display3.print_number_str(time_string, justify_right=True)
    display3.write_display()
    
    display2.print_number_str(time_string, justify_right=True)
    display2.write_display()
    
    display1.print_number_str(time_string, justify_right=True)
    display1.write_display()
    
    display0.print_number_str(time_string, justify_right=True)
    display0.write_display()
    
    time.sleep(1.0) 

# Run through different number printing examples.
print('Press Ctrl-C to quit.')

'''
numbers = [0.0, 1.0, -1.0, 0.55, -0.55, 10.23, -10.2, 100.5, -100.5]

while True:
    # Print floating point values with default 2 digit precision.
    for i in numbers:
        # Clear the display buffer.
        display.clear()
        # Print a floating point number to the display.
        display.print_float(i)
        # Set the colon on or off (True/False).
        display.set_colon(colon)
        # Write the display buffer to the hardware.  This must be called to
        # update the actual display LEDs.
        display.write_display()
        # Delay for a second.
        time.sleep(1.0)
    # Print the same numbers with 1 digit precision.
    for i in numbers:
        display.clear()
        display.print_float(i, decimal_digits=1)
        display.set_colon(colon)
        display.write_display()
        time.sleep(1.0)
    # Print the same numbers with no decimal digits and left justified.
    for i in numbers:
        display.clear()
        display.print_float(i, decimal_digits=0, justify_right=False)
        display.set_colon(colon)
        display.write_display()
        time.sleep(1.0)
    # Run through some hex digits.
    for i in range(0xFF):
        display.clear()
        display.print_hex(i)
        display.set_colon(colon)
        display.write_display()
        time.sleep(0.25)
    # Run through hex digits with an inverted (flipped upside down)
    # display.
    display.set_invert(True)
    for i in range(0xFF):
        display.clear()
        display.print_hex(i)
        display.set_colon(colon)
        display.write_display()
        time.sleep(0.25)
    display.set_invert(False)
    # For the large 1.2" 7-segment display only there are extra functions to
    # turn on/off the left side colon and the fixed decimal point.  Uncomment
    # to try them out:
    # To turn on the left side colon:
    #display.set_left_colon(True)
    # To turn off the left side colon:
    #display.set_left_colon(False)
    # To turn on the fixed decimal point (in upper right in normal orientation):
    #display.set_fixed_decimal(True)
    # To turn off the fixed decimal point:
    #display.set_fixed_decimal(False)
    # Make sure to call write_display() to make the above visible!
    # Flip colon on or off.
    colon = not colon
'''