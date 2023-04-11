
# Repair Layer File Sources

Automatically repairs the sources of certain .LYRX files found within the RECOVER data packages downloaded from the [NASA RECOVER post-wildfire decision support system dashboard](https://www.arcgis.com/apps/dashboards/19af90a8bc5d41188ed855d249bc1c72). 

## Overview 

Layer files (.LYRX file extensions in ArcGIS Pro, .LYR file extensions in ArcMap) do not store relative paths for their sources. When a user adds .LYRX files received via download or another source to their project, the layer in the Contents pane will typically be accompanied by a red exclamation mark ( :exclamation: ). In addition, the layer will not draw if the user has added it to a map. This is because the source is "broken." [Repairing .LYRX sources manually](https://pro.arcgis.com/en/pro-app/latest/help/mapping/layer-properties/repair-broken-data-links.htm) can be time consuming, especially if you have to repair many similar sources. 

This script is designed to assist end users of the NASA RECOVER DSS dashboard in their analysis of areas after wildfires by automatically repairing the sources of the .LYRX files found in the data packages they download. End users can dive right in to analysis without needing to painstakingly repair the data sources for each non-webservice-based .LYRX file.

## Instructions

This script can be found in the RECOVERDataPackageTools.atbx, which should come with every data package downloaded from the NASA RECOVER post-wildfire decision support system dashboard. Instructions for use are as follows:

1. Connect the extracted data package folder to a project in ArcGIS Pro.
2. Locate and expand the RECOVERDataPackageTools.atbx.
3. Double-click on the Repair Layer File Sources script tool to open it in a Geoprocessing pane.
4. In the Fire Folder box, specify the data package for which you would like to repair sources (for example, the folder should look like "Fire_2022_ORWWF_000400" for the Double Creek fire).
5. Click "Run" in the bottom right-hand corner of the Geoprocessing pane. 

The script will set the source for the "broken" .LYRX files to the proper .TIF file. The .LYRX files can now be added to your project without needing to deal with those pesky red exclamation points by manually setting the source.

## Known Issues/TO DO
- [x] Figure out why the Existing Vegetation Cover (EVC) .LYRX is not cooperating.
    - Sometimes, the data source gets set to the wrong .TIF (EVC layer getting set to the EVT .TIF).
- [x] Turn this script into a tool that can be run within an ArcGIS Pro project at the click of a button. 
- [ ] Add comments to complicated parts.
- [ ] Consider alternatives to setting source by index of the string that makes up the file's name.
    - Like perhaps make sure the string of the layer name matches part of the string of the raster name.
