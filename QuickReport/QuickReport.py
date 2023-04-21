# This tool only works in ArcGIS Pro version 3.1 or above.
# Many of the methods accessed via the ArcGISProject class
# are not available in earlier versions of ArcGIS Pro. 

# Libraries
import arcpy, os

def createQuickReport():
    arcGISProVersion = arcpy.GetInstallInfo()["Version"]
    if arcGISProVersion.startswith("3.1"): # Needs to not use .startswith(). What happens when ArcGIS Pro rolls over to 4.x?
        print(f"Current version: {arcGISProVersion}")
        
        # Access current project
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        
        # Create new map
        qrMap = aprx.createMap("QuickReportMap", "Map")
        
        # Access paths of fire perimeter feature class and layout to import
        fp = fr"C:\Users\coler\Documents\ISU\WFH\Fire_2022_ORWWF_000400\Fire.gdb\Fire_Perimeter" # Parameterize
        lyt = fr"C:\Users\coler\Documents\ISU\WFH\Fire_2022_ORWWF_000400\QuickReportLayout.pagx" # Non-parameter
        
        # Add fire perimeter to new map, set extent
        qrMap.addDataFromPath(fp)
        fpLyr = qrMap.listLayers()[-1] # Retrieves the very last layer added to the newly created map
        qrMap.defaultCamera.setExtent(arcpy.Describe(fpLyr).extent) # Set extent to that of the last layer added
        
        # Import layout
        aprx.importDocument(lyt)
        qrLyt = aprx.listLayouts("QuickReportLayout")[-1] # Retrieves last layout added to project
        
        # Get layout elements
        mapFrame = qrLyt.listElements("MapFrame_Element")[0] # Should only be one map frame element
        mapFrame.map = qrMap
        
        print("done")
        
    else:
        print(f"This tool only works in ArcGIS Pro 3.1 or above. Current version: {arcGISProVersion}. Please update ArcGIS Pro to use this tool.")
        

if __name__ == '__main__':
    createQuickReport()