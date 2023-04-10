# Libraries
import os, arcpy

# Need path to Fire.gdb 
# Consider changing to parameter so user can specify which geodatabase to use if they are looking at multiple fires in the same project
directory = os.getcwd()
for filename in os.listdir(directory):
    if filename == "Fire.gdb":
        workspace = os.path.abspath(filename)

# Define workspace
arcpy.env.workspace = workspace

# Choose features to clip, set Fire_Perimeter as clip features
in_features = "SMA" # Surface Management Agencies (change to user defined parameter later)
clip_features = "Fire_Perimeter" 
out_feature_class = in_features + "_Share" # Add _Share to end of in_features string

# Run Pairwise Clip
arcpy.analysis.PairwiseClip(in_features, clip_features, out_feature_class)

# Re-name variable for output of Pairwise Clip
fc = out_feature_class 

# Get total area of the new feature class to be used later in field calculation
# This could alternatively be found by getting the Shape_Area of the Fire_Perimeter feature class
totalArea = 0
with arcpy.da.SearchCursor(fc, ['Shape_Area']) as cursor: # Maybe just pass out_feature_class instead of fc here
    for row in cursor:
        totalArea += row[0]
del cursor

# Add new field for Fire Area Share
arcpy.management.AddField(fc, "fa_Share", "DOUBLE", field_alias="Fire Area Share")

# Cursor to calculate values for new fields
with arcpy.da.UpdateCursor(fc, ['Shape_Area', 'fa_Share']) as cursor:
    for row in cursor: 
        row[1] = (row[0])/totalArea
        cursor.updateRow(row)
del cursor

# Done!