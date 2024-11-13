import ee
import arcpy
import geemap
import os
from datetime import datetime as dt
from datetime import date
import sys


def ProjectCoordinates(x,y,inputcrs,outputcrs):
    point = arcpy.PointGeometry(arcpy.Point(x,y),inputcrs)
    projectedpoint = point.projectAs(outputcrs)
    projectedcoordinates = [projectedpoint.firstPoint.X,projectedpoint.firstPoint.Y]
    return projectedcoordinates

def SatNDVI(myimage, bandr, bandn):
    #Compute the Normalized Difference Vegetation Index (NDVI).
    Red = myimage.select(bandr)
    NIR = myimage.select(bandn)
    ndvi = NIR.subtract(Red).divide(NIR.add(Red))
    return ndvi
        
def geemap_tool():
    #authenticate and initialize ee
    if eeauth == 'username':
        project = 'ee-'+eeparam
        arcpy.AddMessage('the earth engine project is {0}'.format(project))
        ee.Authenticate()
        ee.Initialize(project=project)
        arcpy.AddMessage("the cloud project has been successfully authenticated") 
    elif eeauth == 'projectID':
        arcpy.AddMessage('the earth engine project is {0}'.format(eeparam))
        ee.Authenticate()
        ee.Initialize(project=eeparam)
        arcpy.AddMessage("the cloud project has been successfully authenticated")
    else: 
        arcpy.AddMessage("please provide the GEE username or GEE project name for authentification")
    
    #reproject the current map extent to wgs coordinates
    fextent= arcpy.FeatureEnvelopeToPolygon_management(fpolygon, "Fextent","SINGLEPART")
    fbuffer = arcpy.analysis.Buffer(fextent,"Fbuffer","5000 Meters")
    srin = arcpy.SpatialReference(int(arcpy.Describe(fbuffer).spatialReference.factoryCode)) # Projected  
    srout = arcpy.SpatialReference(4326) # Geographic  
    xin = arcpy.Describe(fbuffer).extent.XMin
    yin = arcpy.Describe(fbuffer).extent.YMin
    xmin,ymin = ProjectCoordinates(xin,yin,srin,srout)
    xin = arcpy.Describe(fbuffer).extent.XMax
    yin = arcpy.Describe(fbuffer).extent.YMax
    xmax,ymax = ProjectCoordinates(xin,yin,srin,srout)
    arcpy.AddMessage("the current map extent is ")
    arcpy.AddMessage(xmin)
    arcpy.AddMessage(ymin)
    arcpy.AddMessage(xmax)
    arcpy.AddMessage(ymax)

    #now = date.today()
    #enddate = now.strftime('%Y-%m-%d')    
    arcpy.AddMessage("the image will be retrieved between {0} and {1}".format(startdate, enddate))
   
    if dt.strptime(startdate,'%Y-%m-%d') > dt.strptime(enddate, '%Y-%m-%d'):
        arcpy.AddMessage("WARNING!!!The startdate is after the current date!") 
    elif startdate == enddate:
        arcpy.AddMessage("WARNING!!!No image in the study area was found during the specific time period. Please include a longer search perioed!")
    else:
        #form the box boundary witht current map extent
        box = ee.Geometry.BBox(xmin,ymin,xmax,ymax)
        #retrieve the image collection from google earth engine

        arcpy.AddMessage("Image will be retrived from:")
        arcpy.AddMessage(Satellite)
        
        if 'LANDSAT/LC09/C02/T1_L2' in Satellite:
            image = ee.ImageCollection("LANDSAT/LC09/C02/T1_L2")\
                    .filterBounds(box)\
                    .filterDate(str(startdate), str(enddate))\
                    .sort('CLOUD_COVER')\
                    .sort('date')\
                    .first()
           
            imagecol = image.getInfo()
            arcpy.AddMessage("retrieving LANDSAT/LC09/C02/T1_L2 image")
            if imagecol is None:
                arcpy.AddMessage("WARNING!!!No image in the study area was found during the specific time period. Please include a longer search perioed!")
            else:
                imageid = image.get("system:id").getInfo() # get the id name of the image
                imageid = imageid[len(imageid)-8:]
                arcpy.AddMessage("The retrived image date is: {0}".format(imageid))
                cloudscore = ee.Image(image).get('CLOUD_COVER').getInfo()
                arcpy.AddMessage("The cloud cover score is {0}".format(cloudscore))
                
                ndvi = SatNDVI(image,'SR_B4','SR_B5')
                ndvi = ndvi.multiply(10000)
                ndvi = ndvi.int16()
                filename = 'LANDSAT_LC09_C02_T1_02'+'_NDVI'+'_'+imageid+'.tif' 
            
                filename = os.path.join(folderdir, filename) 

                geemap.ee_export_image(
                    ndvi, filename=filename, scale=30, region=box, file_per_band=False
                )
                if arcpy.Exists(filename):
                    arcpy.AddMessage("{0} has been downloaded".format(filename))
                else:
                    arcpy.AddMessage("WARNING!!!Request image size is greater than 32MB. Please select a smaller area.")
                    
            
        if 'LANDSAT/LC08/C02/T1_L2' in Satellite:
            image = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")\
                    .filterBounds(box)\
                    .filterDate(str(startdate), str(enddate))\
                    .sort('CLOUD_COVER')\
                    .sort('date')\
                    .first()
           
            imagecol = image.getInfo()
            arcpy.AddMessage("retrieving LANDSAT/LC08/C02/T1_L2 image")
            if imagecol is None:
                arcpy.AddMessage("WARNING!!!No image in the study area was found during the specific time period. Please include a longer search perioed!")
            else:
                imageid = image.get("system:id").getInfo() # get the id name of the image
                imageid = imageid[len(imageid)-8:]
                arcpy.AddMessage("The retrived image date is: {0}".format(imageid))
                cloudscore = ee.Image(image).get('CLOUD_COVER').getInfo()
                arcpy.AddMessage("The cloud cover score is {0}".format(cloudscore))
                
                ndvi = SatNDVI(image,'SR_B4','SR_B5')
                ndvi = ndvi.multiply(10000)
                ndvi = ndvi.int16()
                filename = 'LANDSAT_LC08_C02_T1_02'+'_NDVI'+'_'+imageid+'.tif' 
            
                filename = os.path.join(folderdir, filename) 
                geemap.ee_export_image(
                    ndvi, filename=filename, scale=30, region=box, file_per_band=False
                ) 
                if arcpy.Exists(filename):
                    arcpy.AddMessage("{0} has been downloaded".format(filename))
                else:
                    arcpy.AddMessage("WARNING!!!Request image size is greater than 32MB. Please select a smaller area.")
            
        
        if 'COPERNICUS/S2' in Satellite:
            image = ee.ImageCollection("COPERNICUS/S2")\
                    .filterBounds(box)\
                    .filterDate(str(startdate), str(enddate))\
                    .sort('CLOUD_COVER')\
                    .sort('date')\
                    .first()
           
            imagecol = image.getInfo()
            arcpy.AddMessage("retrieving COPERNICUS/S2 image")
            if imagecol is None:
                arcpy.AddMessage("WARNING!!!No image in the study area was found during the specific time period. Please include a longer search perioed!")
            else:
                imageid = image.get("system:id").getInfo() # get the id name of the image
                imageid = imageid[14:22]
                arcpy.AddMessage("The retrived image date is: {0}".format(imageid))
                cloudscore = ee.Image(image).get('CLOUD_COVER').getInfo()
                arcpy.AddMessage("The cloud cover score is {0}".format(cloudscore))
                
                ndvi = SatNDVI(image,'B4','B8')
                ndvi = ndvi.multiply(10000)
                ndvi = ndvi.int16()
                filename = 'COPERNICUS_S2'+'_NDVI'+'_'+imageid+'.tif' 
            
                filename = os.path.join(folderdir, filename) 
                geemap.ee_export_image(
                    ndvi, filename=filename, scale=10, region=box, file_per_band=False
                ) 
                if arcpy.Exists(filename):
                    arcpy.AddMessage("{0} has been downloaded".format(filename))
                else:
                    arcpy.AddMessage("WARNING!!!Request image size is greater than 32MB. Please select a smaller area.")

    return

if __name__ == "__main__":

    eeauth = arcpy.GetParameterAsText(0)
    eeparam = arcpy.GetParameterAsText(1)
    fpolygon = arcpy.GetParameterAsText(2)
    startdate = arcpy.GetParameterAsText(3)
    enddate = arcpy.GetParameterAsText(4)
    folderdir = arcpy.GetParameterAsText(5)
    Satellite = arcpy.GetParameterAsText(6)

    geemap_tool()

