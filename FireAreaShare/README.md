
# Fire Area Share

Calculates the share of a fire area for each part of any multi-part polygons inside the Fire.gdb that comes with each RECOVER data package downloaded from the [NASA RECOVER post-wildfire decision support system dashboard](https://www.arcgis.com/apps/dashboards/19af90a8bc5d41188ed855d249bc1c72).

## Overview

The breakdown of a fire area is a common workflow for end users of the NASA RECOVER DSS dashboard. For example, if a user wanted to figure out how much of the area affected by the wildfire belonged to the Bureau of Land Management, they might undergo the tedious process of clipping, adding fields, joining to the relevant layer, and calculating the new fields for the new feature class. The aim of this tool is to create that feature class very quickly using one script where parameters are specified once. It produces a new feature class, which is clipped to the Fire_Perimeter, and contains a new field, Fire Area Shared (fa_Share), which contains a decimal value of the breakdown of the fire area. 

The script is compatible with the following feature classes inside the Fire.gdb that comes with each RECOVER data package (more descriptive feature class names in parentheses if applicable):
 - SMA (Surface Management Agency)
 - Soils_gSSURGO
 - Soils_STATSGO
 - Geology
 - Habitat
 - WBD (Watershed Boundary Dataset)
 - LandslidePotential
 - Wetlands
 - Wilderness_Status

## Instructions

In the future, this script will be added as a tool which will come packaged with the RECOVER data packages downloaded from the dashboard. You'll be able to open up the data package folder in an ArcGIS Pro project, expand the RECOVERDataPackageTools.atbx, and click on the tool to generate new features with shares of the fire area already calculated.

For now, follow these steps to use this script as-is in your project:

1. Download a data package from the dashboard and extract it somewhere on your hard drive.
2. Open a new project in ArcGIS Pro.
3. Create a new map using the unzipped data package as its location.
4. Within your project, create a new notebook and copy in this script.
5. Click Run.

## Known Issues/TO DO
- [ ] Turn this script into a tool that can be run within an ArcGIS Pro project at the click of a button. 
- [ ] Add user-defined parameters for running in ArcGIS Pro.
