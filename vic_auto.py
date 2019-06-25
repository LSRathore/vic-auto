
"""
Created on Sat Apr 13 2019
@author: Lokendra Singh Rathore
@National Institute of Hydrology, Roorkee, India
@email: lokendra.nalu@gmail.com
This script is to generate vegetation parameter and soil parameter file 
for Variable Infiltration Capacity (VIC) hydrologic model
It does not generate Forcing files
The script is written in Python 2.7 and has been tested on ArcGIS version 10.5
If you have Python 3, then change put the parantheses after print command allover otherwise it will not run
"""


#############################################################################################################################
#Following python libraries should be installed
import arcpy
import os
import pandas as pd
import numpy as np

############################################################################################################################

### Edit the path of following files:
### Note: Coordinate system for all input files should be : GCS WGS 1984 
###Use \\ or / for file path, dont use \
### Make sure, there is not any space in the file or folder name (use _ insted)


workspace="M:\\rathore\\vic20km\\gis"          ## Put location a folder, all files will be saved in there (TIP: Create a fresh folder)
shape_file="G:\\Rathore\\vic_auto5\\shape_proj.shp"        #Shapefile of the basin area. Make sure its cordinates are GCS WGS 1984
dem="G:\\Rathore\\vic_auto5\\dem_extfill"                  #DEM "  "  "  "  "  "        "    "        "        "      "
lulc="G:\\Rathore\\swat_inp\\soil_lulc\\lulc.tif"          #LULC image of area  (TO MAKE VEG PARAMETER FILE)
soil="M:\\rathore\\vic20km\gis\\soil_fao_sb.tif"   #SOIL Image  (To make soil parameter file)
rooting_depth_csv="C:\\Python27\\ArcGIS10.5\\vic_auto\\RootingDepths.csv"  ##Root depth csv file, provided with the docs
soil_appendix="C:\\Python27\\ArcGIS10.5\\vic_auto\\soil_appendix_3layer.xlsx"  ##Soil appendix, provied with docs

###Cell height and width in degree, Edit acc
cell_h=0.25
cell_w=0.25

##########################################################################################################################
## DO NOT EDIT ANYTHING##
arcpy.env.overwriteOutput = True
arcpy.env.workspace=workspace 
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("WGS 1984")
os.chdir(workspace)
root=pd.read_csv(rooting_depth_csv)

desc = arcpy.Describe(shape_file)
print(("Extent:\n  XMin: {0}, XMax: {1}, YMin: {2}, YMax: {3}".format(desc.extent.XMin, desc.extent.XMax, desc.extent.YMin, desc.extent.YMax)))
top=desc.extent.YMax
bottom=desc.extent.YMin
left=desc.extent.XMin
right=desc.extent.XMax
origin=str(left)+" "+ str(bottom)
opposite=str(right)+" "+ str(top)
y_axis=str(left)+" "+str(bottom+0.010)
#direc=arcpy.env.workspace+"\\"
grid_name="fishnet_f.shp"

print "Making fishnet... \n"
arcpy.CreateFishnet_management(grid_name,origin, y_axis, str(cell_h),str(cell_w), "0", "0", opposite, "LABELS",geometry_type="POLYGON")
arcpy.AddField_management(shape_file, "basin_pt", "SHORT", 0, "", "", "refcode", "NULLABLE", "REQUIRED")
arcpy.CalculateField_management(shape_file,field="basin_pt",expression="1")
arcpy.Union_analysis(["fishnet_f.shp",shape_file], 'union.shp', 'ALL', '#', 'GAPS')
arcpy.AddField_management("union.shp","area1","DOUBLE")
arcpy.AddField_management("fishnet_f.shp", "run_grid", "SHORT", 0, "", "", "refcode", "NULLABLE", "REQUIRED")
print "Calculating area of each grid cell after union... \n"
arcpy.CalculateField_management("union.shp","area1",'!shape.area!',"PYTHON")
temp_layer=arcpy.MakeFeatureLayer_management("union.shp","temp_lyr")
arcpy.SelectLayerByAttribute_management(temp_layer,"NEW_SELECTION","basin_pt=1 AND area1>= 10000000")
print "Making run grid... \n"
arcpy.CopyFeatures_management(temp_layer,"new_run_grid")
arcpy.AddField_management("new_run_grid.shp", "run_grid1", "SHORT", 0, "", "", "refcode", "NULLABLE", "REQUIRED")
arcpy.CalculateField_management("new_run_grid.shp","run_grid1",'1')

arcpy.DeleteField_management(shape_file,"basin_pt")

d= {k:v for k,v in arcpy.da.SearchCursor("new_run_grid.shp",["FID_Fishne","run_grid1"])}

with arcpy.da.UpdateCursor("fishnet_f.shp",["FID","run_grid"]) as cursor:
    for row in cursor:
        if row[0] in d:
            row[1]=d[row[0]]
            cursor.updateRow(row)
print "Created run grid named new_run_grid.shp"

arcpy.MakeFeatureLayer_management("fishnet_f.shp","fish_lyr")
print "Calculating elevation ...\n"
arcpy.AddField_management("fish_lyr","ELEVATION","FLOAT")
arcpy.gp.ZonalStatisticsAsTable_sa("fish_lyr","FID",dem,"ele_tab",'DATA','MEAN')


ddd={k:v for k,v in arcpy.da.SearchCursor("ele_tab",["FID","MEAN"])}
with arcpy.da.UpdateCursor("fish_lyr",["FID","ELEVATION"]) as cursor:
    for row in cursor:
        if row[0] in ddd:
            row[1]=ddd[row[0]]
            cursor.updateRow(row)

arcpy.SelectLayerByAttribute_management("fish_lyr","NEW_SELECTION",'"run_grid"=1')

arcpy.AddField_management("fish_lyr","SOIL","SHORT")
print "Indetifying soil texture... \n"
arcpy.gp.ZonalStatisticsAsTable_sa("new_run_grid.shp","FID_fishne",soil,"soil_tab",'DATA','MAJORITY')

dd={k:v for k,v in arcpy.da.SearchCursor("soil_tab",["FID_fishne","MAJORITY"])}
with arcpy.da.UpdateCursor("fish_lyr",["FID","SOIL"]) as cursor:
    for row in cursor:
        if row[0] in dd:
            row[1]=dd[row[0]]
            cursor.updateRow(row)

arcpy.AddField_management("fish_lyr","lat","FLOAT")
arcpy.AddField_management("fish_lyr","lon","FLOAT")
print "Identifying centroid locations of each grid cells ... \n"
arcpy.CalculateField_management("fish_lyr","lat","!SHAPE.CENTROID.Y!","PYTHON_9.3")
arcpy.CalculateField_management("fish_lyr","lon","!SHAPE.CENTROID.X!","PYTHON_9.3")

arcpy.AddField_management("fish_lyr","slope","FLOAT")
print "The x,y are in degeree and z (elevation) is in meter, so the z=0.000009 was used bcoz 1 meter ~ 0.000009 (CAN BE CHANGED ACCORDINGLY)... \n"
arcpy.gp.Slope_sa(dem, 'slope_temp', 'PERCENT_RISE',"0.000009")   # The x,y are in degeree and z in meter, so 1 meter ~ 0.000009 (CAN BE CHANGED ACCORDINGLY)
(arcpy.Raster('slope_temp')/100).save("slope_per")

print("Calculating slope... \n")
arcpy.gp.ZonalStatisticsAsTable_sa("fish_lyr","FID","slope_per","slope_tab",'DATA','MEAN')
arcpy.AddJoin_management("fish_lyr","FID","slope_tab","FID")
arcpy.CalculateField_management("fish_lyr","fishnet_f.slope","!slope_tab:MEAN!","PYTHON")
arcpy.RemoveJoin_management("fish_lyr","slope_tab")

print "Creating final fishnet (fishnet_final.shp) which consists rungrid, lat, lon, elevation, soil and slope values for all run cell ... \n"
arcpy.CopyFeatures_management("fish_lyr","fishnet_final.shp")
arcpy.AddField_management("fishnet_final.shp","area","FLOAT")
arcpy.CalculateField_management("fishnet_final.shp","area","!shape.area!","PYTHON")


print "Preparing soil parameter file, dont open any files until it completes \n"
arcpy.ExcelToTable_conversion(soil_appendix,"soil_app1")
arcpy.AddJoin_management("fish_lyr","SOIL","soil_app1","SOIL_CLASS")
cols=[a.name for a in arcpy.ListFields("fish_lyr")]
cols_to_take=[cols[0]]+cols[3:5]+cols[6:9]+cols[12:]
arcpy.ExportXYv_stats("fish_lyr",cols_to_take,"COMMA","temp_soil.csv","ADD_FIELD_NAMES")
temp=pd.read_csv(workspace+"\\"+"temp_soil.csv")
temp=temp.iloc[:,2:]

temp["dsmax"]=temp["FISHNET_F.SLOPE"]*temp["SOIL_APP1:KSAT_Z1"]
temp["grid_no"]=temp['FISHNET_F.FID']
temp=temp.drop(['FISHNET_F.FID','FISHNET_F.SLOPE'],axis=1)
c1=temp.columns.tolist()
colord=[c1[0]]+[c1[-1]]+c1[2:6]+[c1[-2]]+c1[6:20]+[c1[1]]+c1[20:-2]
new_temp=temp[colord]
os.chdir(workspace)

arcpy.AddJoin_management("fish_lyr","SOIL","soil_app1","SOIL_CLASS")
cols=[a.name for a in arcpy.ListFields("fish_lyr")]
cols_to_take=[cols[0]]+cols[3:5]+cols[6:9]+cols[12:]
arcpy.ExportXYv_stats("fish_lyr",cols_to_take,"COMMA","temp_soil.csv","ADD_FIELD_NAMES")
temp=pd.read_csv(workspace+"\\"+"temp_soil.csv")
temp=temp.iloc[:,2:]

temp["dsmax"]=temp["FISHNET_F.SLOPE"]*temp["SOIL_APP1:KSAT_Z1"]
temp["grid_no"]=temp['FISHNET_F.FID']
temp=temp.drop(['FISHNET_F.FID','FISHNET_F.SLOPE'],axis=1)
c1=temp.columns.tolist()
colord=[c1[0]]+[c1[-1]]+c1[2:6]+[c1[-2]]+c1[6:20]+[c1[1]]+c1[20:-2]
new_temp=temp[colord]
new_temp=new_temp.dropna(axis=0)
os.chdir(workspace)
new_temp.to_csv("soil_parameter_new.txt",index=None,sep="\t")
arcpy.RemoveJoin_management("fish_lyr","soil_app1")
print "soil parameter with name soil_parameter_new has been generated, it is located in worskpace \n"


print "Generating vegetation par file... \n"
arcpy.gp.TabulateArea_sa("fish_lyr","FID",lulc,"Value","lulc_tab")
arcpy.TableToTable_conversion("lulc_tab",arcpy.env.workspace,"temp_lulc.csv")
temp_l=pd.read_csv(workspace+"\\"+"temp_lulc.csv")
temp_l=temp_l.drop(["OID"],axis=1)
temp_l["Run_grid"]=1
tc=temp_l.columns.tolist()
tc_new=[tc[0]]+[tc[-1]]+tc[1:-1]
temp_l=temp_l[tc_new]
grid_data=temp_l

df=pd.DataFrame()
for i in range(grid_data.shape[0]):
    if grid_data["Run_grid"][i]!= 0:
        NZ=np.count_nonzero(grid_data.iloc[i,2:])                 #no. of non zero lulc areas
        s=pd.DataFrame([grid_data["FID"][i],NZ,-9999,-9999,-9999,-9999,-9999,-9999,-9999]).T
        for j in range(2,grid_data.shape[1]):
            if grid_data.iloc[i,j]!=0:
                lulc_class=int(list(grid_data)[j].split("_")[1])
                fract=grid_data.iloc[i,j]/sum(grid_data.iloc[i,2:])
                for k in range(root.shape[0]):
                    if root.iloc[k,0]==lulc_class:
                        rvalues=root.iloc[k,1:]
                        s1=pd.DataFrame(pd.concat([pd.Series([-9999,lulc_class,fract]),rvalues])).T
                        s1.columns=range(9)
                        s=s.append(s1)
        df=df.append(s)

df.replace(-9999," ").to_excel("vegparam_python_test.xlsx",header=None,index=None)

print "Completed making vegetation par file (vegparam_python_test.xlsx), located in workspace\n"
print "Convert the excel file to tab delimited text file for VIC\n"
print "Vegetation parameter file and soil parameter file have been generated successfully. Remove the header line from soil par file\n"
print "****************************************************************************************\n"

############## SCRIPT FOR SONW/ELEVATION BAND FILE GENERATION ###################
user=input("\nDo you want to make snow/elevation band file? (type 0 for no, 1 for yes): \n")
if user==1:
    user_i=input("Type the number of elevation bands required: \n")
    dem_ext=arcpy.sa.ExtractByMask(dem,"fishnet_f.shp")
    dem_ext.save("dem_extfish.tif")
    dem_desc=arcpy.sa.Raster("dem_extfish.tif")
    d1=dem_desc.minimum
    d2=dem_desc.maximum
    band_dif=math.ceil((d2-d1)/user_i)
    remap=[]
    r1=d1
    print "The elevation band file will have the following range of bands: \n"
    for i in range(user_i):
        r= [r1+(i*band_dif), r1+band_dif*(i+1),i+1]
        print r
        remap.append(r)
    

    dem_re=arcpy.sa.Reclassify("dem_extfish.tif","VALUE",arcpy.sa.RemapRange(remap))
    dem_re.save("reclass_dem_eleband.tif")
    
    print "Elevation band file is being processed... \n"
    arcpy.RasterToPolygon_conversion(in_raster=dem_re,raster_field='VALUE',out_polygon_features="ras2poly_redem",simplify="NO_SIMPLIFY")
    arcpy.sa.TabulateArea("fishnet_f.shp","FID", "reclass_dem_eleband.tif", "VALUE","tab_area_eleband")
    arcpy.Union_analysis(["ras2poly_redem.shp","fishnet_f.shp"],"union_elebnd")
    arcpy.gp.ZonalStatisticsAsTable_sa('union_elebnd.shp', 'FID_ras2po', 'dem_extfish.tif', "ele_eachzonetab1", 'DATA', 'MEAN')
    arcpy.JoinField_management("union_elebnd.shp","FID_ras2po","ele_eachzonetab1","FID_ras2po")
    arcpy.TableToExcel_conversion("union_elebnd.shp","temp_eb.xls")
    
    temp_eb=pd.read_excel("temp_eb.xls")
    temp1=temp_eb[(temp_eb["run_grid"]>=0) & (temp_eb["FID_ras2po"]>=0)]
    temp2=temp1[["FID","FID_ras2po","FID_fishne","run_grid","MEAN",'gridcode']]
    pivot=pd.pivot_table(temp2,index=["FID_fishne","run_grid"],columns="gridcode",values="MEAN",aggfunc=np.mean,fill_value=0)
    
    arcpy.TableToExcel_conversion("tab_area_eleband","tabulate_area_temp.xls")
    tab_area=pd.read_excel("tabulate_area_temp.xls")
    tab_area["sum"]=tab_area.iloc[:,2:].sum(axis=1)
    df_rand=pd.DataFrame()
    for i in range(user_i):
        df_rand[str(i)]=tab_area.iloc[:,i+2]/tab_area["sum"]

    pivot=pivot.reset_index()
    pivot=pivot.drop("FID_fishne",axis=1)
    df_rand["gridcode"]=pivot.index
    pivot["gridcode"]=df_rand["gridcode"]
    dfm1=df_rand.merge(pivot,on="gridcode")
    dfm2=dfm1.merge(df_rand,on="gridcode")
    dfm2=dfm2[dfm2["run_grid"]==1]
    dfm2=dfm2.drop(["gridcode","run_grid"],axis=1)
    dfm2.to_csv("elebandfile_"+str(user_i),header=None,sep="\t")
    print "Elevation/snow band file with mentioned band numbers, has been prepared with the name of \n"
    print "elebandfile_"+str(user_i)+ "in the workspace."
