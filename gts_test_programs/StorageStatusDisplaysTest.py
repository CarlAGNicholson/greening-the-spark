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


    step = 5
    
    print("§ 1. Setting all LED bars on.")
    setLEDbar(BATTERIES_STATUS, 100)
    time.sleep(1.0)
    setLEDbar(HYDRO_STATUS, 100)
    time.sleep(1.0)
    print("§ 2. Setting LED bars off.")
    setLEDbar(BATTERIES_STATUS, 0)
    time.sleep(1.0)
    setLEDbar(HYDRO_STATUS, 0)
    time.sleep(1.0)
    print("§ 3. Setting LED bars from level 0 to 100...")
    for value in range(0,1001,step):
        #print("§ level: ", value/10)
        setLEDbar(BATTERIES_STATUS, value/10)
        setLEDbar(HYDRO_STATUS, value/10)
        time.sleep(0.001)
    time.sleep(2.0)
    print("§ LED bar test complete.")
    setLEDbar(BATTERIES_STATUS, 0)
    setLEDbar(HYDRO_STATUS, 0)
    print
    
test1()




