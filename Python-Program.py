#-------------------------------------------------------------------
# For CE 594R GIS Programming
# By: Stephen Duncan
#     Dustin Woodbury
# Group Name: GIS Dragons
# Project 1 (Python Atlas) Cell Tower Analysis
#-------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------
# Import modules
#-----------------------------------------------------------------------------------------------
import arcpy
from arcpy.sa import *
import os

#-----------------------------------------------------------------------------------------------
# Parameters defined
#-----------------------------------------------------------------------------------------------
cellular = arcpy.GetParameterAsText(0)
if cellular == '#' or not cellular:
    cellular = "cellular" # provide a default value if unspecified
Project_Counties = arcpy.GetParameterAsText(1)
if Project_Counties == '#' or not Project_Counties:
    Project_Counties = "Project_Counties" # provide a default value if unspecified
number_of_startPage = arcpy.GetParameterAsText(2)
if number_of_startPage == '#' or not number_of_startPage:
    number_of_startPage = 1 # provide a default value if unspecified	
countyBufferMiles = arcpy.GetParameterAsText(3)
if countyBufferMiles == '#' or not countyBufferMiles:
    countyBufferMiles = "1 Miles" # provide a default value if unspecified
KernalDense = arcpy.GetParameterAsText(4)
if KernalDense == '#' or not KernalDense:
    KernalDense = "20000" # provide a default value if unspecified
i=5 #To help make combining code with Dustin easier.
# DEM Raster
DEMToUse = arcpy.GetParameterAsText(i)
if DEMToUse == '#' or not DEMToUse:
	DEMToUse = 'DEMToUse'
# Roads Shapefile
RoadsToUse = arcpy.GetParameterAsText(i+1)
if RoadsToUse == '#' or not RoadsToUse:
	RoadsToUse = 'RoadsToUse'
# Buffer length
RoadBuffer = arcpy.GetParameterAsText(i+2)
if RoadBuffer == '#' or not RoadBuffer:
	RoadBuffer = '.0001 Miles'
# Optional Output Coordinate System Defaults to NAD_1983_UTM_Zone_12N if nothing chosen
OutputCordSystem = arcpy.GetParameterAsText(i+3)
if OutputCordSystem == '#' or not OutputCordSystem:
	OutputCordSystem = "PROJCS['NAD_1983_UTM_Zone_12N',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['false_easting',500000.0],PARAMETER['false_northing',0.0],PARAMETER['central_meridian',-111.0],PARAMETER['scale_factor',0.9996],PARAMETER['latitude_of_origin',0.0],UNIT['Meter',1.0]]"
# Optional Cellsize parameter (uses largest of inputs if not specified)
cellsize_option = arcpy.GetParameterAsText(i+4)
if cellsize_option == '#' or not cellsize_option:
	cellsize_option = "MAXOF"
#-----------------------------------------------------------------------------------------------
# End Parameters
#-----------------------------------------------------------------------------------------------
	
#-----------------------------------------------------------------------------------------------
# Set System Environment Settings
#-----------------------------------------------------------------------------------------------
arcpy.env.outputCoordinateSystem = OutputCordSystem
arcpy.env.cellSize = cellsize_option
arcpy.env.overwriteOutput = True
arcpy.env.workspace = "C:\\Users\\Stephen\\Documents\\CE594R_GISProgramming\\PythonProject.gdb"
#Set the current map as the map document
mxd = arcpy.mapping.MapDocument("CURRENT")
# Edit the right data frame
df = arcpy.mapping.ListDataFrames(mxd, "CurrentDataLayer")[0]
#-----------------------------------------------------------------------------------------------
# End System Environment Settings
#-----------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------
# Define Global Variable Names
#-----------------------------------------------------------------------------------------------
SlopeDEM = 'SlopeDEM'
ApprovedSlopes = 'ApprovedSlopes'
RoadsToUseBuffer = 'RoadsToUseBuffer'
S_R_Raster = 'S_R_Raster'
cellular_Clip = 'cellular_Clip'
OneProjectCounties = "OneProjectCounties"
oneCountyBuffer = "oneCountyBuffer"
CellTowerLocations = 'CellTowerLocations'
FinalRaster = 'FinalRaster'
#-----------------------------------------------------------------------------------------------
# End Global Variable Names
#-----------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------
# Using a function to analyze the slope, buffer the roads, and extract by mask all the different
# inputs and output a masked raster of good areas that fit both places.
# Inputs are as follows:
#	(1) Elevation DEM or NED you plan to use
#	(2) The roads shapefile you plan to use and buffer from
#	(3) The number you will use to buffer from the roads
#	(4) The output raster name
#-----------------------------------------------------------------------------------------------
def SlopeRasterMask(DEM1, ROADS1, BUFFERNUM, final_SLOPEROADMASK):
	
	# Now we run the slope tool to analyze it
	arcpy.AddMessage("Slope Tool Running")
	arcpy.gp.Slope_sa(DEM1, SlopeDEM, "DEGREE", "1")
	for j in range (100):
		pass
	
	# We next us the calc tool on it
	arcpy.AddMessage("Reclassifing Slope Tool Running")
	ReClassSlope = RemapRange([[-1,5,1],[5,90,"NODATA"]])
	a_slopeDEM = Reclassify(SlopeDEM, "Value", ReClassSlope, "NODATA")
	for j in range (100):
		pass
	
	# Now we need to buffer the roads shapefile
	arcpy.AddMessage("Buffer Tool Running")
	arcpy.Buffer_analysis(ROADS1, RoadsToUseBuffer, BUFFERNUM, "FULL", "ROUND", "ALL")
	for j in range (100):
		pass
	
	# Combine the Road Buffer with the Approved Slopes Raster with Extract by Mask
	arcpy.AddMessage("Extract by Mask Tool Running")
	arcpy.gp.ExtractByMask_sa(a_slopeDEM, RoadsToUseBuffer, final_SLOPEROADMASK)
	for j in range (100):
		pass
#-----------------------------------------------------------------------------------------------
# End SlopeRasterMask
#-----------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------
# This function is to help set the layout view. The different parameters are:
#	(1) The County Name you are looking at
#	(2) The Page Number you will start from
#	(3) THe Kernal Density used to produce the map
#-----------------------------------------------------------------------------------------------
def FinishMapLayout(County_Name, Start_Page, Kernal_Density):
	prj = arcpy.mapping.MapDocument("CURRENT")
	for elem in arcpy.mapping.ListLayoutElements(prj, "TEXT_ELEMENT"):
		if elem.name == "PageTitle":
			elem.text = "<FNT size=\"18\">" + County_Name + " County</FNT>"
			arcpy.AddMessage("Changing Map Title to: \"" + County_Name + " County\"")
		if elem.name == "PageNumber":
			elem.text = "<FNT size=\"12\">Page " + str(Start_Page) + "</FNT>"
			arcpy.AddMessage("Changing Page Number to: \"" + str(Start_Page) + "\"")
			Start_Page += 1
		if elem.name == "MapContent":
			elem.text = "<FNT size=\"12\">County: " + County_Name + "\r\nKernal Density: " + str(Kernal_Density) + "\r\n\r\nProduced by:\r\nGIS Dragons\r\nStephen Duncan\r\nDustin Woodbury\r\nDate: 28 Jan 2015\r\nProjection:\r\nNAD_1983_UTM_Zone_12N</FNT>"
			arcpy.AddMessage("Kernal Density used was: \"" + str(Kernal_Density) + "\"")
		arcpy.RefreshActiveView()
#-----------------------------------------------------------------------------------------------
# End FinishMapLayout
#-----------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------
# This function is to help set the PDF documents. The different parameters are:
#	(1) The County Name you will name the map for
#	(2) The Atlas Path you will save everything too
#-----------------------------------------------------------------------------------------------
def PDFstuff(mapname, AtlasPath, ActualPDFCreate, page):
	#Export map to pdf
	pdfmap=str(folder+"\\"+ mapname + str(county_count) + ".pdf")
		#In case we test or repeat the name...
	if os.path.exists(pdfmap):
		arcpy.AddMessage("Checking and Deleting an Old Map")
		os.remove(pdfmap)
	
	arcpy.AddMessage("Creating single map to add to Atlas")
	arcpy.mapping.ExportToPDF(mxd, pdfmap)

	#Adds County map to atlas
	if page > 1:
		ActualPDFCreate = arcpy.mapping.PDFDocumentOpen(AtlasPath)
	
	ActualPDFCreate.appendPages(pdfmap)

	#Saves the atlas PDF then opens it again to add the next map
	ActualPDFCreate.saveAndClose()
	ActualPDFCreate = arcpy.mapping.PDFDocumentOpen(AtlasPath)
#-----------------------------------------------------------------------------------------------
# End PDFstuff
#-----------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------
# Function to select counties, buffer counties,  clip with cellular and create raster.
# The different parameters are:
#	(1) The County Shapefile you wish to analyze
#	(2) The County Name you wish to find
#	(3) The Cell Tower Shapefile you wish to find the Kernal Density for
#	(4) The County Buffer distance you wish to use
#	(5) The name of the output raster
#	(6) THe Kernal Density number [sq km] to be used to produce the map
#-----------------------------------------------------------------------------------------------
def countyToRaster(Project_Counties1, countyName, cellular1, oneCountyBuffer1, CellTowerLocations1, KernalDense1):

	#For w in range(0,number_of_polys):
	# Process: Select
	#?find Name? using FID?
	arcpy.AddMessage("Select Tool Started")
	arcpy.Select_analysis(Project_Counties1, OneProjectCounties, "\"NAME\" = '" + countyName + "'")
	
	#Zoom To the new county Features, but don't put it on the legend
	myCurrentLayer = arcpy.mapping.Layer(OneProjectCounties)
	arcpy.mapping.AddLayer(df, myCurrentLayer, "BOTTOM")
	layer = arcpy.mapping.ListLayers(mxd, myCurrentLayer)[0]
	ext = layer.getExtent()
	df.extent = ext
	legend = arcpy.mapping.ListLayoutElements(mxd, "LEGEND_ELEMENT", "Legend")[0]
	legend.removeItem(layer)
	arcpy.mapping.RemoveLayer(df, layer)
	arcpy.RefreshActiveView()
	
	# Process: Buffer
	arcpy.AddMessage("Buffer Tool Started")
	arcpy.Buffer_analysis(OneProjectCounties, oneCountyBuffer1, countyBufferMiles, "FULL", "ROUND", "ALL")

	# Process: Clip
	arcpy.AddMessage("Clip Tool Started")
	arcpy.Clip_analysis(cellular1, oneCountyBuffer1, cellular_Clip, "")
	
	# Process: Kernel Density
	arcpy.AddMessage("Kernal Density Tool Started")
	b_DEM = KernelDensity(cellular_Clip, "NONE", cellsize_option, KernalDense1, "SQUARE_KILOMETERS")

	# Process: Reclassify (2)
	arcpy.AddMessage("Reclassifing Tool Started")
	c_DEM = b_DEM * 10000
	ReClassSlope2 = RemapRange([[0,20,1],[20,1000000000,"NODATA"]])
	d_DEM = Reclassify(c_DEM, "Value", ReClassSlope2, "NODATA")
	arcpy.gp.ExtractByMask_sa(d_DEM, OneProjectCounties, CellTowerLocations1)

	#arcpy.AddMessage("Displaying Raster")
	#myCurrentLayer = arcpy.mapping.Layer(CellTowerLocations1)
	#arcpy.mapping.AddLayer(df, myCurrentLayer, "AUTO_ARRANGE")
	#arcpy.RefreshActiveView()
	
#-----------------------------------------------------------------------------------------------
# End countyToRaster
#-----------------------------------------------------------------------------------------------

# folder path
folder="C:\\Users\\Stephen\\Documents\\CE594R_GISProgramming\\"

#Atlas pdf path
pdfPath=folder+"CellTowerAnalysis.pdf"

#Check if path exists
if os.path.exists(pdfPath):
	os.remove(pdfPath)

# Create the atlas pdf using the pdfPath
arcpy.AddMessage("Creating PDF at " + pdfPath)
pdfDoc = arcpy.mapping.PDFDocumentCreate(pdfPath)

# Now using Def SlopeRasterMask(1,2,3,4)
SlopeRasterMask(DEMToUse, RoadsToUse, RoadBuffer, S_R_Raster)
#myCurrentLayer = arcpy.mapping.Layer(S_R_Raster)
#arcpy.mapping.AddLayer(df, myCurrentLayer, "BOTTOM")

# finding name list for counties
myList = [row.getValue('NAME') for row in arcpy.SearchCursor(Project_Counties)]
pagenum = number_of_startPage

for county in myList:
	findName = county.replace('u','')
	arcpy.AddMessage("Working on " + findName + "County")
	# Analyze the County, Kernal, etc.
	county_count = 1
	
	for myDensity in KernalDense.split(';'):
		arcpy.AddMessage("Kernal Denisty # being used is: " + str(myDensity))
		arcpy.AddMessage("Kernal Denisty type being used is: " + str(type(myDensity)))
		countyToRaster(Project_Counties, findName, cellular, oneCountyBuffer, CellTowerLocations, float(myDensity))
		#myCurrentLayer = arcpy.mapping.Layer(CellTowerLocations)
		#arcpy.mapping.AddLayer(df, myCurrentLayer, "BOTTOM")
		
		#Finding the County Stuffs and Displaying it
		#arcpy.AddMessage('type of SRRaster:'+str(type(S_R_Raster)))
		e_DEM = Raster(S_R_Raster) * CellTowerLocations
		arcpy.gp.ExtractByMask_sa(e_DEM, Project_Counties, FinalRaster)
		arcpy.AddMessage("Displaying Raster")
		myCurrentLayer = arcpy.mapping.Layer(FinalRaster)
		arcpy.mapping.AddLayer(df, myCurrentLayer, "AUTO_ARRANGE")
		arcpy.RefreshActiveView()
		
		#PreDone = arcpy.mapping.Layer("PreDoneStuff")
		#arcpy.ApplySymbologyFromLayer_management(myCurrentLayer, PreDone)
		#arcpy.RefreshActiveView()
		
		# Now using Def FinishMapLayout(1,2,3)
		arcpy.AddMessage("Working on the map layout")
		FinishMapLayout(findName, int(pagenum), myDensity)
		pagenum = int(pagenum) + 1
		county_count = county_count + 1
		
		#Start the editing process for Creating and Editing the PDF Files
		arcpy.AddMessage("Creating and Editing PDF files")
		PDFstuff(findName, pdfPath, pdfDoc, int(pagenum) - 1)
		
		#Clear out the final raster for a new one.
		arcpy.Delete_management(FinalRaster)

#Out of Loop / Finishing off the Atlas
pdfDoc = arcpy.mapping.PDFDocumentOpen(pdfPath)
pdfDoc.saveAndClose()
