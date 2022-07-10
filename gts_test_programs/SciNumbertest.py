def formatSciNumber(number):
    #if number < 1.0e-9: number = 0.0
    sci_format = f"{number:.1e}"
    blinking = 0
    
    if sci_format[4] == "+":
        number_string = sci_format[:2] + sci_format[2:4] + sci_format[6]
        #decimal_point = 1
        colon = 0

    elif sci_format[4] == "-":
        number_string = sci_format[:2] + sci_format[2:3] + "-" + sci_format[6]
        #decimal_point = 1
        colon = 0
    else:
        #logbook.writeLog("ERROR", app, procedure, "Formatting error in sign field " + sci_format[4])
        print("ERROR - Formatting error in sign field " + sci_format[4])
          
    return(number_string, colon, blinking)

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
    return number_string, colon, blinking
      
number = 110000
number_string, colon, blinking = formatPositiveNumber4digit(number)
print(number_string, colon, blinking)

for i in range(-10,11):
    number = 1.34567 * 10**i
    number_string, colon, blinking = formatPositiveNumber4digit(number)
    print(number_string, colon, blinking)
    
number = 88888
number_string, colon, blinking = formatPositiveNumber4digit(number)
print(number_string, colon, blinking)
'''


number = 1.2e2
test(number)

number = 1.2e-2
test(number)

number = 6.7e8
test(number)

number = 7.8e-9
test(number)

number = 1.2e12
test(number)

number = 1.2e-12
test(number)

number = 12345
test(number)
'''
