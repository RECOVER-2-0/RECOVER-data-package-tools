# Libraries
import os, arcpy

# Function
def repairSources():

    # Get current directory
    directory = os.getcwd()

    # Loop
    for filename in os.listdir(directory):
        if filename.endswith(".lyrx",3,8):    
            lyrPath = os.path.join(directory, filename) # Consider change to just os.path.abspath(filename)
            print(lyrPath)
            lyrFile = arcpy.mp.LayerFile(lyrPath)
            for lyr in lyrFile.listLayers():
                if lyr.supports("datasource"):
                    if lyr.isBroken:
                        cp = lyr.connectionProperties
                        cp['connection_info']['database'] = directory
                        for tif in os.listdir(directory):
                            if tif.startswith(filename[:3]) and tif.endswith(".tif"): # Consider change to matching strings
                                tifName = tif
                        cp['dataset'] = tifName
                        print("updating connection")
                        lyr.updateConnectionProperties(lyr.connectionProperties, cp)
            lyrFile.save()
            print("moving on")
            
    print("done")

if __name__ == '__main__':
    repairSources()