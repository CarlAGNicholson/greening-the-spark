# Greening the Spark Grid Control System
# Application: calibrate servos for power and changes gauges
# Version 1.0
# Date: 05/05/2021
# Author Carl Nicholson

# Import standard libraries
import time
import sys

# Import GTS libraries (processes)
sys.path.append(r'/home/pi/Desktop/GTS')
import gts_lib 
import gts_lib.device_drivers
import gts_lib.logbook

# Process link abbreviations

dd = gts_lib.device_drivers
log = gts_lib.logbook

# Initialise process
app = "calGauges"
procedure = "main"

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

print("§ Get readings for power (red knob) and changes (blue knob) gauges")
log.writeLog("Info",app,procedure,"Running gauge servos calibration app.")

def start():
    while True:
        adc_1 = redboard.readAdc_1()
        adc_2 = redboard.readAdc_2()
        #adc_3 = redboard.readAdc_3()
        
        # convert 0 - 3,3V to -90 to +90 (roughly)
        power_servo_position = -80 + adc_1 * 60 + (adc_2 - 1.5) * 4
        changes_servo_position = power_servo_position
        
        redboard.servo27(power_servo_position)
        redboard.servo13(changes_servo_position)
        redboard.servo6(power_servo_position)
        redboard.servo5(changes_servo_position)
        redboard.servo11(power_servo_position)
        redboard.servo10(changes_servo_position)
        redboard.servo9(power_servo_position)
        redboard.servo8(changes_servo_position)

        print("red knob (V): %.2f; blue knob (V): %.2f; gauge: %.2f." % (adc_1, adc_2, power_servo_position))

        time.sleep(0.1)
        
def end():
    log.writeLog("Info",app,procedure,"App terminated successfully.")

try:
    start()

except KeyboardInterrupt:
    end()
    sys.exit(0)


