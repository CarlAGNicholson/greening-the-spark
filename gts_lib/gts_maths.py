# Greening the Spark Grid Control System
# Module: Maths
# Version 2.0
# Date: 27/01/2022
# Author Carl Nicholson

# Change log
# 08/02/22 Release of V2 for development

# To do list - search for "TBD"
# TBD use linterpolate in linterpolate1D and linterpolate1D in linterpolate2D

# Import standard libraries
import sys
import copy
from math import sqrt

# Set GTS filepath; must be set independently because cannot load globals

if sys.platform == 'win32':
    gts_filepath = "D:\Projects\Greening the Spark\GTS" #WindowsPC
else:
    gts_filepath = r'/home/pi/Desktop/GTS' # set RPi pathname

# Import GTS libraries
import gts_lib
import gts_lib.logbook as logbook

DEBUG = False
app = "maths"
procedure = "init"
logbook.writeLog("Info", app, procedure, "Maths initialised.")

# In use

def transpose2D(arg):
    '''Transposes matrix. Note: original restored by calling transpose again.'''
    matrix = isok2D(arg)
    #print("§ transpose isok result", matrix)
    if type(matrix) == type("string"):
        return matrix
    
    result = []
    for column_index in range(len(arg[0])):
        column = []
        for row in arg:
            column.append(row[column_index])
        result.append(column)			
    return result    


def float2D(arg):
    '''Converts all values to float or returns an error.'''
    try:
        return [[float(q) for q in m] for m in arg]            
    except:
        return "Error converting matrix element to float."

def isok2D(arg):
    '''Checks the homogeneity of the array, ie. all rows the same length.'''
    ok = True
    for row in arg:
        #print("§ isok ", row)
        ok &= len(row) == len(arg[0])
    #print("§ok = ",ok)
    if ok:
        return ok
    else:
        return "Array is not a regular 2D matrix."
    

def print2D(name, arg):
    '''Prints a user friendly display of a 2D array.'''
    if type(arg) == type("string"):
        print('§ string "', name, '" :', arg)

    else:
        row_number = 0
        for row in arg:
            print('§ array "', name, '" row ', row_number, ':', row, sep = "")
            row_number += 1
        print()

def print2DasCSV(name, array2D):
    '''Prints a CSV version of a 2D array with a title name.'''
    print(name, "as CSV:")
    for row in array2D:
        print(*row, sep = ",")
    #print()


def scalarop1D(n, arg_array1D, op = "*"):
    '''Transforms the elements of a 1D array by the scalar n and returns the resulting array.
    Allowed operations are *, /, + and -. Default is multiplication.'''

    if op == "*":
        return [m*n for m in arg_array1D]
    elif op == "/":
        if n == 0:
            return "Division by zero." 
        else:
            return [m/n for m in arg_array1D]
    elif op == "+":
        return [m+n for m in arg_array1D]
    elif op == "-":
        return [m-n for m in arg_array1D]
    else:
        return "Unknown operator."
    

def lfit_old(x, x1, x2, y1, y2):
    '''Linear fit, returns y value given x lying on line joining points (x1, y1) and (x2, y2)'''
    if x2 == x1:
        logbook.writeLog("ERROR", "mathslib", "lfit", "Division by zero.")
    return y1 + (x - x1) * (y2 - y1) / (x2 - x1)

def lfit(x, x1, y1, x2, y2):
    '''Linear fit, returns y value given x lying on line joining points (x1, y1) and (x2, y2)'''
    if x2 == x1:
        logbook.writeLog("ERROR",  "mathslib", "lfit", "Division by zero, two points have same x value.")
    return y1 + (x - x1) * (y2 - y1) / (x2 - x1)
    
def linterpolate(x1, x2, w):
    '''Linear interpolation between numbers x1 and x2 where w is the fraction x is between x1 and x2.'''
    return (1-w)*x1+ w*x2
    
def op1Don2D(arg_list, arg_array2D, op = "*", orientation = "r"):
    '''Performs multiplication ("*")/ division ("/")/ addition ("+") / subtraction ("-") on the
    elements of a 2D array by a list and returns the resulting array. Orientation:
        "r" means all elements of nth row of array operated on by nth member of the list
        "c" means nth element of each row operated on by nth member of the list.
    '''

    row_index = 0
    if orientation == "r":

        if len(arg_list) != len(arg_array2D):
            return "List length doesn't match number of array rows."
        for row in arg_array2D:
            if op == "*":
                arg_array2D[row_index] = scalarop1D(arg_list[row_index], arg_array2D[row_index],"*")
            elif op == "/":
                if arg_list[row_index] == 0:
                    return "Division by zero."
                else:
                    arg_array2D[row_index] = scalarop1D(arg_list[row_index], arg_array2D[row_index],"/")
            elif op == "+":
                arg_array2D[row_index] = scalarop1D(arg_list[row_index], arg_array2D[row_index],"+")
            elif op == "-":
                arg_array2D[row_index] = scalarop1D(arg_list[row_index], arg_array2D[row_index],"-")
            else:
                return "Unknown operator."
            row_index += 1
        return arg_array2D

    elif orientation == "c":

        trans = transpose2D(arg_array2D)
        inter = op1Don2D(arg_list, trans, op, "r")   
        return transpose2D(inter)
          
    else:
        return "Unknown orientation."

def getChanges2D(array2D):
    '''Gets changes calculated as differences between successive elements of a given row.'''

    result = []
    for row in array2D:
        #print("§ getChanges: ", row)
        for index in range(len(row)):
            #print("§ index: ", index)

            if index != len(row)-1:
                row[index] = row[index+1] - row[index]
            else:
                row[index] = row[index-1]
        #print("§ row ", row)
        final_row = row[:len(row)-1]
        result.append(final_row)

    return result

def getChanges(array1D):
    '''Changes are differences between successive elements of a list.
    Returns a list with one fewer members.
    '''
    result = []
    for index in range(len(array1D)-1):
        if index != len(array1D)-1:
            new_value = array1D[index+1] - array1D[index]
        else:
            #new_value = 0
            pass
        result.append(new_value)
    return result

def getChangesWrap(array1D):
    '''Changes are differences between successive elements of a list.
    Extra sample is wrapped to first to make up the number.
    '''
    result = []
    for index in range(len(array1D)):
        sample_plus_one = (index+1) % (len(array1D))
        sample = index % (len(array1D))
        new_value = array1D[sample_plus_one] - array1D[sample]
        #print("sample, array1D[sample+1], array1D[sample], value", sample, array1D[sample_plus_one], array1D[sample], new_value)
        result.append(new_value)
    return result

def getChangesExtrap(array1D):
    '''Changes are differences between successive elements of a list.
    Extra sample is extrapolated from last 2 to make up the number.
    '''
    result = []
    for index in range(len(array1D)):
        if index < len(array1D)-1:
            new_value = array1D[index+1] - array1D[index]
        else:
            new_value = 2* result[index-1] - result[index-2]
        #print("index, new value", index, new_value)
        result.append(new_value)
    return result

def getAggregates2D(array2D):
    '''Calculates min, max and max absolute values for each row in 2D array.'''
    Min = []
    Max = []
    MaxAbs = []
        
    for row in array2D:
        #print("§ Row: ", row)
        Min.append(min(row))
        Max.append(max(row))
    #print("§ Min: ", Min)
    #print("§ Max: ", Max)
    index = 0
        
    for element in Min:
        MaxAbsNext = max([abs(Min[index]),abs(Max[index])])
        MaxAbs.append(MaxAbsNext)
        index += 1
    #print("§ MaxAbs: ", MaxAbs)
    return Min, Max, MaxAbs

def maxabs(array):
    ''' Returns max of absolute values in a 1D array. '''
    maxabs = 0
    for value in array:
        if abs(value) > maxabs:
            maxabs = abs(value)
    return maxabs

def linterpolate2DArrays(array1, array2, w):
    ''' linear interpolation between elements of 2D array1 and 2D array2 where w is distance from array1'''
    result = copy.deepcopy(array1)
    for i in range(len(array1)):
        for j in range(len(array1[0])):
            result[i][j] = (1-w)*array1[i][j]+ w*array2[i][j]
    return result


# 2D arrays

def smultiply2DArray(n, array1):
    '''Multiplies the elements of array1 by the scalar n and returns the resulting array'''
    return [[q*n for q in m] for m in array1]

def vmaxabs2DArray(array1):
    '''Gets max absolute value of each column.'''
    vmax = copy.copy(array1[0])
    for i in range(len(vmax)):
        vmax[i] = 0
    for row in array1:
        for i in range(len(row)):
            if abs(row[i]) > abs(vmax[i]):
                vmax[i] = abs(row[i])
    return vmax

def vminabs2DArray(array1):
    '''Gets min absolute value of each column.'''
    vmin = copy.copy(array1[0])
    for row in array1:
        for i in range(len(row)):
            if abs(row[i]) < abs(vmin[i]):
                vmin[i] = abs(row[i])
    return vmin

def vnegative2DArray(array1):
    '''Checks to see if any negative values in each column, returns list of booleans.'''
    vnegative = copy.copy(array1[0])
    for i in range(len(vnegative)):
        vnegative[i] = False
    for row in array1:
        for i in range(len(row)):
            if (row[i]) < 0:
                vnegative[i] = True
    return vnegative

# 1D arrays

def check1DArrays(array1, array2):
    ''' checks that arrays are the same size'''
    error = len(array1) != len(array2)
    return not error

def rms1D(array):
    sum_of_squares = 0.0
    for i in range(0, len(array)):
        sum_of_squares += array[i]**2
    rms = sqrt(sum_of_squares / len(array))
    return rms

def rmsDiff1D(array1, array2):
    #print("§ array sizes:", len(array1), len(array2))
    #print("§ array 1:", array1)
    #print("§ array 2:", array2)
    if len(array1) != len(array2):
        logbook.writeLog("ERROR",  "mathslib", "rmsDiff1D", "Arrays must be the same size.")
    sum_of_squares = 0.0
    for i in range(0, len(array1)):
        sum_of_squares += (array1[i] - array2[i])**2
    rms = sqrt(sum_of_squares / len(array1))
    return rms
    
def linterpolate1DArrays(array1, array2, w):
    ''' linear interpolation between elements of 1D array1 and 1D array2 where w is the fraction x is between x1 and x2.'''
    #result = copy.deepcopy(array1)
    result = []
    #print("§ linterpolate array1 = ", array1)
    #print("§ linterpolate array2 = ", array2)
    #print("§ linterpolate weight = ", w)
    for i in range(len(array1)):
        #print("§ linterpolate i = ", i)
        #result[i] = (1-w)*array1[i]+ w*array2[i]
        interpolate = (1-w)*array1[i]+ w*array2[i]
        result.append(interpolate)
    #print("§ linterpolate result = ", result)
    return result

def vmultiply1DArrays(array1, array2):
    ''' elements of 1D array1 multiplied by corresponding elements of 1D array2'''
    #result = copy.deepcopy(array1)

    result = []
    for i in range(len(array1)):
        product = array1[i]*array2[i]
        result.append(product)

    return result

# mixed 1d & 2D

def check2Dby1DArrays(array1, array2):
    ''' checks that arrays are the same size'''
    error = len(array1[0]) != len(array2)
    return not error

def vmultiply2Dby1DArrays(array1, array2):
    ''' 1D array elements of 2D array1 multiplied by corresponding elements of 1D array2'''
    result = copy.deepcopy(array1)
    for row in result:
        for i in range(len(row)):
            row[i] = row[i]*array2[i]
    return result


# specials for test purposes

def op1Don2D_tests():

# op1Don2D tests

    print("§ Test 1")
    a1 = [[1,2,3,4],[2,3,4,5]]
    print2D("a1",a1)
    print2D("a1tr", transpose2D(a1))
    
    a2 = [[5,6],[7,8],[9,10],[11,12]]
    print2D("a2",a2)
    print2D("a2tr", transpose2D(a2))

    l1 = [1,100,1000,10000]
    print('§ list "l1 "',l1)
    l2 = [10,100]
    print('§ list "l2 "',l2)

    l3 = [0,100]
    print('§ list "l2 "',l3)

    print("§ test 1 - no errors")
    result = op1Don2D(l2, a1, op = "*", orientation = "r")
    print("§ result type = ", type(result))
    print("§ result = ", result)

    print("§ test 2 - unknown orientation ")
    result = op1Don2D(l2, a1, op = "*", orientation = "p")
    print("§ result type = ", type(result))
    print("§ result = ", result)

    print("§ test 3 - unkown operator")
    result = op1Don2D(l2, a1, op = "p", orientation = "r")
    print("§ result type = ", type(result))
    print("§ result = ", result)

    print("§ test 4 - division by zero")
    result = op1Don2D(l3, a1, op = "/", orientation = "r")
    print("§ result type = ", type(result))
    print("§ result = ", result)
  
def getchanges2D_tests():

    array2D = [[1,2,3,4,5,6],[0,0,0,0,0,0],[7,6,5,50,60,70]]
    print2D("power",array2D)
    result = getchanges2D(array2D)
    print2D("changes",result)

def transpose2D_tests():

    a1 = [[1,2,3,4,5,6],[0,0,0,0,0,0],[7,6,5,50,60,70]]
    print2D("regular",a1)
    a2 = [[1,2,3,4,5,6],[0,0,0,0,0],[7,6,5,50,60,70]]
    print2D("irregular",a2)
    tra1 = transpose2D(a1)
    print2D("regular",tra1)
    tra2 = transpose2D(a2)
    print("§ type: ", type(tra2))
    print("§ value: ", tra2)
    print2D("irregular",(tra2))
 

    '''
    mylist = [1,200,1000]
    print(op1Don2D(mylist, array2D, op = "*", orientation = "r"))
    print2D("test",array2D)    
          

    #print("check : ",check2D(array2D))

    
    


    a = [[1,-21,10],[4,5,-6]]
    vmax = vmaxabs2DArray(a)
    print("vmax: ", vmax)

    vmin = vminabs2DArray(a)
    print("vmin: ", vmin)
                                       
    vnegative = vnegative2DArray(a)
    print("vnegative: ", vnegative)


    a = [[1,2,3],[4,5,6]]
    b = [1,10,100]

    result = check2Dby1DArrays(a,b)
    print(result)
    result = vmultiply2Dby1DArrays(a,b)
    print(result)



   array = [[1,2,3,4,5,6,7,8],
            [2,3,4,5,6,7,8,9],
            [3,4,5,6,7,8,9,10]
            ]

    
    array1 = [1,2,3,4,5,6,7,8]
    array2 = [2,3,4,5,6,7,8,9]
    array3 = [3,4,5,6,7,8,9,10]
    array4 = [1,2,3,4,5,6,7,8,9,10] # will generate a mismatch error


    array1 = [[0, 0], [0, 0]]
    array2 = [[1, 1], [1, 1]]
    array3 = [[2, 2], [2, 2]]
    array4 = [[1, 2], [4, 5], [7, 8], [9,10]] # will generate a mismatch error
    
    print()
    print("Interpolation using 2 2D arrays")

    # row index goes up with the sample number
    # w goes up with the frame number

    row_index = 0
    for row in array:
        print("=" * 60)    
        print("row index = ",row_index)
        print("=" * 60)
        if row_index > 0:
            array1 = copy.copy(array2)
            array2 = copy.copy(row)
            for w in range(0,10):

                result = linterpolate1DArrays(array1, array2, w/10)
                print("-" * 60)
                print("w = ",w)
                print("a1 = ", array1)
                print("a2 = ", array2)
                print("result = ", [round(elem,2) for elem in result]) 
            
        else:
            array1 = copy.copy(row)
            array2 = copy.copy(array1)
            result = copy.copy(array2)
            print("§ Nothing happening yet...")

        result = copy.copy(array2)
        print("final result = ", [round(elem,2) for elem in result])
        row_index += 1


        
        # first interval
        w = 0.0
        for k in range(10):
            result = linterpolate1DArrays(array1, array2, w)
            print(round(w,2))
            print([round(elem,2) for elem in result])
            w += 0.1

            
        # second interval
        w = 0.0
        for k in range(2):
            result = linterpolate1DArrays(array2, array3, w)
            print(round(w,2))
            print([round(elem,2) for elem in result])
            w += 0.1




    if check1DArrays(array1, array2):
        # first interval
        w = 0.0
        for k in range(10):
            result = linterpolate1DArrays(array1, array2, w)
            print(round(w,2))
            print([round(elem,2) for elem in result])
            w += 0.1
            
    if check1DArrays(array2, array3):
        # second interval
        w = 0.0
        for k in range(2):
            result = linterpolate1DArrays(array2, array3, w)
            print(round(w,2))
            print([round(elem,2) for elem in result])
            w += 0.1

    else:
        result = False
        print("Arrays not compatible. Process halted")
        sys.exit   

    if check2DArrays(array1, array2):
        # first interval
        w = 0.0
        for k in range(10):
            result = linterpolate2DArrays(array1, array2, w)
            print(w)
            print(result)
            w += 0.1

        # second interval
        w = 0.0
        for k in range(10):
            result = linterpolate2DArrays(array2, array3, w)
            print(w)
            print(result)
            w += 0.1

    else:
        result = False
        print("Arrays not compatible. Process halted")
        sys.exit   



    print()
    print("Scalar multiplication of a 2D array")

    n = 5
    result = smultiply2DArray(n, array2)
    print(result)

'''    

def testChanges():
    a = [1,2,3,4,6,8,1,0,8,5,0]
    c = getChanges(a)
    print("a" , a)
    print("c" , c)


def start():
    #op1Don2D_tests()
    #getchanges2D_tests()
    #transpose2D_tests()
    testChanges()
    pass

if __name__ == "__main__":
    start()
