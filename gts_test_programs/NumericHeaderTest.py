# Greening the Spark Grid Control System
# Application: Numeric header test
# Version 1.0
# Date: 14/09/2021
# Author Carl Nicholson - adapted from:

# SPDX-FileCopyrightText: Copyright (c) 2020 ladyada for Adafruit Industries
#
# SPDX-License-Identifier: MIT



import busio
import board
import adafruit_aw9523
import digitalio
import time

# Import standard libraries
#import time
import datetime
import sys
#import smbus

sys.path.append(r'/home/pi/Adafruit')
#import HT16K33
import SevenSegment

# expander stuff=================================================================
BATTERIES_I2C_ADDRESS = 0x58
HYDRO_I2C_ADDRESS = 0x59
#Set device to be tested
TEST_DEVICE_I2C_ADDRESS = BATTERIES_I2C_ADDRESS
i2c = busio.I2C(board.SCL, board.SDA)
BATTERIES_STATUS = adafruit_aw9523.AW9523(i2c,BATTERIES_I2C_ADDRESS)
HYDRO_STATUS = adafruit_aw9523.AW9523(i2c,HYDRO_I2C_ADDRESS)
print("Found AW9523")
# Set all pins to outputs and LED (const current) mode
LEDBAR_MASK = 0x70FE
BATTERIES_STATUS.LED_modes = LEDBAR_MASK
BATTERIES_STATUS.directions = LEDBAR_MASK
HYDRO_STATUS.LED_modes = LEDBAR_MASK
HYDRO_STATUS.directions = LEDBAR_MASK

# Calibrate brightness & map LEDs to pins
LED_bar_brightness = [0,16,16,16,32,32,4,4,4,4,4]
LED2PIN = [0,1,2,3,4,5,6,7,12,13,14]
IO2PIN = [0,8,9,10,11,0,15]

MODE_SWITCH_PIN = BATTERIES_STATUS.get_pin(8)
MODE_SWITCH_PIN.direction = digitalio.Direction.INPUT# Button on AW io 1

# Create display instances on default I2C address (0x70+) and bus number.

SevenSegmentDisplays = []
for display_number in range(4):
    
    # Create displays
    SevenSegmentDisplays.append(SevenSegment.SevenSegment(address=0x73 - display_number, busnum=1))
    
    # Initialise displays. (Must be called once before using the displays.)
    SevenSegmentDisplays[display_number].begin()
    SevenSegmentDisplays[display_number].clear()
    SevenSegmentDisplays[display_number].write_display()
    SevenSegmentDisplays[display_number].set_colon(True)
    SevenSegmentDisplays[display_number].write_display()
    
# Initialise numeric header data  
header_strings = [] # in control panel
for display_number in range(4):
    header_strings.append("")

def setLEDbar(aw,level):
# Set the LED bar array to match the level
# 0 = empty (no bars on) to full (all bars on)
# PIN 1 = red, pin 10 = blue
    if level == 0:
        LED_MAX = 0
    elif level == 100:
        LED_MAX = 10
    else:
        LED_MAX = divmod(level,12.5)[0] + 1
    for LED in range(1,11):
        if LED <= LED_MAX:
            aw.set_constant_current(LED2PIN[LED], LED_bar_brightness[LED])
        else:
            aw.set_constant_current(LED2PIN[LED], 0)
        time.sleep(0.001)
# end of expander stuff========================================================

# 7 seg stuff=================================================================


def setNumericHeader(header_strings):
    ''' Update numeric data header as follows:
        switch up:   [clock hh:mm, frequency dd.dd, CO2 d.d"e"e, cost d.d"e"e]
        switch down: [wind d.d"e"e, solar d.d"e"e, fossil fuels d.d"e"e, nuclear d.d"e"e]   
    '''

    #F0FF_string = "F0FF"
    #print("§ set Header_strings", header_strings)

    for display_number in range(4):
        #print("int mode_switch", int(mode_switch))
        #print("§ mode, display", display_number)
        #print("header string", header_strings[mode_switch][display_number][0])
        header_string = header_strings[display_number][0]
        header_colon = header_strings[display_number][1]
        header_blinking = header_strings[display_number][2]
        
        #header_blinking = False
        #print("§ header string, stop, colon", header_string, header_stop, header_colon)
    
        if header_colon == 1:
            SevenSegmentDisplays[display_number].set_colon(True)
            SevenSegmentDisplays[display_number].write_display()
        elif header_colon == 0:
            SevenSegmentDisplays[display_number].set_colon(False)
            SevenSegmentDisplays[display_number].write_display()
        else:
            print("Invalid value for set colon", header_colon)
            
        if header_blinking == 1:    
            SevenSegmentDisplays[display_number].set_blink(SevenSegment.HT16K33.HT16K33_BLINK_2HZ)
        else:
            SevenSegmentDisplays[display_number].set_blink(False)

            
#print("§ setNH header string ", header_strings[mode_switch][display_number][0],mode_switch,display_number)
        SevenSegmentDisplays[display_number].print_number_str(header_string, justify_right=True)
        #SevenSegmentDisplays[display_number].print_number_str("2.1f", justify_right=True)
        SevenSegmentDisplays[display_number].write_display()
        

#SevenSegmentDisplays[display_number].print_number_str("22e8", justify_right=True)
        #+SevenSegmentDisplays[display_number].write_display() 
        #time.sleep(0.1)        mode_switch = int(MODE_SWITCH_PIN.value)

def writeNumericHeader(mode_switch, \
                       sim_time, \
                       frequency, \
                       total_CO2, \
                       total_cost, \
                       total_wind_energy, \
                       total_solar_energy, \
                       total_fossil_fuels_energy, \
                       total_nuclear_energy):

    def formatSciNumber(number):
        blinking = 0
        sci_format = f"{number:.1e}"
            
        if sci_format[4] == "+":
            number_string = sci_format[:2] + sci_format[2:4] + sci_format[6]
            colon = 0

        elif sci_format[4] == "-":
            number_string = sci_format[:2] + sci_format[2:3] + "-" + sci_format[6]
            colon = 0
        else:
            #logbook.writeLog("ERROR", app, procedure, "Formatting error in sign field " + sci_format[4])
            print("ERROR - Formatting error in sign field " + sci_format[4])
                  
        return number_string

    def formatPositiveNumber4digit(number):
        procedure = "fmtPosNum"
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
            #logbook.writeLog("ERROR", app, procedure, "Number out of range (>= 10^10)")
            print("ERROR - number out of range: ", number)
        #print("§ fPN4 ", number, number_string)
        return (number_string, colon, blinking)

    def formatFrequency(number):
        real_format = f"{number:2.2f}"
        if real_format[2] != "." or len(real_format) != 5:
            print("Invalid frequency format", real_format)
        else:
            number_string = real_format
            colon = 0
            blinking = 0
          
        return (number_string, colon, blinking)

    def formatSimClock(sim_time):
        number_string = sim_time.strftime("%H") + sim_time.strftime("%M")
        colon = 1
        blinking = 0
          
        return (number_string, colon, blinking)
    
    # format data strings
    if mode_switch == 0:
        header_strings[0] = formatSimClock(sim_time)
        header_strings[1] = formatFrequency(frequency)
        header_strings[2] = formatPositiveNumber4digit(total_CO2)
        header_strings[3] = formatPositiveNumber4digit(total_cost)
    elif mode_switch == 1: 
        header_strings[0] = formatPositiveNumber4digit(total_wind_energy)
        header_strings[1] = formatPositiveNumber4digit(total_solar_energy)
        header_strings[2] = formatPositiveNumber4digit(total_fossil_fuels_energy)
        header_strings[3] = formatPositiveNumber4digit(total_nuclear_energy)
    else:
        print("§ log error, invalid mode switch position", mode_switch)

    #print("§ write Header_strings", header_strings)

    setNumericHeader(header_strings)

def updateControlPanel(sim_time, \
                       frequency, \
                       total_CO2, \
                       total_cost, \
                       total_wind_energy, \
                       total_solar_energy, \
                       total_fossil_fuels_energy, \
                       total_nuclear_energy):

    # get switch position
    mode_switch = int(MODE_SWITCH_PIN.value)
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

#Grid_model substitute
print("§ Running numeric header prototype")

# Data from grid module:
# Upper values

frequency = 49.00
total_CO2 = 1.0e-10
total_cost = 1.0e-10

# Lower values
total_wind_energy = 1.0e-5
total_solar_energy = 1.0e-5
total_fossil_fuels_energy = 1.0e-5
total_nuclear_energy = 1.0e-5

while True:
    #mode_switch = int(MODE_SWITCH_PIN.value)
    print("CO2 : ", total_CO2, "; cost : ", total_cost)
    sim_time = datetime.datetime.now()
    updateControlPanel(sim_time, \
                       frequency, \
                       total_CO2, \
                       total_cost, \
                       total_wind_energy, \
                       total_solar_energy, \
                       total_fossil_fuels_energy, \
                       total_nuclear_energy)

    frequency += 0.01
    total_CO2 *= 3.3
    total_cost *= 3.3
    # Lower values
    total_wind_energy *= 3.3
    total_solar_energy *= 3.3
    total_fossil_fuels_energy *= 3.3
    total_nuclear_energy *= 3.3
    time.sleep(2.0)

