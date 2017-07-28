# Compute tensegrity geometry.
# All lengths are in mm with the "leg" aligned to the z-axis. 
# STL processing based on https://pypi.python.org/pypi/numpy-stl
# numpy-stl license: BSD
# made with python 2.7.6, numpy 1.13.1, matplotlib 2.0.2, numpy-stl 2.3.2

# Of course, experiment with your own stl input files.  

# See the pdf for some extra explanations. 

import math
import stl
from stl import mesh
import numpy as np 
from numpy import linalg as LA
import os 

from mpl_toolkits import mplot3d
from matplotlib import pyplot

STL_BASE = 'src_stl/base_10mm_6mm.STL'
STL_TIP = 'src_stl/tip_rad_6mm_inc_hole.STL'
STL_TIP_NO_HOLE = 'src_stl/tip_rad_6mm.STL'
RAD_BASE = 3 

def triangle_leg_length(cordL):
    print "---"
    print "cord length(mm):", cordL, ", triangle leg length(mm):", cordL*math.sqrt(3) 
    return cordL*math.sqrt(3)

def triangle_leg_rad(triangleL):
    # Solve a standard least squares problem, 
    # see the pdf for why this makes sense here. 
    l = triangleL 
    s = l/math.sqrt(3)

    a = np.matrix([[0],[s],[0]])
    b = np.matrix([[0.5*s],[-0.5*s],[0.5*math.sqrt(2)*s]])
    c = np.matrix([[0],[s],[math.sqrt(2)*s]])
    d = np.matrix([[0],[0],[0]])
    B = c-a
    A = np.matrix([[b[0,0]-a[0,0], c[0,0]-d[0,0]],\
        [b[1,0]-a[1,0], c[1,0]-d[1,0]],\
        [b[2,0]-a[2,0], c[2,0]-d[2,0]]]) 
    ATb = np.matmul(A.T,B)
    ATA = np.matmul(A.T,A)
    x = np.matmul(LA.inv(ATA),ATb)
    r=LA.norm(a*(1-x[0])+b*x[0]-c*(1-x[1])-d*x[1])/2
    print "Given l(mm)=", l, "the radius becomes r(mm)=", r  
    # We do not have a circle, thus apply the polygon scaling factor
    c = math.sqrt(5*math.cos(math.pi/5)*math.sin(math.pi/5)*(1/math.pi))
    r /= c 
    print "After polygon compensation r(mm)=", r 
    return r

# The following two functions are directly from numpy-stl:  
# https://pypi.python.org/pypi/numpy-stl

# Finding the max dimensions, useful in translations! 
def find_mins_maxs(obj):
    minx = maxx = miny = maxy = minz = maxz = None
    for p in obj.points:
        # p contains (x, y, z)
        if minx is None:
            minx = p[stl.Dimension.X]
            maxx = p[stl.Dimension.X]
            miny = p[stl.Dimension.Y]
            maxy = p[stl.Dimension.Y]
            minz = p[stl.Dimension.Z]
            maxz = p[stl.Dimension.Z]
        else:
            maxx = max(p[stl.Dimension.X], maxx)
            minx = min(p[stl.Dimension.X], minx)
            maxy = max(p[stl.Dimension.Y], maxy)
            miny = min(p[stl.Dimension.Y], miny)
            maxz = max(p[stl.Dimension.Z], maxz)
            minz = min(p[stl.Dimension.Z], minz)
    return minx, maxx, miny, maxy, minz, maxz

def translate(_solid, step, padding, multiplier, axis):
    if axis == 'x':
        items = [0, 3, 6]
    elif axis == 'y':
        items = [1, 4, 7]
    elif axis == 'z':
        items = [2, 5, 8]
    for p in _solid.points:
        # point items are ((x, y, z), (x, y, z), (x, y, z))
        for i in range(3):
            p[items[i]] += (step * multiplier) + (padding * multiplier)

def gen_stl(L, FILE_OUT, selec):
    # Load the stl files we scale based on the user input. 
    main_body_up = mesh.Mesh.from_file(STL_TIP)
    main_body_down = mesh.Mesh.from_file(STL_TIP)
    leg = mesh.Mesh.from_file(STL_BASE)

    if selec == 0:
        cordL = L 
        # Given the user input, calc the triangle leg length. 
        triangleL = triangle_leg_length(cordL) 
        # Note that the up and down parts do not scale, so we already have 2cm. 
        leg.z*=(triangleL-20)/10; 

        translate(main_body_up,(triangleL-20),0,1,'z')
        # Find the outer dimensions of our mesh: 
        minx, maxx, miny, maxy, minz, maxz = find_mins_maxs(main_body_down)
        x1 = maxx - minx
    
    elif selec == 1:
        ans = raw_input("Do you want a hole for assembly?(y/n) ")
        while ans != 'y' and ans != 'n':
            ans = raw_input("Please answer y or n ")
        if ans == 'n':
            print"You selected no"
            main_body_up = mesh.Mesh.from_file(STL_TIP_NO_HOLE)
            main_body_down = mesh.Mesh.from_file(STL_TIP_NO_HOLE)
        else:
            print"You selected yes"

        triangleL = L
        # Given the user input, calc the rad:  
        r = triangle_leg_rad(triangleL)
    
        # Scale the tips
        main_body_down.x*=(r/RAD_BASE)
        main_body_down.y*=(r/RAD_BASE)
        main_body_down.z*=(r/RAD_BASE)
        main_body_up.x*=(r/RAD_BASE)
        main_body_up.y*=(r/RAD_BASE)
        main_body_up.z*=(r/RAD_BASE)

        # Take the radius-based scaling into account. 
        leg.z*=(triangleL-(20/RAD_BASE)*r)/10; 
        leg.x*=(r/RAD_BASE)
        leg.y*=(r/RAD_BASE)

        # Find the outer dimensions of our mesh: 
        minx, maxx, miny, maxy, minz, maxz = find_mins_maxs(main_body_down)
        x1 = maxx - minx

        translate(main_body_up,(triangleL-(20/RAD_BASE)*r),0,1,'z')

    else:
        print"Fatal error"

    # Rotate the lower part and move it back in position.
    # The 0.5 is arbitrary(direction vec), see numpy-stl for more information. 
    main_body_down.rotate([0.0, 0.5, 0.0], math.radians(180))
    translate(main_body_down,x1,0,1,'x')

    # Put everything together and save your file (binary).
    # Check the part in favourite mesh editor or print it right away! 
    combined = mesh.Mesh(np.concatenate([main_body_up.data, leg.data, main_body_down.data]))
    combined.save(FILE_OUT)
    print FILE_OUT,"saved in", os.getcwd() 
    print "Good luck printing!"
    print ""

    # Show the STL 
    figure = pyplot.figure()
    axes = mplot3d.Axes3D(figure)
    axes.add_collection3d(mplot3d.art3d.Poly3DCollection(combined.vectors))

    # Auto scale to the mesh size
    scale = combined.points.flatten(-1)
    axes.auto_scale_xyz(scale, scale, scale)

    # Show the plot to the screen
    pyplot.title(FILE_OUT)
    pyplot.show()
