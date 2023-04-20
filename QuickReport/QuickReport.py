# This tool only works in ArcGIS Pro version 3.1 or above.
# Many of the methods accessed via the ArcGISProject class
# are not available in earlier versions of ArcGIS Pro. 

# Libraries
import arcpy, os

def createQuickReport():
    arcGISProVersion = arcpy.GetInstallInfo()["Version"]
    if arcGISProVersion.startswith("3.1"): # Needs to not use .startswith(). What happens when ArcGIS Pro rolls over to 4.x?
    # do something
        pass
    else:
        print(f"This tool only works in ArcGIS Pro 3.1 or above. Current version: {arcGISProVersion}. Please update ArcGIS Pro to use this tool.")
        return

if __name__ == '__main__':
    createQuickReport()