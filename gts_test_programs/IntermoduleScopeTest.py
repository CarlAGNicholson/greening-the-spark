# Import standard libraries
import sys

print("§ test starting app.")

# Set GTS filepath 
if sys.platform == 'win32':
    gts_filepath = "D:\Projects\Greening the Spark\GTS" #WindowsPC

else:
    gts_filepath = r'/home/pi/Desktop/GTS' # set RPi pathname

sys.path.append(gts_filepath) # Windows

# Import GTS libraries

import gts_lib
import sys
import time as t
import datetime as dt
import keyboard

import gts_lib.intermodule_scope_test_library as lib

print(lib.John.age)
print(lib.James.age)

print(lib.John.runClown())
print(lib.James.runClown())

print(lib.John.runClown())
print(lib.James.runClown())

print(lib.John.runClown())
print(lib.James.runClown())



'''

#from gts_lib.intermodule_scope_test_library import John

FullConfiguration = [{"first":1,"second":2},{"third":3,"fourth":4}]

for dataset in FullConfiguration:
    #print("§ glob : ", dataset)
#    print("§ glob ", dataset.items())
#    print("§ glob ", dataset.keys())
#    print("§ glob ", dataset.values())



    for item in dataset.keys():
        print("§ glob : ", item, dataset[item])



for i in range(10):
    lib.increment()
    print(lib.lib_variable)
'''
#John.description("long")
#John.description("short")

