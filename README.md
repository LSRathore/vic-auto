# vic-auto

This python script generates soil parameter and vegetation parameter files for Variable Infiltration Capacity (VIC) Hydrologic Model. The script `vic_auto.py` also prepares the elevation/snow band file, if required.

Use *force_auto.py* to generate forcing files. Necessary files have been provided with documents. 

# Requirements

* The script  is written in python version 2.7, running it on python3 may produce error.

* *vic_auto.py* requires **arcpy** and **pandas** to run, make sure both are installed.

* This script needs the following files from users:

	a) DEM covering basin area
	
	b) Land use land cover map
	
	c) Soil map (If not available, use the [generate-soil-map](https://github.com/lokendrarathore/generate-soil-map) repo to generate a soil map for basin area)
	
	d) Shapefile of the catchment area

# How to Use

* Put all input files' location in *vic_auto.py* as mentioned there. Make sure that all the input files have the same co-ordinate system as stated in the file.

* Other required files are provided with this repo, provide thier locations also.

## Note

* While preparing the soil map, define the soil class types according to the provided soil appendix file.

* Use *vic_auto.py* for soil and vegetation file generation. An addition file *force_auto.py* is provided to generate meteorological forcing files for the basin area.
