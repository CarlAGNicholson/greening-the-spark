# Greening the Spark Grid Control System
# App: Representations calibration - wind turbine & sun lamp
# Version 1.0
# Date: 05/05/2021
# Author Carl Nicholson
#++++++++++++++++++++++

# Import standard libraries
#import math 
import time
import sys

 # Import GTS libraries (processes)
sys.path.append(r'/home/pi/Desktop/GTS')
import gts_lib
import gts_lib.logbook
log = gts_lib.logbook

# Initialise process
app = "RCal"
procedure ="main"
log.writeLog("Info",app,procedure,"Running representations calibration app.")

import pigpio
pi = pigpio.pi()

#Setup I2C for ADCs, used for FossilFuel and Nuclear Power control inputs
import smbus

try:
    bus = smbus.SMBus(1)
    address = 0x48
except FileNotFoundError: 
    procedure ="I2C"
    log.writeLog("ERROR",app,procedure,"I2C not enabled! Enable I2C in raspi-config.")
    
sys.path.append(r'/home/pi/RedBoard')
import redboard

#max_wind_speed = 80
max_motor_speed_15V = 40
#max_sun_intensity = 1000
max_sunlamp_value = 80 # at 15V

Clockwise = 0
WindTurbineMotorDir = 24
WindTurbineMotorPWMB = 25
SunLampMotorDir = 23
SunLampMotorPWMB = 18
 
# Read control pots in a loop
print("§ Get readings for wind turbine (red knob) and sun lamp (blue knob) gauges")
print()
print("§ Please turn the knobs back to zero before exiting with <ctrl> c.")
time.sleep(5)
print()

def start():
    while True:
        adc_1 = redboard.readAdc_1()
        adc_2 = redboard.readAdc_2()
        
        # convert 0 - 3,3V to 0 to 100% PWM
        wind_turbine_speed = adc_1 * 100 / 3.35
        sun_lamp_brightness = adc_2 * 100 / 3.35 -0.295
        if wind_turbine_speed > max_motor_speed_15V:
            wind_turbine_speed = max_motor_speed_15V
            print("$ Turbine speed limited to 40%.")
        
        pi.write(WindTurbineMotorDir, Clockwise)  # set motor direction
        pi.write(SunLampMotorDir, Clockwise)  # set motor direction
        
        pi.set_PWM_dutycycle(WindTurbineMotorPWMB,wind_turbine_speed)
        pi.set_PWM_dutycycle(SunLampMotorPWMB,sun_lamp_brightness)   

        print("red knob (V): %.2f; wind turbine: %.2f; blue knob (V): %.2f; sun lamp: %.2f." % (adc_1, wind_turbine_speed, adc_2, sun_lamp_brightness))

def end():
    procedure ="end"
    log.writeLog("Info",app,procedure,"Calibration complete.") 
 
try:
    start()

except KeyboardInterrupt:
    end()
    sys.exit(0)
 
