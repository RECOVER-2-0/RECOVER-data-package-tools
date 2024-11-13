geemapNDVItool in Longterm_monitor_NDVI toolbox

The tool is to take in user defined the ROI and time period, and download the LandSat 9 Level 2 Collection 2 Tier 1 scene, or  LandSat 8 Level 2 Collection 2 Tier 1 scene , or Sentinel-2 MSI Multispectral Instrument Level 2A then calculate the NDVI. 
 
Overview

The tool is to take in user defined the ROI and time period, and download the LandSat 9 Level 2 Collection 2 Tier 1 scene (https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC09_C02_T1_L2), or  LandSat 8 Level 2 Collection 2 Tier 1 scene (https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2), or Sentinel-2 MSI Multispectral Instrument Level 2A  then calculate the NDVI. The two bands for NDVI calculation  for LandSat data is 'SR_B4'(red) and 'SR_B5' (near infrared), for Sentinel data is 'B4' (red) and 'B8' (Near infrared) . The NDVI image will be downloaded to the user designated folder. One image will be download for each Satellite image each time. To get multiple images between the time period, user can change the start date and end date. This tool needs a cloned ArcGIS pro default Python environment with installation of geemap.‌

Instructions

This script can be found in the longterm_monitor_NDVI.atbx which can be download from https://github.com/RECOVER-2-0/RECOVER-data-package-tools/blob/main/Longterm_Monitor_NDVI/longterm_monitor_NDVI.atbx.
The toolbox can be opened in ArcGIS Pro 3.1 after. Parameters explaination are as the following:

eeauth: The GEE authentication method. Choose from username or projectID.

eeparam: According to the selection of eeauth. If username is selected, it needs the username that associated with Google Earth Engine Cloud project. If the gmail is abc@gmail.com, please type in abc. Then the GEE project name will be ee-username. This is the default the gee project naming convention.
If the projectID is selected. It needs your GEE project name. To find the the project name, please go to https://console.developers.google.com/ and login with your user email, You will be prompted with registered GEE cloud projects. If your project page is empty with the above link, it means that you don't have the account registered with cloud project, please follow the steps in here https://developers.google.com/earth-engine/cloud/earthengine_cloud_project_setup

fpolygon: Fire perimeter polygon can be in feature class or shape file format. Envelope was created with Feature Envelope to Polygon (https://pro.arcgis.com/en/pro-app/latest/tool-reference/data-management/feature-envelope-to-polygon.htm), and a 5000 meter buffer was created based on Envelope to enlarge the search spatial extent. Fextent, and Fbuffer two feature classes will be saved to the ArcGIS Pro default geodatabase. These are the intermediate features. End users can delete these data after the running of the tool.

startdate: Image collection start date in form of yyyy-mm-dd.

enddate: Image collection end date in form of yyyy-mm-dd

folderdir: The folder that the NDVI image will be downloaded to.

Satellite: End user can choose from LandSat 9 Level 2 Collection 2 Tier 1 scene, LandSat 8 Level 2 Collection 2 Tier 1 scene, and Sentinel-2 MSI Multispectral Instrument Level 2A. Or any combination of the image collections. The NDVI image resolution will be 30m for LandSat image, and 10m for Sentinel image.


Known Issues/TO DO

User needs to have an gmail account and register a GEE cloud project.
If new user account applied, user need to go to C:\Users\[YOUR USERNAME]\.config\earthengine\ and delete the credentials file to avoid conflict.
It would require a cloned ArcGIS python environment and installation geemap packages.
ArcGIS pro deep learning package has a conflict with geemap packages. It would recommend seperate clone python environment to host geemap and deep learning packages seperately.



