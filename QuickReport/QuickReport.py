import arcpy, os
from matplotlib import pyplot as plt
import seaborn
from arcpy.sa import *
import pandas as pd
from bs4 import BeautifulSoup
import shutil
import traceback

# Add commas to string of numbers
def add_commas(number_input):

    number_as_string = str(number_input)

    if len(number_as_string) <= 3:
        # No commas needed for numbers with three digits or less
        pass
    else:
        number_list = list(number_as_string)
        
        # Use reversed() to go through the list backwards
        number_with_commas_list = list(''.join(y + ',' * (x % 3 == 2) for x, y in enumerate(reversed(number_list))))

        # numbers with digits that are multiples of 3 will always get a comma added to the end of their list form, so just remove it
        if number_with_commas_list[len(number_with_commas_list) - 1] == ',':
            number_with_commas_list.pop()

        # reverse the list (now with commas) and turn it back into a string
        number_with_commas_as_string = ''
        for x in reversed(number_with_commas_list):
            number_with_commas_as_string += x

        return number_with_commas_as_string

# Population Summary Figures
def popSummary(census_blocks):
    # do something
    total_population = 0
    total_area = 0
    null_area = 0
    with arcpy.da.SearchCursor(census_blocks, ['pop_c', 'Shape_Area']) as cursor:
        for row in cursor:
            total_area += row[1]
            if row[0] is not None:
                total_population += row[0]
            else:
                null_area += row[1]

    total_area_acres = add_commas(round((total_area/4046.8564224)))
    population_data_availability = round(100 - ((null_area/total_area) * 100))

    return add_commas(total_population), total_area_acres, population_data_availability

# Surface Management Summary Pie Chart
def acreagePieChart(inputFeatures, clipFeatures, statField, chartTitle, outpath):
    tempOutput = inputFeatures + "_Distribution"
    tempOutput2 = inputFeatures + "_Dissolve"
    arcpy.PairwiseClip_analysis(inputFeatures, clipFeatures, tempOutput)
    
    arcpy.Dissolve_management(tempOutput, tempOutput2, [statField])
    
    arcpy.CalculateGeometryAttributes_management(tempOutput2, [["Acres", "AREA"]], area_unit="ACRES")
    
    # Get lists of your field of interest and acre values
    statFieldValList = []
    acreList = []
    
    totalAcreage = 0
    
    with arcpy.da.SearchCursor(tempOutput2, ['Acres', statField]) as cursor:
        for row in cursor:
            statFieldValList.append(row[1])
            acreList.append(row[0])
            totalAcreage += row[0]
    del cursor
    
    arcpy.Delete_management(tempOutput)
    arcpy.Delete_management(tempOutput2)# delete temporary layers
    
    #return statFieldValList, acreList, totalAcreage

    paletteColor = seaborn.color_palette('colorblind')

    csfont = {'fontname': 'Times New Roman'}
    
    plt.suptitle(chartTitle, fontsize = 14, **csfont)
    plt.title("Total acreage: " + add_commas(str(round(totalAcreage))), **csfont)

    plt.pie(x = acreList, labels = statFieldValList, colors = paletteColor, 
        autopct = '%.1f%%')

    plt.savefig(os.path.join(outpath, statField + "_PieChart.png"))
    plt.clf()
    
# Land Cover Summary Table
def landCoverSummary(zoneData, valueRaster):
    
    fire_latest_ObjectID = int(arcpy.GetCount_management(zoneData)[0])
    
    arcpy.CheckOutExtension("Spatial")
    
    zoneField = "poly_IncidentName" # should always be the same
    outTable = os.path.join(os.path.split(zoneData)[0], "zStat_EVT")
    with arcpy.EnvManager(overwriteOutput = True):

        arcpy.MakeFeatureLayer_management(zoneData, "latest_shape", f"OBJECTID = {fire_latest_ObjectID}")

        ZonalStatisticsAsTable("latest_shape", zoneField, valueRaster, outTable,
                            "DATA", "MAJORITY")
    
    arcpy.CheckInExtension("Spatial")
    
    flds = ["LFRDB", "EVT_NAME", "EVT_ORDER", "EVT_CLASS", "EVT_SBCLS"]
    fldsCln = ["Code", "Name", "Order", "Class", "Subclass", "Acres", "Percent Cover"]
    
    arcpy.JoinField_management(outTable, "MAJORITY", valueRaster, "Value", flds)
    
    arcpy.CalculateField_management(outTable, "Acres", "!AREA!/4046.8564224", "PYTHON3",
                                   "", "LONG")
    
    flds.append("Acres")
    
    vals = []
    
    with arcpy.da.SearchCursor(outTable, flds) as cursor:
        for row in cursor:
            vals.append(row)
    
    ## next, calculate pct cover by calculating *vals* Acres/ *fireFc* Shape_Area/4046.8564224
    flds.append("Pct_Cover")
    
    valsList = list(vals[0]) 
    
    fireFcShapeArea = [row[0] for row in arcpy.da.SearchCursor(zoneData, ["Shape_Area"])][0]
    lcAcres = valsList[5]

    pctCov = (round(lcAcres/(fireFcShapeArea/4046.8564224), 2) * 100)

    valsList.append(pctCov)

    landCoverTxt = f"{valsList[1]} class {valsList[0]}"
    
    df = pd.DataFrame({'MAJORITY EVT COVER': fldsCln, '': valsList})
    
    return str(df.to_html(index=False)), landCoverTxt

# Topography Summary Tables    
def topoStatTable(zoneData, topoRaster, tblTitle):
    
    fire_latest_ObjectID = int(arcpy.GetCount_management(zoneData)[0])

    arcpy.CheckOutExtension("Spatial")
    
    zoneField = "poly_IncidentName" # Should always be the same
    outTable = os.path.join(os.path.split(zoneData)[0], "zStat_topo")
    with arcpy.EnvManager(overwriteOutput = True):
        
        arcpy.MakeFeatureLayer_management(zoneData, "latest_shape", f"OBJECTID = {fire_latest_ObjectID}")

        ZonalStatisticsAsTable("latest_shape", zoneField, topoRaster, outTable,
                          "DATA", "ALL")
    
    arcpy.CheckInExtension("Spatial")
    
    statFlds = ["MIN", "MAX", "MEDIAN", "MEAN"]
    statCln = ["Minimum", "Maximum", "Median", "Mean"]
    
    vals = [row for row in arcpy.da.SearchCursor(outTable, statFlds)]
    valsList = list(vals[0]) # Forcing the list of 1 tuple returned by the SearchCursor to a plain list
    
    roundedValsList = [round(elem, 2) for elem in valsList]
    
    df = pd.DataFrame({tblTitle: statCln, '': roundedValsList})
    
    return str(df.to_html(index=False))

# Write HTML to Report
def writeToReport(report_doc_location, HTML_to_insert, HTML_element_ID):
    reportTemplate = open(report_doc_location)
    soup = BeautifulSoup(reportTemplate, "html.parser")
    text = soup.find_all(id=HTML_element_ID)[0]
    text.clear()
    temp = BeautifulSoup(HTML_to_insert, features= "lxml")
    nodesToInsert = temp.find('body').children
    for i, node in enumerate(nodesToInsert):
        text.insert(i, node)
    html = soup.prettify("utf-8")
    with open(report_doc_location, "wb") as file:
        file.write(html)

# Get fire info
def getFireInfo(fire_feature_class):
    '''
    The search cursor returns a list of tuples, with each tuple representing individual rows of the feature class being searched.
    The index_selection variable is made to return the last (most recent) row for the fire perimeter. That variable is used to 
    select the right tuple returned by the search cursor. Then that single tuple is turned into a list for use later. 
    '''
    index_selection = int(arcpy.GetCount_management(fire_feature_class)[0]) - 1
    
    fire_info = []
    with arcpy.da.SearchCursor(fire_feature_class, ["poly_IncidentName", "attr_UniqueFireIdentifier", "Shape_Area"]) as cursor:
        for row in cursor:
            fire_info.append(row)
            
    fire_info_list = list(fire_info[index_selection])
    acres = add_commas(round(fire_info_list[2]/4046.8564224))
    fire_info_list[2] = acres
    
    return fire_info_list

def buildReport(data_package):
    
    try:
        # data_package = arcpy.GetParametersAsText(0) # Get data package location
        
        # Get fire ID, geodatabase, feature class
        fire_id = os.path.split(data_package)[1]
        fire_gdb = os.path.join(data_package, fire_id + ".gdb")
        fire_fc = os.path.join(fire_gdb, fire_id)

        # Copy template (want to leave the boilerplate document intact for other reports)
        report_doc = os.path.join(data_package, fire_id + "_Report.html")
        shutil.copyfile(os.path.join(data_package, "FireReportBoilerplate.html"), report_doc)
        
        # Insert HTML for fire name, ID, and acres into the report cover page
        fire_info = getFireInfo(fire_fc)
        name_id = f"<div>{fire_info[0]} Fire ({fire_info[1]}) Summary</div>"
        acres = f"<div>{fire_info[2]} Acres</div>"
        writeToReport(report_doc_location = report_doc, HTML_to_insert = name_id, HTML_element_ID = "coverName")
        writeToReport(report_doc_location = report_doc, HTML_to_insert = acres, HTML_element_ID = "coverAcres")

        # Population Summary
        census_blocks_layer = os.path.join(fire_gdb, "Population_CensusBlocks2020")
        summary_figs = popSummary(census_blocks_layer)
        total_pop_html = f"<span>{summary_figs[0]}</span>"
        writeToReport(report_doc, total_pop_html, "populationImpact")
        total_acres_html = f"<span>{summary_figs[1]}</span>"
        writeToReport(report_doc, total_acres_html, "totalAffectedAcres")
        pop_data_availability_html = f"<span>{summary_figs[2]}</span>"
        writeToReport(report_doc, pop_data_availability_html, "populationDataAvailability")

        # Surface Management Agency Summary Pie Chart
        sma = os.path.join(fire_gdb, "SMA")
        smaField = "MGMT_AGNCY"
        t = "Surface Management Agency Summary"
        acreagePieChart(sma, fire_fc, smaField, t, data_package)
        sma_chart = f'<img src="{smaField + "_PieChart.png"}">'
        writeToReport(report_doc, sma_chart, "smaChart")

        # Soils Summary Pie Chart 
        soil = os.path.join(fire_gdb, "Soils_gSSURGO")
        soil_field = "HYDROLGRP_DCD"
        t = "Hydrologic Soils Group Summary"
        acreagePieChart(soil, fire_fc, soil_field, t, data_package)
        soil_chart = f'<img src="{soil_field + "_PieChart.png"}">'
        writeToReport(report_doc, soil_chart, "soilChart")

        # Land Cover Summary Table
        evt_raster = os.path.join(data_package, "EVT.tif")
        land_cover_info = landCoverSummary(fire_fc, evt_raster)
        land_cover_table = land_cover_info[0]
        writeToReport(report_doc, land_cover_table, "landCoverTable") ## TODO: Re-format land cover table to look cleaner
        land_cover_text = land_cover_info[1]
        writeToReport(report_doc, land_cover_text, "landCoverText")

        # Topography Summary Tables
        aspect = os.path.join(data_package, "TopographyAspect_WesternUS.tif")
        aspect_table_html = topoStatTable(fire_fc, aspect, "Aspect")
        writeToReport(report_doc, aspect_table_html, "aspectTable")

        elev = os.path.join(data_package, "TopographyElevation_WesternUS_bepf.tif")
        elev_table_html = topoStatTable(fire_fc, elev, "Elevation")
        writeToReport(report_doc, elev_table_html, "elevationTable")

        slope = os.path.join(data_package, "TopographySlopeDegree_WesternUS.tif")
        slope_table_html = topoStatTable(fire_fc, slope, "Slope")
        writeToReport(report_doc, slope_table_html, "slopeTable")



        print("Success!")

    except Exception as e:
        print("Failure.")
        print(traceback.format_exc())
        print(e)

if __name__ == "__main__":

    data_package_location = arcpy.GetParameterAsText(0)

    buildReport(data_package_location)
