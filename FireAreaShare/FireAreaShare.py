# Libraries
import arcpy

def GetFireAreaShare(workspace, in_features, clip_features):
    # Define workspace
    arcpy.env.workspace = workspace

    # Choose features to clip, set Fire_Perimeter as clip features
    # clip_features = "Fire_Perimeter" 
    out_feature_class = in_features + "_Share" # Add _Share to end of in_features string

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

    # Add new field for Fire Area Share
    arcpy.management.AddField(fc, "fa_Share", "DOUBLE", field_alias="Fire Area Share")

    # Cursor to calculate values for new fields
    arcpy.AddMessage("Calculating share for each feature in the feature class.")
    with arcpy.da.UpdateCursor(fc, ['Shape_Area', 'fa_Share']) as cursor:
        for row in cursor: 
            row[1] = (row[0])/totalArea
            cursor.updateRow(row)
    del cursor
    arcpy.AddMessage("Fire area share calculated successfully.")
    return

if __name__ == '__main__':

    workspace = arcpy.GetParameterAsText(0)
    in_features = arcpy.GetParameterAsText(1)
    clip_features = arcpy.GetParameterAsText(2)

    GetFireAreaShare(workspace, in_features, clip_features)