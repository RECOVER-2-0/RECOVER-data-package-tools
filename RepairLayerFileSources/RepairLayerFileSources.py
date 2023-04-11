# Libraries
import os, arcpy

# Function
def repairSources(fire_folder):

    # Loop
    for filename in os.listdir(fire_folder):
        if filename.endswith(".lyrx",3,8):    
            lyrPath = os.path.join(fire_folder, filename) # Consider change to just os.path.abspath(filename)
            print(lyrPath)
            lyrFile = arcpy.mp.LayerFile(lyrPath)
            for lyr in lyrFile.listLayers():
                if lyr.supports("datasource"):
                    if lyr.isBroken:
                        cp = lyr.connectionProperties
                        cp['connection_info']['database'] = fire_folder
                        for tif in os.listdir(fire_folder):
                            if tif.startswith(filename[:3]) and tif.endswith(".tif"): # Consider change to matching strings
                                tifName = tif
                        cp['dataset'] = tifName
                        print("updating connection")
                        lyr.updateConnectionProperties(lyr.connectionProperties, cp)
            lyrFile.save()
            print("moving on")
            
    print("done")

if __name__ == '__main__':
    
    fire_folder = arcpy.GetParameterAsText(0)
    
    repairSources(fire_folder)