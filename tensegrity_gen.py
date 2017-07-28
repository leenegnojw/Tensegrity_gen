# Tensegrity generator
# All lengths are in mm with the "leg" aligned to the z-axis. 
# STL processing based on https://pypi.python.org/pypi/numpy-stl
# numpy-stl license: BSD
# made with python 2.7.6, numpy 1.13.1, matplotlib 2.0.2, numpy-stl 2.3.2

# of course, experiment with your own stl input files.  

import math
import tensegrity_geom as tg 

FILE_OUT_0 = 'gen_stl/floating_tensegrity_leg.stl'
FILE_OUT_1 = 'gen_stl/contact_tensegrity_leg.stl'

# Based on standard Ultimaker printers(mm):
MAX_LEG = 200
MAX_CORD = MAX_LEG*(1/math.sqrt(3))
MIN_CORD = 30
MIN_LEG = 30 

print "----------------------"
print "--- Tensegrity_gen ---"
print "----------------------\n"

print "Make a selection, if you want to generate the 'floating'(0)\nor 'contact'(1) tensegrity structure.\nAny other key will exit the program."
selec = int(raw_input("Please enter your choice: 0 or 1: ")) 
print ""

if selec == 0:
    print"--- Tensegrity_float ---\n"
    print"This tiny program generates stl files to be assembled into a floating tensegrity structure. \
    Building these things can be quite hard so to help, you can enter a simple cord length where-after the to-be-printed parts are generated.\n" 
    print"The advised cord length is around 60mm, but make sure it is at least 12mm. \
    The upper bound depends on your printer, but note that 115mm cord length already results in a triangle leg of 200mm(standard printer dimension!)\n" 

    cordL = float(raw_input("Please enter your desired cord length(mm): ")) 

    print "you entered", cordL
    while cordL<=MIN_CORD or cordL>=MAX_CORD: 
        print "Please enter a number above", MIN_CORD,"(mm) and below", MAX_CORD,"(mm)"  
        cordL = float(raw_input("Enter your desired cord length(mm): ")) 
    tg.gen_stl(cordL,FILE_OUT_0,selec)

elif selec == 1: 
    print"--- Tensegrity_contact ---\n"
    print"This tiny program generates the stl files needed to assemble your contact-based tensegrity structure. \
    You have to supply the length of the triangle leg and the corresponding thickness(radius of the polygon) will \
    be computed where-after the stl file is generated.\n"
    print"The advised length is around 100mm.\n"
    triangleL = float(raw_input("Please enter your desired triangle-leg length(mm): ")) 

    print "you entered", triangleL 
    while triangleL<=MIN_LEG or triangleL>=MAX_LEG: 
        print "Please enter a number above", MIN_LEG,"(mm) and below", MAX_LEG,"(mm)"  
        triangleL = float(raw_input("Enter your desired cord length(mm): ")) 
    tg.gen_stl(triangleL,FILE_OUT_1,selec)

else:
    print"End of the program." 

