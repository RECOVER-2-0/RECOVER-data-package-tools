# The script tool name has been changed from "Fire Area Share" to "Percent Distribution within Fire Perimeter."

# Libraries
import arcpy

def GetFireAreaShare(workspace, in_features, clip_features):
    # Define workspace
    arcpy.env.workspace = workspace

    # Choose features to clip, set Fire_Perimeter as clip features
    # clip_features = "Fire_Perimeter" 
    out_feature_class = in_features + "_Distribution" # Add _Distribution to end of in_features string

    # Run Pairwise Clip
    arcpy.analysis.PairwiseClip(in_features, clip_features, out_feature_class)
    arcpy.AddMessage("Features clipped to Fire Perimeter.")

    # Re-name variable for output of Pairwise Clip
    fc = out_feature_class 

    # Get total area of the new feature class to be used later in field calculation
    # This could alternatively be found by getting the Shape_Area of the Fire_Perimeter feature class
    totalArea = 0
    arcpy.AddMessage("Calculating total area...")
    with arcpy.da.SearchCursor(fc, ['Shape_Area']) as cursor: # Maybe just pass out_feature_class instead of fc here
        for row in cursor:
            totalArea += row[0]
    del cursor

    # Add new field for Fire Area Distribution
    arcpy.management.AddField(fc, "fa_Distribution", "DOUBLE", field_alias="Distribution within Fire Area")

    # Cursor to calculate values for new fields
    arcpy.AddMessage("Calculating distribution for each feature in the feature class.")
    with arcpy.da.UpdateCursor(fc, ['Shape_Area', 'fa_Distribution']) as cursor:
        for row in cursor: 
            row[1] = ((row[0])/totalArea)*100
            cursor.updateRow(row)
    del cursor
    arcpy.AddMessage("Fire area distribution calculated successfully.")

    # Add to current map
    aprx = arcpy.mp.ArcGISProject("CURRENT")
    aprxMap = aprx.listMaps()[0]
    aprxMap.addDataFromPath(fc)
    
    return

if __name__ == '__main__':

    workspace = arcpy.GetParameterAsText(0)
    in_features = arcpy.GetParameterAsText(1)
    clip_features = arcpy.GetParameterAsText(2)

    GetFireAreaShare(workspace, in_features, clip_features)