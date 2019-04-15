# vic-auto
This script generates soil parameter and vegetation parameter files for Variable Infiltration Capacity VIC Model.

Some useful files (rooting depth and soil appendix) are provided with docs. Use 3 layers files.

Procedure to Follow:

1. Make sure python is installed and the following libraries are also

		arcpy
	
		pandas
	
		os

2. If unable to install arcpy, then:

		Go to C:\python\Arcgis10.x
	
		Open command prompt and cd to C:\python\Arcgis10.x
	
		Type in command prompt: python
	
		Type: import arcpy
	
		If the last command run without giving error, it means arcpy is installed in the Arcpy10.x folder
	
		Now save the vic_auto.py script in the same folder and run from there
	
3. The script is written in python2.7 and it gives error with python 3 and advanced versions. 
To use it in python3, change the all print commands (line:59, 66, 70, 83, 97, 110, 118, 124, 129, 148, 150, 180, 181). 
Put the print sentence in parantheses ()

4. Edit the vic_auto.py script from line 27 to 38 (Give the paths of requiered files):

		workspace= Path of folder where all files will be stored. Making a new folder is advised.
	
		shape_file=Basin shapefile path
	
		dem=DEM        
	
		lulc=LULC
	
		soil=Soil raster
	
		rooting_depth_csv= A csv file consists of rooting depth. It is provided with the code.
	
		soil_appendix= An excel file for soil properties. It is provided with code.
	
	
		Change cell_h and cell _w that are cell height and cell width accordingly. These variables are in degree so use (0.01, 0.05 instead of 1km, 5km ...)
	
5. All gis raster files should has cordinate system: GCS WGS 1984, if not then project files.

6. Prepare the soil raster according to soil_class and type in soil_appendix_3layer.xlsx file.

7. Prepare the land use land cover raster according to LULC_CLASS.xlsx file
