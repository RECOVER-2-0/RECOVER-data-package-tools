import arcpy, os
from matplotlib import pyplot as plt
import seaborn
from arcpy.sa import *
from IPython.display import HTML, display
import pandas as pd
from bs4 import BeautifulSoup
import shutil
import traceback

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
    
    plt.suptitle(chartTitle, fontsize = 14)
    plt.title("Total acreage: " + str(round(totalAcreage, 2)))

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
    print(vals)
    valsList = list(vals[0]) 
    
    fireFcShapeArea = [row[0] for row in arcpy.da.SearchCursor(zoneData, ["Shape_Area"])][0]
    lcAcres = valsList[5]

    pctCov = (round(lcAcres/(fireFcShapeArea/4046.8564224), 4) * 100)

    valsList.append(pctCov)
        
    #fldsVals = [fldsCln, valsList]
    
    df = pd.DataFrame({'Attribute': fldsCln, 'Value': valsList})
    
    #print(df.to_html(index=False, header=False))
    
    df = df.style.set_caption("MAJORITY EVT COVER").set_table_styles([{
        'selector': 'caption',
        'props': [
            ('text-align', 'center'),
            ('color', 'black'),
            ('font-size', '14px')
        ]
    }])

    #display(HTML(df.to_html(index=False)))
    return str(df.to_html(index=False))

# Topography Summary Tables    
def topoStatTable(zoneData, topoRaster, tblTitle):
    arcpy.CheckOutExtension("Spatial")
    
    zoneField = "poly_IncidentName" # Should always be the same
    outTable = "zStat_topo" 
    
    ZonalStatisticsAsTable(zoneData, zoneField, topoRaster, outTable,
                          "DATA", "ALL")
    
    arcpy.CheckInExtension("Spatial")
    
    statFlds = ["MIN", "MAX", "MEDIAN", "MEAN"]
    statCln = ["Minimum", "Maximum", "Median", "Mean"]
    
    vals = [row for row in arcpy.da.SearchCursor(outTable, statFlds)]
    valsList = list(vals[0]) # Forcing the list of 1 tuple returned by the SearchCursor to a plain list
    
    roundedValsList = [round(elem, 2) for elem in valsList]
    
    df = pd.DataFrame({tblTitle: statCln, '': roundedValsList})
    
    print(df.to_html(index=False))

    #display(HTML(df.to_html(index=False)))
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
    acres = round(fire_info_list[2]/4046.8564224)
    fire_info_list[2] = acres
    
    return fire_info_list

def buildReport():
    
    try:
        # data_package = arcpy.GetParametersAsText(0) # Get data package location
        data_package = r"C:\Users\coler\Documents\ArcGIS\Projects\ReportGeneration\Fire_2023_COSJF_000570"
        # Get fire ID, geodatabase, feature class
        fire_id = os.path.split(data_package)[1]
        fire_gdb = os.path.join(data_package, fire_id + ".gdb")
        fire_fc = os.path.join(fire_gdb, fire_id)

        # Copy template (want to leave the boilerplate document intact for other reports)
        report_doc = os.path.join(data_package, fire_id + "_Report.html")
        shutil.copyfile(os.path.join(data_package, "Report_Boilerplate.html"), report_doc)
        
        # Insert HTML for fire name, ID, and acres into the report cover page
        fire_info = getFireInfo(fire_fc)
        name_id = f"<div>{fire_info[0]} Fire ({fire_info[1]}) Summary</div>"
        acres = f"<div>{fire_info[2]} Acres</div>"
        writeToReport(report_doc_location = report_doc, HTML_to_insert = name_id, HTML_element_ID = "coverName")
        writeToReport(report_doc_location = report_doc, HTML_to_insert = acres, HTML_element_ID = "coverAcres")

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
        land_cover_table = landCoverSummary(fire_fc, evt_raster)
        writeToReport(report_doc, land_cover_table, "landCoverTable") ## TODO: Re-format land cover table to look cleaner

        # Topography Summary Tables


        print("Success!")

    except Exception as e:
        print("Failure.")
        print(traceback.format_exc())
        print(e)

if __name__ == "__main__":
    buildReport()
