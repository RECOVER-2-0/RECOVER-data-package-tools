import arcpy, os
from matplotlib import pyplot as plt
import seaborn
from arcpy.sa import *
from IPython.display import HTML, display
import pandas as pd
from bs4 import BeautifulSoup


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
        autopct = '%.0f%%')

    plt.savefig(os.path.join(outpath, "PieChart.png"))
    
# Land Cover Summary Table
def landCoverSummary(zoneData, fire_feature_class, valueRaster):
    arcpy.CheckOutExtension("Spatial")
    
    zoneField = "poly_IncidentName" # should always be the same
    outTable = "zStat_EVT"
    
    ZonalStatisticsAsTable(zoneData, zoneField, valueRaster, outTable,
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
    
    valsList = list(vals[0]) # For some reason, the search cursor returns a list of 1 tuple, so here we change it back into a list
    
    fireFcShapeArea = [row[0] for row in arcpy.da.SearchCursor(fire_feature_class, ["Shape_Area"])][0]
    lcAcres = valsList[5]

    pctCov = (round(lcAcres/(fireFcShapeArea/4046.8564224), 4) * 100)

    valsList.append(pctCov)
        
    fldsVals = [fldsCln, valsList]
    
    df = pd.DataFrame({'Attribute': fldsCln, 'Value': valsList})
    
    print(df.to_html(index=False, header=False))
    
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
def writeToReport(data_package_location, HTML_to_insert, HTML_element_ID):
    
    templatePath = os.path.join(data_package_location, "Report_Boilerplate.html")

    reportTemplate = open(templatePath)

    soup = BeautifulSoup(reportTemplate, "html.parser")

    text = soup.find_all(id=HTML_element_ID)[0]

    text.clear()

    temp = BeautifulSoup(HTML_to_insert)

    nodesToInsert = temp.find('body').children

    for i, node in enumerate(nodesToInsert):
        text.insert(i, node)


    html = soup.prettify("utf-8")
    with open(templatePath, "wb") as file:
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

def main():
    fireId = input("Please input a fire ID: (For example, Fire_2023_AZASF_000170)")
    # Path to data package folder
    fireDataPackage = os.path.join(os.path.dirname( arcpy.mp.ArcGISProject("CURRENT").filePath), fireId)
    fireGdb = os.path.join(fireDataPackage, fireId + ".gdb")
    fireFc = os.path.join(fireGdb, fireId)

    print(fireDataPackage)
    print(fireGdb)
    print(fireFc)