# Greening the Spark Grid Control System
# Application: ADAFruit I2C GPIO expander and LED bar test program
# Version 1.0
# Date: 09/09/2021
# Author Carl Nicholson - adapted from:

# SPDX-FileCopyrightText: Copyright (c) 2020 ladyada for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import busio
import board
import adafruit_aw9523
import digitalio
import time

BATTERIES_I2C_ADDRESS = 0x58
HYDRO_I2C_ADDRESS = 0x59

#Set device to be tested
TEST_DEVICE_I2C_ADDRESS = BATTERIES_I2C_ADDRESS

i2c = busio.I2C(board.SCL, board.SDA)
BATTERIES_STATUS = adafruit_aw9523.AW9523(i2c,BATTERIES_I2C_ADDRESS)
HYDRO_STATUS = adafruit_aw9523.AW9523(i2c,HYDRO_I2C_ADDRESS)
#MODE_SWITCH = adafruit_aw9523.AW9523(i2c,BATTERIES_I2C_ADDRESS)
#MODE_SWITCH_PIN = MODE_SWITCH.get_pin(8)
#MODE_SWITCH_PIN.direction = digitalio.Direction.INPUT# Button on AW io 1

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
    
    #LED_MAX = divmod(int(level)+10,11)[0]
    if level == 0:
        LED_MAX = 0
    elif level == 100:
        LED_MAX = 10
    else:
        LED_MAX = divmod(level,12.5)[0] + 1
        
    #print("§ LED_MAX = ", LED_MAX)
    
    for LED in range(1,11):
        #print("§ LED, PIN: ", LED, LED2PIN[LED])
        if LED <= LED_MAX:
            aw.set_constant_current(LED2PIN[LED], LED_bar_brightness[LED])
        else:
            aw.set_constant_current(LED2PIN[LED], 0)
        time.sleep(0.001)

def test1(): # LED bar accuracy test

    print("§ test 1 - storage status LED bar arrays accuracy")
    print("§ 1. Setting LED bars to levels 0 (batteries) and 100 (hydro)")    
    setLEDbar(BATTERIES_STATUS, 100)
    setLEDbar(HYDRO_STATUS, 0)
    time.sleep(2.0)
    
    print("§ 2. Setting LED bars to levels 100 (batteries) and 0 (hydro)")    
    setLEDbar(BATTERIES_STATUS, 0)
    setLEDbar(HYDRO_STATUS, 100)
    time.sleep(2.0)
    
    print("§ 3. Setting LED bars from level 0 to 100...")
    step = 10
    for value in range(0,1001,step):
        #print("§ level: ", value/10)
        setLEDbar(BATTERIES_STATUS, value/10)
        setLEDbar(HYDRO_STATUS, value/10)
        time.sleep(0.0001)
    time.sleep(2.0)
    print("§ LED bar test complete.")
    setLEDbar(BATTERIES_STATUS, 0)
    setLEDbar(HYDRO_STATUS, 0)
    print
    

def test2(): # Input test - mode switch
    print("§ test 2 - input mode switch for 7 seg displays")
    print("§ Running in 2s ...")
    time.sleep(2.0)
    MODE_SWITCH = adafruit_aw9523.AW9523(i2c,BATTERIES_I2C_ADDRESS)
    MODE_SWITCH_PIN = MODE_SWITCH.get_pin(8)
    MODE_SWITCH_PIN.direction = digitalio.Direction.INPUT# Button on AW io 1
    while True:    
        MODE_SWITCH_POSITION = MODE_SWITCH_PIN.value
        print(MODE_SWITCH_POSITION)
        time.sleep(0.1)
        
def test3():

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
        
# Test initiation
    
#test1() # LED bar test
        
#test2() # Input test - mode switch

test3()

