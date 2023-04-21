# This tool only works in ArcGIS Pro version 3.1 or above.
# Many of the methods accessed via the ArcGISProject class
# are not available in earlier versions of ArcGIS Pro. 

# Libraries
import arcpy, os

def createQuickReport():
    arcGISProVersion = arcpy.GetInstallInfo()["Version"]
    if arcGISProVersion.startswith("3.1"): # Needs to not use .startswith(). What happens when ArcGIS Pro rolls over to 4.x?
        print(f"Current version: {arcGISProVersion}")
        
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        qrMap = aprx.createMap("QuickReportMap", "Map")
        fp = fr"C:\Users\coler\Documents\ISU\WFH\Fire_2022_ORWWF_000400\Fire.gdb\Fire_Perimeter" # Parameterize
        
        qrMap.addDataFromPath(fp)
        
        fpLyr = qrMap.listLayers()[-1] # Retrieves the very last layer added to the newly created map
        qrMap.defaultCamera.setExtent(arcpy.Describe(fpLyr).extent) # Set extent to that of the last layer added
        
        
        print("done")
    else:
        print(f"This tool only works in ArcGIS Pro 3.1 or above. Current version: {arcGISProVersion}. Please update ArcGIS Pro to use this tool.")
        return

if __name__ == '__main__':
    createQuickReport()