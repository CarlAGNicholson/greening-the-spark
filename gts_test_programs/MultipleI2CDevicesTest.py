# Greening the Spark Grid Control System
# Application: Multiple I2C devices test program
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

        
def test1():

    print("§ 3. Setting LED bars from level 0 to 100 & getting mode switch position...")
    step = 5
    
    MODE_SWITCH_PIN = BATTERIES_STATUS.get_pin(8)
    MODE_SWITCH_PIN.direction = digitalio.Direction.INPUT# Button on AW io 1
    
    for value in range(0,1001,step):
        #print("§ level: ", value/10)
        setLEDbar(BATTERIES_STATUS, value/10)
        setLEDbar(HYDRO_STATUS, value/10)
        MODE_SWITCH_POSITION = MODE_SWITCH_PIN.value
        print(MODE_SWITCH_POSITION)
        time.sleep(0.001)
    time.sleep(2.0)
    print("§ LED bar test complete.")
    setLEDbar(BATTERIES_STATUS, 0)
    setLEDbar(HYDRO_STATUS, 0)
    print
    

# 7 seg stuff=================================================================
# Import standard libraries
import time
import datetime
import sys
#import smbus

sys.path.append(r'/home/pi/Adafruit')
#import HT16K33
import SevenSegment
# Create display instance on default I2C address (0x70) and bus number.
#display = SevenSegment.SevenSegment()


SevenSegmentDisplays = []
for display_number in range(4):
    
    # Create displays
    SevenSegmentDisplays.append(SevenSegment.SevenSegment(address=0x70 + display_number, busnum=1))
    
    # Initialise displays. (Must be called once before using the displays.)
    SevenSegmentDisplays[display_number].begin()
    SevenSegmentDisplays[display_number].clear()
    SevenSegmentDisplays[display_number].write_display()
    SevenSegmentDisplays[display_number].set_colon(True)
    SevenSegmentDisplays[display_number].write_display()

def test2():

    print("§ Running simple numeric header test")
    print('§ Press Ctrl-C to quit.')
    
    MODE_SWITCH_PIN = BATTERIES_STATUS.get_pin(8)
    MODE_SWITCH_PIN.direction = digitalio.Direction.INPUT# Button on AW io 1
    F0FF_string = "F0FF"

    while True:
        mode_switch = MODE_SWITCH_PIN.value
        if mode_switch:
            time_string = F0FF_string
        else:
            display_time = datetime.datetime.now()
            print(display_time)
            time_string = display_time.strftime("%H") + display_time.strftime("%M")
             
        for display_number in range(4):
            SevenSegmentDisplays[display_number].print_number_str(time_string, justify_right=True)
            SevenSegmentDisplays[display_number].write_display()
        
        time.sleep(1.0)

test1()
test2()



