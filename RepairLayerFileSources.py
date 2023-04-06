# Libraries
import os, arcpy

# Get current directory
directory = os.getcwd()

# Loop
for filename in os.listdir(directory):
    if filename.endswith(".lyrx",3,8):    
        lyrPath = os.path.join(directory, filename)
        print(lyrPath)
        lyrFile = arcpy.mp.LayerFile(lyrPath)
        for lyr in lyrFile.listLayers():
            if lyr.supports("datasource"):
                if lyr.isBroken:
                    cp = lyr.connectionProperties
                    cp['connection_info']['database'] = directory
                    for tif in os.listdir(directory):
                        if tif.startswith(filename[:2]) and tif.endswith(".tif"):
                            tifName = tif
                    cp['dataset'] = tifName # string containing .tif name here, how do we get it here?
                    print("updating connection")
                    lyr.updateConnectionProperties(lyr.connectionProperties, cp)
        lyrFile.save()
        print("moving on")
        
print("done")