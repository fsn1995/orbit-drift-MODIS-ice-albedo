# %% 
import geemap
import ee
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
sns.set_theme(style="darkgrid", font="Arial", font_scale=2)
# %%
Map = geemap.Map()
Map

# %%
"""
time range for calculating mean albedo
"""
date_start = ee.Date.fromYMD(2000,  3,  1)
date_end   = ee.Date.fromYMD(2022, 12, 31)

"""
time range for calculating anomaly 
too many concurrent aggretation error may occur
"""
# 
# date_start = ee.Date.fromYMD(2000,  3,  1)
# date_end   = ee.Date.fromYMD(2000, 12, 31)


# %% prepare img collection
greenlandmask = ee.Image('OSU/GIMP/2000_ICE_OCEAN_MASK') \
                   .select('ice_mask').eq(1) #'ice_mask', 'ocean_mask'
colFilter = ee.Filter.And(
        ee.Filter.date(date_start, date_end),
        # ee.Filter.calendarRange(6,8,"month")
        # ee.Filter.dayOfYear(173, 173) # June 22 near summer solstice
    )    

dataset = ee.ImageCollection('MODIS/006/MOD10A1') \
    .select("Snow_Albedo_Daily_Tile") \
    .filter(colFilter) \
    .map(lambda img: img.updateMask(greenlandmask))

"""export albedo image to asset to save time"""
aoi = ee.Image('OSU/GIMP/2000_ICE_OCEAN_MASK').geometry()#.bounds() 
meanAlbedo = dataset.mean()   

geemap.ee_export_image_to_asset(
    meanAlbedo,
    description="meanAlbedoGrISmodis",
    assetId="meanAlbedoGrISmodis",
    region=aoi,
    scale=500,
    maxPixels=1e11
)
'''
how to get corner coordinates: 
https://gis.stackexchange.com/questions/318959/get-lon-lat-of-a-top-left-corner-for-geometry-in-google-earth-engine
'''
# listCoords = ee.Array.cat(aoi.coordinates(), 1); 

# # get the X-coordinates
# xCoords = listCoords.slice(1, 0, 1)
# yCoords = listCoords.slice(1, 1, 2)

# xMin = xCoords.reduce('min', [0]).get([0,0])
# xMax = xCoords.reduce('max', [0]).get([0,0])
# yMin = yCoords.reduce('min', [0]).get([0,0])
# yMax = yCoords.reduce('max', [0]).get([0,0])

'''
alternatively, https://gist.github.com/graydon/11198540
list of country-bounding-boxes
'GL': ('Greenland', (-73.297, 60.03676, -12.20855, 83.64513)),
'''
xMin = -73.297
xMax = -12.20855
yMin = 60.03676
yMax = 83.64513
# %% prepare anomaly



# Difference between start and finish
# diff = date_end.difference(date_start, 'month')
diff = date_end.difference(date_start, 'month')

# Make a list of all dates
timestep = 1; # steps of time 

date_range = ee.List.sequence(0, diff.subtract(1), timestep).map(lambda month: date_start.advance(month,'month'))

# Funtion for iteraton over the range of dates
def getMonthly(date, newlist):
  # Cast
    date = ee.Date(date)
    newlist = ee.List(newlist)

    # Filter collection between date and the next day
    filtered = dataset.filterDate(date, date.advance(timestep,'month'))
    #   nimproperty = filtered.get()
    # Make the mosaic
    image = ee.Image(
        filtered.mean().copyProperties(filtered.first())) \
        .subtract(meanAlbedo)

    # Add the mosaic to a list only if the collection has images
    return ee.List(ee.Algorithms.If(filtered.size(), newlist.add(image.set('system:time_start', filtered.first().get('system:time_start'))), newlist))

img_col = ee.ImageCollection(ee.List(date_range.iterate(getMonthly, ee.List([]))))
col_size = img_col.size().getInfo()
imgList = img_col.toList(col_size)

# %%
"""
ref: 
Justin Braaten
https://gis.stackexchange.com/questions/362958/plotting-viirs-against-longitude-in-google-earth-engine
"""
# latImg = ee.Image.pixelLonLat().select('latitude')
latStep = 1
latStarts = ee.List.sequence(60, 84-latStep, latStep)

for i in range(col_size):
    img = ee.Image(imgList.get(i))

    def latitudinal_stats(lat):
        startLat = ee.Number(lat)
        endLat = startLat.add(latStep)
        stat = img.reduceRegion(**{
            'reducer': ee.Reducer.mean(),
            'geometry': ee.Geometry.Rectangle(xMin, startLat, xMax, endLat),
            'scale': 500, # Change scale as needed
            'bestEffort': True,
            'tileScale': 6, # 0.1-16,
            'maxPixels': 1e11
            })
        return ee.Feature(img.geometry(), stat).set('lat', lat)
    latStatList = latStarts.map(latitudinal_stats)
    lonStatsCol = ee.FeatureCollection(ee.List(latStatList))
    imgtime = img.get('system:time_start').getInfo()
    print(pd.to_datetime(imgtime, unit="ms"))
    
    # geemap.ee_export_vector_to_drive(
    #     lonStatsCol, 
    #     description=str(imgtime), 
    #     folder="export",
    #     fileFormat="CSV",
    # )
    
    if i==0:
        df = geemap.ee_to_pandas(lonStatsCol)
        df["timestamp"] = imgtime
    else:
        dfnew = geemap.ee_to_pandas(lonStatsCol)
        dfnew["timestamp"] = imgtime
        df = pd.concat([df, dfnew])



# %%
