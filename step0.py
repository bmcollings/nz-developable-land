### remove undedevelopable areas (water bodies) using NZ LCDB
# and calc slope for potential developable area ###

# import modules
from osgeo import gdal
import pandas as pd 
pd.set_option('display.max_rows', 10)

import geopandas as gpd

# track time
import time
start = time.time()
last = time.time()

# import csv containing lat/long for FUAs and create points gpd
fua_df = pd.read_csv('inputs/FUA-test.csv')
fua_gdf = gpd.GeoDataFrame(fua_df, geometry=gpd.points_from_xy(fua_df.longitude, fua_df.latitude), crs='EPSG:4326').to_crs(2193)

# create 70km buffer for each FUA to get aoi
fua_gdf['aoi'] = fua_gdf.buffer(70000)

buffer = fua_gdf.buffer(70000)
buffer.to_file('inputs/buffer.shp')

print(fua_gdf)

print('buffering FUAs complete')
print(time.time() - last, 'seconds')
last = time.time()
print() 

# import LCDB and return water bodies 
water_bodies = gpd.read_file('inputs/lcdb-v50-land-cover-database-version-50-mainland-new-zealand.shp')

water_bodies = water_bodies[water_bodies.Name_2018.isin(['Not land', 'Lake or Pond', 'River', 'Estuarine Open Water', 'Mangrove']) == False]

print(water_bodies)

print('loading water_bodies complete')
print(time.time() - last, 'seconds')
last = time.time()
print() 

# Calculate slope for potential developable land within each FUA
# import and mask dem and write output to inputs folder 
dem = 'inputs/nz-dem-15m-2193.kea'

# Clip water_bodies by each aoi
for index, row in fua_gdf.iterrows():
    namePath = 'inputs/' + row['Name']
    
    print(row)

    aoi_path = namePath + '_aoi.shp'
    developable_area = water_bodies.geometry.clip(row['aoi'])
    developable_area.to_file(aoi_path)

    developable_area_path = namePath + '_aoi.kea'

    # mask dem to get potential developable pixels within FUA aoi with gdal warp
    gdal.Warp(destNameOrDestDS=developable_area_path,
    srcDSOrSrcDSTab=dem, format='kea', cutlineDSName=aoi_path, cutlineLayer=row['Name'] + '_aoi', cropToCutline=True)

    print('masking dem complete')
    print(time.time() - last, 'seconds')
    last = time.time()
    print() 

    # Calculate slope using gdal DEMprocessing
    destPath = namePath + '-slope-test.kea'
    srcDS = developable_area_path

    gdal.DEMProcessing(destName=destPath, srcDS=developable_area, processing='slope', format='kea', slopeFormat='degree')

    print('calculating slope complete')
    print(time.time() - last, 'seconds')
    last = time.time()
    print()

print('Total processing time')
print(time.time() - start, 'seconds')
last = time.time()
print() 

