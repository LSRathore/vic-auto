"""
Created on Tue May 14 2019
@author: Lokendra Singh Rathore
@National Institute of Hydrology, Roorkee, India
@email: lokendra.nalu@gmail.com

This script is to generate forcing files
for Variable Infiltration Capacity (VIC) hydrologic model
It downloads the rainfall, min temp, max temp and wind speed data from ERA-Interim
Make sure you have an account on ECMWF and installed ECMWF key. For more details, visit:
https://confluence.ecmwf.int/display/WEBAPI/Accessing+ECMWF+data+servers+in+batch

The script is written in Python 2.7 and has been tested on ArcGIS version 10.5
If you have Python 3, then change put the parantheses after print command allover otherwise it will not run

Last Edited-
"""

#############################################################################################################################
#Following python libraries should be installed (arcpy, numpy, pandas, netCDF4 and ecmwf-api-client)

import arcpy
import pandas as pd
from netCDF4 import Dataset
import os
from math import *
import numpy as np
from ecmwfapi import ECMWFDataServer
#############################################################################################################################
##        EDIT THIS SECTION ONLY
 
workspace="M:\\rathore\\vic20km\\force"                    # Make a new folder and give its path
shape="G:\\Rathore\\vic_auto5\\shape_proj.shp"    #Shape file, coordinate- GCS WGS 1984
start_time="1979-01-01"    # FORMAT "YYYY-MM-DD"  ( Date must be in quotation marks)
end_time="2017-07-31"      #SAME FORMAT ^

decimal_pts=2  #no of decimal points in forcing file name
# grid size in degrees (on which the VIC will run)
cell_h=0.25
cell_w=0.25
###########################################################################################################################

os.chdir(workspace)
arcpy.env.workspace=workspace
arcpy.env.overwriteOutput=True

arcpy.MakeFeatureLayer_management(shape,"shape_lyr")
desc=arcpy.Describe("shape_lyr")
n=math.ceil(desc.extent.YMax)
w=math.floor(desc.extent.XMin)
s=math.floor(desc.extent.YMin)
e=math.ceil(desc.extent.XMax)

area=str(n)+"/"+str(w)+"/"+str(s)+"/"+str(e)
date_era=start_time+"/to/"+end_time
name_era_nc_file="force_auto_era_"+start_time[:4]+"_"+end_time[:4]+"_5km.nc"
server = ECMWFDataServer()
##CODE FOR FORECAST

print "Downloading weather data from ERA-Interim...\n"
print "It may take several minutes if time perioed is long or basin area is large..\n"

# server = ECMWFDataServer()
# server.retrieve({
#     "class": "ei",
#     "dataset": "interim",
#     "date": date_era,
#     "expver": "1",
#     "grid": "0.5/0.5",                        
#     "levtype": "sfc",
#     "param": "165.128/166.128/201.128/202.128/228.128",
#     "step": "12",
#     "stream": "oper",
#     "time": "00:00:00",
#     "area": area,
#     "type": "fc",
#     "format": "netcdf",
#     "target": name_era_nc_file,
# })

print "Downloaded the weather data, a netcdf file has been generated in the worskpace specified...\n"
nc=Dataset('M:\\rathore\\vic20km\\force\\force_auto_era_1979_2017_5km.nc')
lat=list(nc.variables['latitude'][:])
lon=list(nc.variables['longitude'][:])

top=desc.extent.YMax
bottom=desc.extent.YMin
left=desc.extent.XMin
right=desc.extent.XMax
origin=str(left)+" "+ str(bottom)
opposite=str(right)+" "+ str(top)
y_axis=str(left)+" "+str(bottom+0.010)

fish="fishnet.shp"



print "Making fishnet... \n"
arcpy.CreateFishnet_management(fish,origin, y_axis, str(cell_h),str(cell_w), "0", "0", opposite, "LABELS",geometry_type="POLYGON")


arcpy.AddGeometryAttributes_management(fish,"CENTROID")
cursor=arcpy.da.SearchCursor(fish,["FID","CENTROID_Y","CENTROID_X"])
l=[1,2,3]
for row in cursor:
    row=list(row)
    l=np.vstack((l,row))

ll=pd.DataFrame(l)
ll.columns=['fid','lat','lon']
ll=ll.iloc[1:,:]

print "Generating forcing files in a folder named force_auto_files...\n"
print "Columns of forcing files: Rainfall(m), Windspeed(m/s), Max Temperature and Minimum Temperature (C)...\n"

for i in range(len(ll)):
    latt=ll.iloc[i,1]
    lonn=ll.iloc[i,2]
    near_lat_era_idx=np.abs(np.asarray(lat)-latt).argmin()
    near_lon_era_idx=np.abs(np.asarray(lat)-latt).argmin()
    tp=pd.DataFrame(nc.variables["tp"][:,near_lat_era_idx,near_lon_era_idx],columns=["tp"])
    tmax=pd.DataFrame(nc.variables["mx2t"][:,near_lat_era_idx,near_lon_era_idx],columns=["tmax"])
    tmin=pd.DataFrame(nc.variables["mn2t"][:,near_lat_era_idx,near_lon_era_idx],columns=["tmin"])
    u10=pd.DataFrame(nc.variables["u10"][:,near_lat_era_idx,near_lon_era_idx],columns=["win"])
    v10=pd.DataFrame(nc.variables["v10"][:,near_lat_era_idx,near_lon_era_idx],columns=["win"])
    tp[tp<0]=0
    tp=tp*1000
    wind=np.sqrt(u10**2 + v10**2)
    tmax=tmax-273
    tmin=tmin-273
    final=pd.concat((tp,wind,tmax,tmin),axis=1)
    final=final.round(decimal_pts)
    temp_name="%."+str(decimal_pts)+"f"
    force_name="data_"+temp_name % latt + "_" + temp_name % lonn
    final.to_csv(force_name,index=None, header=None, sep="\t")


print "**********Successfully generated forcing files**************"

###################################################################################################################
