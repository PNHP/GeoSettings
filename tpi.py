#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:      http://www.jennessent.com/downloads/tpi-poster-tnc_18x22.pdf
#
# Author:      ctracey
#
# Created:     13/07/2018
# Copyright:   (c) ctracey 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------

#import packages
import os, arcpy, datetime
from arcpy import env
from arcpy.sa import *

# set directories and env variables
arcpy.env.overwriteOutput = True
arcpy.env.qualifiedFieldNames = False

# set input paramenters for Tool
dem = arcpy.GetParameterAsText(0)
outGDB = arcpy.GetParameterAsText(1)

# smooth the DEM to eliminate noise
dem = FocalStatistics(dem, NbrCircle(3,"CELL"),"MEAN", "DATA")

# calculate slope
slope = arcpy.Slope_3d(dem, "tpisrc_slope", "DEGREE")
slope = Int(slope)
slope = Reclassify(slope,"Value",RemapRange([[0,5,5],[6,90,6]]))
slope.save("tpi_slope")

# calculate the topographic position index at a fine scale
tpisrc_fm300 = FocalStatistics(dem, NbrAnnulus(15,30,"CELL"),"MEAN", "DATA")
tpisrc_rc300 = Int((dem - tpisrc_fm300)+0.5)
tpisrc_rc300mean = float(arcpy.GetRasterProperties_management(tpisrc_rc300, "MEAN").getOutput(0))
arcpy.AddMessage("The mean of tpi300 is {0}.".format(tpisrc_rc300mean))
tpisrc_rc300std = float(arcpy.GetRasterProperties_management(tpisrc_rc300, "STD").getOutput(0))
tpisrc_rc300_stdi = Int((((tpisrc_rc300 - tpisrc_rc300mean) / tpisrc_rc300std) * 100) + .5)
tpisrc_rc300_stdi.save("tpi_300")
arcpy.CalculateStatistics_management("tpi_300")

# calculate the topographic position index at a broad scale
tpisrc_fm2000 = FocalStatistics(dem, NbrAnnulus(62,67,"CELL"),"MEAN", "DATA")
tpisrc_rc2000 = Int((dem - tpisrc_fm2000)+0.5)
tpisrc_rc2000mean = float(arcpy.GetRasterProperties_management(tpisrc_rc2000, "MEAN").getOutput(0))
arcpy.AddMessage("The mean of tpi2000 is {0}.".format(tpisrc_rc2000mean))
tpisrc_rc2000std = float(arcpy.GetRasterProperties_management(tpisrc_rc2000, "STD").getOutput(0))
tpisrc_rc2000_stdi = Int((((tpisrc_rc2000 - tpisrc_rc2000mean) / tpisrc_rc2000std) * 100) + .5)
tpisrc_rc2000_stdi.save("tpi_2000")
arcpy.CalculateStatistics_management("tpi_2000")

# combine rasters
outCombine = Combine(["tpi_slope","tpi_300","tpi_2000"])
outCombine.save("outcombine2")

# assign topographic position
arcpy.AddField_management("outcombine2", "tpi", "LONG")
arcpy.AddField_management("outcombine2", "class", "TEXT","", "", 100)

with arcpy.da.UpdateCursor("outcombine2",["tpi_slope", "tpi_300", "tpi_2000", "tpi", "class"]) as cursor:
    for row in cursor:
        if (row[1] > -100 and row[1] < 100 and row[2] > -100 and row[2] < 100 and row[0] <= 5):
            row[3] = 5
            row[4] = "broad flat areas"
        elif (row[1] > -100 and row[1] < 100 and row[2] > -100 and row[2] < 100 and row[0] >= 6):
            row[3] = 6
            row[4] = "broad open slopes"
        elif (row[1] > -100 and row[1] < 100 and row[2] >= 100):
            row[3] = 7
            row[4] = "flat ridge tops"
        elif (row[1] > -100 and row[1] < 100 and row[2] <= -100):
            row[3] = 4
            row[4] = "U-shaped valleys"
        elif (row[1] > -100 and row[2] > -100 and row[2] < 100):
            row[3] = 2
            row[4] = "lateral midslope, incised drainages"
        elif (row[1] > 100 and row[2] > -100 and row[2] < 100):
            row[3] = 9
            row[4] = "lateral midslope drainage divides"
        elif (row[1] <= -100 and row[2] >= 100):
            row[3] = 3
            row[4] = "stream headwaters"
        elif (row[1] <= -100 and row[2] <= -100):
            row[3] = 1
            row[4] = "deep, narrow canyons"
        elif (row[1] <= -100 and row[2] <= 0):
            row[3] = 11
            row[4] = " upper part of deep, narrow canyons"
        elif (row[1] >= 100 and row[2] >= 100):
            row[3] = 10
            row[4] = "flat ridge tops???"
        elif (row[1] >= 100 and row[2] <= -100):
            row[3] = 8
            row[4] = "local ridge/hilltops"
         # Update the cursor with the updated list
        cursor.updateRow(row)

tpi_final = Lookup("outcombine2","tpi")
tpi_final.save("tpi_final")
