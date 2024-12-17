import re
import linecache
import os
import sys
import numpy as np
import math
import pandas as pd
import tkinter as tk
from tkinter import filedialog

xcoord1 = "x"
ycoord1 = "y"
zcoord1 = "z"

xcoord2 = "x"
ycoord2 = "y"
zcoord2 = "z"

xcoord3 = "x"
ycoord3 = "y"
zcoord3 = "z"

ax = 0.0
ay = 0.0
az = 0.0

bx = 0.0
by = 0.0
bz = 0.0

flag = 0

linenum = 0
pattern = re.compile("POINT")

def magnitude(vector):
    return math.sqrt(sum(pow(element, 2) for element in vector))

# with open('path/to/text.dxf', 'rt') as file:
# Create the root window
root = tk.Tk()
root.withdraw()

# Ask the user to select a file using a file dialog
file_path = filedialog.askopenfilename()

# Read the CSV file into a Pandas DataFrame
df = pd.read_csv(file_path)

#filename = input("Enter the file name: ")
# separate file name and extension
name, ext = os.path.splitext(file_path)
# add ".csv" extension to the file name
output_filename = name + ".csv"

fh = open(output_filename, 'w')

# read in groups of 3 pts on a plane

with open(file_path, 'r+') as file:
    for myline in file:
        linenum += 1
# find the first line with the entry 'POINT'
        if pattern.search(myline) != None and flag == 0:
            flag = 1
            i = 0
            # count number of lines below entry for 'POINT' to the first coordinate
            while i < 12:
                myline = file.readline()
                i += 1

            xcoord1 = myline
            myline = file.readline()
            myline = file.readline()

            ycoord1 = myline
            myline = file.readline()
            myline = file.readline()

            zcoord1 = myline

# find the second line with the entry 'POINT'
        if pattern.search(myline) != None and flag == 1:
            flag = 2
            i = 0
            # count number of lines below entry for 'POINT' to the first coordinate
            while i < 12:
                myline = file.readline()
                i += 1

            xcoord2 = myline
            myline = file.readline()
            myline = file.readline()
           
            ycoord2 = myline
            myline = file.readline()
            myline = file.readline()

            zcoord2 = myline
            
# find the third line with the entry 'POINT'
        if pattern.search(myline) != None and flag == 2:
            flag = 0
            i = 0
            # count number of lines below entry for 'POINT' to the first coordinate
            while i < 12:
                myline = file.readline()
                i += 1

            xcoord3 = myline
            myline = file.readline()
            myline = file.readline()

            ycoord3 = myline
            myline = file.readline()
            myline = file.readline()

            zcoord3 = myline

# cross product logic
            ax = float(xcoord2.strip("\n")) - float(xcoord1.strip("\n"))
            ay = float(ycoord2.strip("\n")) - float(ycoord1.strip("\n"))
            az = float(zcoord2.strip("\n")) - float(zcoord1.strip("\n"))
            bx = float(xcoord3.strip("\n")) - float(xcoord1.strip("\n"))
            by = float(ycoord3.strip("\n")) - float(ycoord1.strip("\n"))
            bz = float(zcoord3.strip("\n")) - float(zcoord1.strip("\n"))
            #cross product
            a = [ax,ay,az]
            b = [bx,by,bz]
            cross = np.cross(a,b)
# area of triangle defined by the three points
            area = magnitude(cross)
# unit normal vector to the plane defined by the three points
            unitnorm = [cross[0]/area, cross[1]/area, cross[2]/area]
# determine dip and dip direction
            if(unitnorm[2] < 0):
                unitnorm[0] = -unitnorm[0]
                unitnorm[1] = -unitnorm[1]
                unitnorm[2] = -unitnorm[2]

            dip = 90 - (180/np.pi)*np.arcsin(unitnorm[2])

            if(unitnorm[0] > 0 and unitnorm[1] > 0):
                dipdir = (180/np.pi)*np.arctan(unitnorm[0] / unitnorm[1])
            elif(unitnorm[0] < 0 and unitnorm[1] < 0):
                dipdir = 180 + (180/np.pi)*np.arctan(unitnorm[0] / unitnorm[1])
            elif(unitnorm [0] > 0 and unitnorm[1] < 0):
                dipdir = 180 + (180/np.pi)*np.arctan(unitnorm[0] / unitnorm[1])
            elif(unitnorm [0] < 0 and unitnorm[1] > 0):
                dipdir = 360 + (180/np.pi)*np.arctan(unitnorm[0] / unitnorm[1])

# print results
            fh.write("P1, " + xcoord1.rstrip("\n") + ", " + ycoord1.rstrip("\n") + ", " + zcoord1)
            fh.write("P2, " + xcoord2.rstrip("\n") + ", " + ycoord2.rstrip("\n") + ", " + zcoord2)
            fh.write("P3, " + xcoord3.rstrip("\n") + ", " + ycoord3.rstrip("\n") + ", " + zcoord3)
            fh.write(format(dip, '.2f') + ", " + format(dipdir, '.2f') + ", " + format(area, '.2f') + "\n")

fh.close()
