# Greening the Spark Grid Control System
# Library: device drivers, interface between software models and external hardware
# Version 2.0
# Date: 27/01/2022
# Author Carl Nicholson

# Change log
# 27/01/22 Release of V2 for development

# To do list - also search for "TBD"s
# TBD Implement expansion board I/O mapping
# TBD Implement error trapping for offline hardware

# Import standard libraries
import time
import sys

# Import third party libraries
# Adafruit
import busio
import board
import adafruit_aw9523
import digitalio

sys.path.append(r'/home/pi/Adafruit')
#import HT16K33
import SevenSegment

# expander stuff=================================================================
AW1_I2C_ADDRESS = 0x58
AW2_I2C_ADDRESS = 0x59
i2c = busio.I2C(board.SCL, board.SDA)
AW1 = adafruit_aw9523.AW9523(i2c,AW1_I2C_ADDRESS)
AW2 = adafruit_aw9523.AW9523(i2c,AW2_I2C_ADDRESS)
#print("Found AW9523")
# Set all LED bar pins to outputs and LED (const current) mode
LEDBAR_MASK = 0x70FE
AW1.LED_modes = LEDBAR_MASK
AW1.directions = LEDBAR_MASK
AW2.LED_modes = LEDBAR_MASK
AW2.directions = LEDBAR_MASK

# Calibrate brightness & map LEDs to pins
LED_bar_brightness = [0,16,16,16,32,32,4,4,4,4,4]
LED2PIN = [0,1,2,3,4,5,6,7,12,13,14]
IO2PIN = [0,8,9,10,11,0,15]

MODE_SWITCH_PIN = AW1.get_pin(8)
MODE_SWITCH_PIN.direction = digitalio.Direction.INPUT

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

# Redboard 
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


# Initialise process
app = "I2CTP"
procedure = "main"


# Import GTS libraries
if sys.platform == 'win32':
    gts_filepath = "D:\Projects\Greening the Spark\GTS" #WindowsPC
else:
    gts_filepath = r'/home/pi/Desktop/GTS' # set RPi pathname

sys.path.append(gts_filepath)
import gts_lib
#import gts_lib.device_drivers as dd
import gts_lib.logbook as log

# Initialise process
app = "device drivers"
procedure = "main"

# Constant definitions

CLOCKWISE = 0
WIND_TURBINE_MOTOR_DIR = 24
WIND_TURBINE_MOTOR_PWMB = 25
SUN_LAMP_MOTOR_DIR = 23
SUN_LAMP_MOTOR_PWMB = 18

GRID_STATUS_INDICATOR_PINS = {}
GRID_STATUS_INDICATOR_PINS["RED"] = 4
GRID_STATUS_INDICATOR_PINS["AMBER"] = 7

# Reference only
#WIND_POWER_GAUGE = 27
#WIND_CHANGES_GAUGE = 13
#SOLAR_POWER_GAUGE = 6
#SOLAR_CHANGES_GAUGE = 5
#DEMAND_POWER_GAUGE = 11
#DEMAND_CHANGES_GAUGE = 10
#FOSSILFUEL_POWER_GAUGE = 9
#NUCLEAR_POWER_GAUGE = 8
#FOSSIL_FUELS_CONTROL_INPUT = 1
#NUCLEAR_CONTROL_INPUT = 2

# Initialise representations
pi.write(WIND_TURBINE_MOTOR_DIR, CLOCKWISE)  # set motor direction
pi.write(SUN_LAMP_MOTOR_DIR, CLOCKWISE)  # set motor direction

# Initialise indicators
pi.set_mode(GRID_STATUS_INDICATOR_PINS["AMBER"], pigpio.OUTPUT)
pi.set_mode(GRID_STATUS_INDICATOR_PINS["RED"], pigpio.OUTPUT)
pi.set_pull_up_down(GRID_STATUS_INDICATOR_PINS["AMBER"], pigpio.PUD_DOWN)
pi.set_pull_up_down(GRID_STATUS_INDICATOR_PINS["RED"], pigpio.PUD_DOWN)


def setGauge(element, gauge_type, position): # note: gauge_type not used, as there is no difference in the code.
    procedure = "setGauge"
    DEBUG_LOOP = False
    if DEBUG_LOOP: print("§ DD servo {} position {:.2f}".format(element, position))
    
    if element == "wind":
        #if DEBUG_LOOP: log.writeLog("Info",app,procedure, "Wind power gauge set to {value:.2f}".format(value = position))
        redboard.servo27(position)
    elif element == "solar":
        #if DEBUG_LOOP: log.writeLog("Info",app,procedure, "Solar power gauge set to {value:.2f}".format(value = position))
        redboard.servo6(position)
    elif element == "demand":
        #if DEBUG_LOOP: log.writeLog("Info",app,procedure, "Demand power gauge set to {value:.2f}".format(value = position))
        redboard.servo11(position)

    elif element == "wind_forecast":
        #if DEBUG_LOOP: log.writeLog("Info",app,procedure, "Wind forecast gauge set to {value:.2f}".format(value = position))
        redboard.servo13(position)
    elif element == "solar_forecast":
        #if DEBUG_LOOP: log.writeLog("Info",app,procedure, "Solar forecast gauge set to {value:.2f}".format(value = position))
        redboard.servo5(position)
    elif element == "demand_forecast":
        #if DEBUG_LOOP: log.writeLog("Info",app,procedure, "Demand predicted gauge set to {value:.2f}".format(value = position))
        redboard.servo10(position)      
        
    elif element == "fossil_fuels":
        #if DEBUG_LOOP: log.writeLog("Info",app,procedure, "Fossil fuels power gauge set to {value:.2f}".format(value = position))
        redboard.servo9(position)        
    elif element == "nuclear":
        #if DEBUG_LOOP: log.writeLog("Info",app,procedure, "Nuclear power gauge set to {value:.2f}".format(value = position))
        redboard.servo8(position)      
    else:
        log.writeLog("ERROR", app, procedure, "Unknown element " + element + " - sim aborted.")

def setRepresentation(value, representation):
    procedure = "setRep"
    if representation == "wind":
        pi.set_PWM_dutycycle(WIND_TURBINE_MOTOR_PWMB,value)
    elif representation == "solar":
        pi.set_PWM_dutycycle(SUN_LAMP_MOTOR_PWMB,value)
    else:
        log.writeLog("ERROR",app,procedure,"Unknown representation " + representation + " - sim aborted.")

def readControl(element, control_type): # note: control_type not used, as there is only one: potentiometer.
    procedure = "readControl"
    if element == "fossil_fuels":
        #log.writeLog("Info",app,procedure, "Getting fossil fuel control.")
        control = redboard.readAdc_1()
    elif element == "nuclear":
        #log.writeLog("Info",app,procedure, "Getting nuclear control.")
        control = redboard.readAdc_2()
    else:
        log.writeLog("ERROR",app,procedure,"Unknown element " + element + " - sim aborted.")

    #print("red knob (V): %.2f; wind turbine: %.2f; blue knob (V): %.2f; sun lamp: %.2f." % (adc_1, wind_turbine_speed, adc_2, sun_lamp_brightness))   
    return control

def setStorageStatusIndicator(name, level):
# Set the LED bar array to display the level

    def setLEDbar(aw,level):
        '''
        0 = empty (no bars on) to full (all bars on)
        PIN 1 = red, pin 10 = blue '''

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
        
    procedure = "setSSI"
    DEBUG_LOOP = False
    if DEBUG_LOOP: print("§ setSSI", name, level)    
    if 0.0 <= level <= 100.0:
        if name == "batteries":
            setLEDbar(AW1,level)            
        elif name == "hydro":
            setLEDbar(AW2,level)  
        else:
            log.writeLog("ERROR",app,procedure, "Invalid storage name", name) 
    else:
        log.writeLog("ERROR",app,procedure, name + " storage level out of range (0 - 1)")  
    #print("§ dd setSSI setting status indicator", name, "with value %.2f" % (level))

def setGridStatusIndicator(name, value):
    procedure = "setGSI"
    #print("§ dd setGSI setting status indicator", name, "with value", value)
    if name == "RED" or name == "AMBER":
        #print("§ dd setGSI pi.read before", pi.read(GRID_STATUS_INDICATOR_PINS[name]))
        pi.write(GRID_STATUS_INDICATOR_PINS[name], value)
        #print("§ dd setGSI pi.read after", pi.read(GRID_STATUS_INDICATOR_PINS[name]))
    elif name == "GREEN":
        #print("§ dd setGSI to green no action required")
        pass
    else:
        logbook.writeLog("ERROR", app, procedure, "Invalid grid status LED colour" + value)


def setNumericHeader(header_strings):
    ''' Update numeric data header as follows:
    switch up:   [clock hh:mm, frequency dd.dd, CO2 d.d"e"e, cost d.d"e"e]
    switch down: [wind d.d"e"e, solar d.d"e"e, fossil fuels d.d"e"e, nuclear d.d"e"e]
    '''
    procedure = "setNumHead"
    for display_number in range(4):
        header_string = header_strings[display_number][0]
        #header_stop = header_strings[display_number][1]
        header_colon = header_strings[display_number][1]
        header_blinking = header_strings[display_number][2]
        #print("§ header string, stop, colon", header_string, header_stop, header_colon)   
        if header_colon == 1:
            SevenSegmentDisplays[display_number].set_colon(True)
            SevenSegmentDisplays[display_number].write_display()
        elif header_colon == 0:
            SevenSegmentDisplays[display_number].set_colon(False)
            SevenSegmentDisplays[display_number].write_display()
        else:
            log.writeLog("ERROR",app,procedure, "Invalid value for set_colon", header_colon)
            
        if header_blinking == 1:
            SevenSegmentDisplays[display_number].set_blink(SevenSegment.HT16K33.HT16K33_BLINK_2HZ)
        elif header_blinking == 0:
            SevenSegmentDisplays[display_number].set_blink(False) #print("§ setNH header string ", header_strings[mode_switch][display_number][0],mode_switch,display_number)
        else:
            log.writeLog("ERROR",app,procedure, "Invalid value for set_blink", header_blinking)
   
        SevenSegmentDisplays[display_number].print_number_str(header_string, justify_right=True)
        SevenSegmentDisplays[display_number].write_display()
