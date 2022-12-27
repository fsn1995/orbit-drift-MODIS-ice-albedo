# %% [markdown]
# This python script samples arctic dem product and harmonized satellite 
# albedo from random sampling points generated in previous step.
# 
# To do list:
# Speed is limited using for loops. This should be definitely avoided.
# 
# Users should change the size of spatial window when extracting the pixel values. 

# %%
import geemap
import ee
import pandas as pd

# %% [markdown]
# # Prepare sample sites

# %%
Map = geemap.Map()
Map

# %%
# greenlandmask = ee.Image('OSU/GIMP/2000_ICE_OCEAN_MASK') \
#                    .select('ice_mask').eq(1) #'ice_mask', 'ocean_mask'
# arcticDEM = ee.Image('UMN/PGC/ArcticDEM/V3/2m_mosaic')

# arcticDEMgreenland = arcticDEM.updateMask(greenlandmask)

# visPara = {'min': 0,  'max': 3000.0, 'palette': ['0d13d8', '60e1ff', 'ffffff']}
# # visPara = {'min': 0,  'max': 3000.0, 'palette': palette}

# Map.addLayer(arcticDEMgreenland, visPara, 'Arctic DEM terrain')
# Map.setCenter(-41.0, 74.0, 3)
# Map.add_colorbar(visPara, label="Elevation (m)", discrete=False, orientation="vertical", layer_name="Arctic DEM terrain")

# %%
randomPoints = ee.FeatureCollection("projects/ee-deeppurple/assets/orbitdrift/randomGrIS5km")
Map.addLayer(randomPoints, {}, 'Random points')
# geemap.ee_export_vector(randomPoints, 'randomPoints.kmz')

# %%
sampleN = randomPoints.size().getInfo()
sampleList = randomPoints.geometry().coordinates().getInfo()

# %% [markdown]
# ## Albedo

# %%
def addVisnirAlbedo(image):
    albedo = image.expression(
        '0.7605 * Blue + 0.8090 * Green - 1.8376 * Red + 0.9145 * NIR + 0.1627',
        {
            'Blue': image.select('Blue'),
            'Green': image.select('Green'),
            'Red': image.select('Red'),
            'NIR': image.select('NIR')
        }
    ).rename('visnirAlbedo')
    return image.addBands(albedo).copyProperties(image, ['system:time_start'])

# %%
''''if vis-nir bands albedo'''
rmaCoefficients = {
  'itcpsL7': ee.Image.constant([-0.0084, -0.0065, 0.0022, -0.0768]),
  'slopesL7': ee.Image.constant([1.1017, 1.0840, 1.0610, 1.2100]),
  'itcpsS2': ee.Image.constant([0.0210, 0.0167, 0.0155, -0.0693]),
  'slopesS2': ee.Image.constant([1.0849, 1.0590, 1.0759, 1.1583])
}; #rma
# Function to get and rename bands of interest from OLI.
def renameOli(img):
  return img.select(
    ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'QA_PIXEL', 'QA_RADSAT'], #'QA_PIXEL', 'QA_RADSAT'
    ['Blue',  'Green', 'Red',   'NIR',   'QA_PIXEL', 'QA_RADSAT']) #'QA_PIXEL', 'QA_RADSAT'

# Function to get and rename bands of interest from ETM+, TM.
def renameEtm(img):
  return img.select(
    ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'QA_PIXEL', 'QA_RADSAT'], #,   'QA_PIXEL', 'QA_RADSAT'
    ['Blue',  'Green', 'Red',   'NIR',   'QA_PIXEL', 'QA_RADSAT']) #, 'QA_PIXEL', 'QA_RADSAT'

# Function to get and rename bands of interest from Sentinel 2.
def renameS2(img):
  return img.select(
    ['B2',   'B3',    'B4',  'B8',  'QA60', 'SCL'],
    ['Blue', 'Green', 'Red', 'NIR', 'QA60', 'SCL']
  )

def oli2oli(img):
  return img.select(['Blue', 'Green', 'Red', 'NIR']) \
    .toFloat()

def etm2oli(img):
  return img.select(['Blue', 'Green', 'Red', 'NIR']) \
    .multiply(rmaCoefficients["slopesL7"]) \
    .add(rmaCoefficients["itcpsL7"]) \
    .toFloat()
    # .round() \
    # .toShort() 
    # .addBands(img.select('pixel_qa'))

def s22oli(img):
  return img.select(['Blue', 'Green', 'Red', 'NIR']) \
    .multiply(rmaCoefficients["slopesS2"]) \
    .add(rmaCoefficients["itcpsS2"]) \
    .toFloat()
    # .round() \
    # .toShort() # convert to Int16
    # .addBands(img.select('pixel_qa'))

def imRangeFilter(image):
  maskMax = image.lt(1)
  maskMin = image.gt(0)
  return image.updateMask(maskMax).updateMask(maskMin)

'''
Cloud mask for Landsat data based on fmask (QA_PIXEL) and saturation mask 
based on QA_RADSAT.
Cloud mask and saturation mask by sen2cor.
Codes provided by GEE official. '''

# the Landsat 8 Collection 2
def maskL8sr(image):
  # Bit 0 - Fill
  # Bit 1 - Dilated Cloud
  # Bit 2 - Cirrus
  # Bit 3 - Cloud
  # Bit 4 - Cloud Shadow
  qaMask = image.select('QA_PIXEL').bitwiseAnd(int('11111', 2)).eq(0)
  saturationMask = image.select('QA_RADSAT').eq(0)

  # Apply the scaling factors to the appropriate bands.
  # opticalBands = image.select('SR_B.').multiply(0.0000275).add(-0.2)
  # thermalBands = image.select('ST_B.*').multiply(0.00341802).add(149.0)

  # Replace the original bands with the scaled ones and apply the masks.
  #image.addBands(opticalBands, {}, True) \ maybe not available in python api
  return image.select(['Blue', 'Green', 'Red', 'NIR']).multiply(0.0000275).add(-0.2) \
    .updateMask(qaMask) \
    .updateMask(saturationMask)

  
# the Landsat 4, 5, 7 Collection 2
def maskL457sr(image):
  # Bit 0 - Fill
  # Bit 1 - Dilated Cloud
  # Bit 2 - Unused
  # Bit 3 - Cloud
  # Bit 4 - Cloud Shadow
  qaMask = image.select('QA_PIXEL').bitwiseAnd(int('11111', 2)).eq(0)
  saturationMask = image.select('QA_RADSAT').eq(0)

  # Apply the scaling factors to the appropriate bands.
  # opticalBands = image.select('SR_B.')
  # opticalBands = image.select('SR_B.').multiply(0.0000275).add(-0.2)
  # thermalBand = image.select('ST_B6').multiply(0.00341802).add(149.0)

  # Replace the original bands with the scaled ones and apply the masks.
  return image.select(['Blue', 'Green', 'Red', 'NIR']).multiply(0.0000275).add(-0.2) \
      .updateMask(qaMask) \
      .updateMask(saturationMask)
 #
 # Function to mask clouds using the Sentinel-2 QA band
 # @param {ee.Image} image Sentinel-2 image
 # @return {ee.Image} cloud masked Sentinel-2 image
 #
def maskS2sr(image):
  qa = image.select('QA60')

  # Bits 10 and 11 are clouds and cirrus, respectively.
  cloudBitMask = 1 << 10
  cirrusBitMask = 1 << 11
  # Bits 1 is saturated or defective pixel
  not_saturated = image.select('SCL').neq(1)
  # Both flags should be set to zero, indicating clear conditions.
  mask = qa.bitwiseAnd(cloudBitMask).eq(0) \
      .And(qa.bitwiseAnd(cirrusBitMask).eq(0)) 

  return image.updateMask(mask).updateMask(not_saturated).divide(10000)


# %%
# Define function to prepare OLI images.
def prepOli(img):
  orig = img
  img = renameOli(img)
  img = maskL8sr(img)
  img = oli2oli(img)
  img = imRangeFilter(img)
  # img = addTotalAlbedo(img)
  img = addVisnirAlbedo(img)
  return ee.Image(img.copyProperties(orig, orig.propertyNames()))

# Define function to prepare ETM+/TM images.
def prepEtm(img):
  orig = img
  img = renameEtm(img)
  img = maskL457sr(img)
  img = etm2oli(img)
  img = imRangeFilter(img)
  # img = addTotalAlbedo(img)
  img = addVisnirAlbedo(img)
  return ee.Image(img.copyProperties(orig, orig.propertyNames()))

# Define function to prepare S2 images.
def prepS2(img):
  orig = img
  img = renameS2(img)
  img = maskS2sr(img)
  img = s22oli(img)
  img = imRangeFilter(img)
  # img = addTotalAlbedo(img)
  img = addVisnirAlbedo(img)
  return ee.Image(img.copyProperties(orig, orig.propertyNames()).set('SATELLITE', 'SENTINEL_2'))


# %%
# dem related functions
# def demtool(img):
#     img = img.updateMask(greenlandmask)
#     demproduct = ee.Terrain.products(img)
#     return demproduct

# %%
# https://developers.google.com/earth-engine/tutorials/community/intro-to-python-api-guiattard by https://github.com/guiattard
def ee_array_to_df(arr, list_of_bands):
    """Transforms client-side ee.Image.getRegion array to pandas.DataFrame."""
    df = pd.DataFrame(arr)

    # Rearrange the header.
    headers = df.iloc[0]
    df = pd.DataFrame(df.values[1:], columns=headers)

    # Remove rows without data inside.
    df = df[['longitude', 'latitude', 'time', *list_of_bands]]#.dropna()

    # Convert the data to numeric values.
    for band in list_of_bands:
        df[band] = pd.to_numeric(df[band], errors='coerce')

    # Convert the time field into a datetime.
    # df['datetime'] = pd.to_datetime(df['time'], unit='ms')

    # Keep the columns of interest.
    df = df[['time', 'longitude', 'latitude', *list_of_bands]].dropna()

    return df

# %%
date_start = ee.Date.fromYMD(2021, 1, 1)
date_end = ee.Date.fromYMD(2022, 12, 31)

# %%
for i in range(0, len(sampleList)):

  print('The feature id is: %d out of %d, %s' %(i, len(sampleList), pd.Timestamp.today()))
  
  
  aoi = ee.Geometry.Point(sampleList[i])
  # Map.addLayer(aoi, {}, stationName)
  

  # create filter for image collection
  colFilter = ee.Filter.And(
      ee.Filter.geometry(aoi), # filterbounds not available on python api https://github.com/google/earthengine-api/issues/83
      ee.Filter.date(date_start, date_end),
      ee.Filter.calendarRange(6, 8, 'month')
      # ee.Filter.lt('CLOUD_COVER', 50)
  )

  s2colFilter =  ee.Filter.And(
      ee.Filter.geometry(aoi), # filterbounds not available on python api https://github.com/google/earthengine-api/issues/83
      ee.Filter.date(date_start, date_end),
      ee.Filter.calendarRange(6, 8, 'month'),
      ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 50)
  )
  oli2Col = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2') \
              .filter(colFilter) \
              .map(prepOli) \
              .select(['visnirAlbedo'])
  oliCol = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \
              .filter(colFilter) \
              .map(prepOli) \
              .select(['visnirAlbedo'])
  etmCol = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2') \
              .filter(colFilter) \
              .filter(ee.Filter.calendarRange(1999, 2020, 'year')) \
              .map(prepEtm) \
              .select(['visnirAlbedo'])
  tmCol = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2') \
              .filter(colFilter) \
              .map(prepEtm) \
              .select(['visnirAlbedo'])
  tm4Col = ee.ImageCollection('LANDSAT/LT04/C02/T1_L2') \
              .filter(colFilter) \
              .map(prepEtm) \
              .select(['visnirAlbedo'])
  s2Col = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
              .filter(s2colFilter) \
              .map(prepS2) \
              .select(['visnirAlbedo'])
  # landsatCol = etmCol.merge(tmCol)
  landsatCol = oliCol.merge(etmCol).merge(tmCol).merge(tm4Col).merge(oli2Col)
  multiSat = landsatCol.merge(s2Col).sort('system:time_start', True)# // Sort chronologically in descending order.
  if multiSat.size().getInfo()==0:
    continue
  # export albedo as csv
  pointAlbedo = multiSat.getRegion(aoi, 500).getInfo() # The number e.g. 500 is the buffer size
  dfalbedo = ee_array_to_df(pointAlbedo, ['visnirAlbedo'])
  dfalbedo["id"] = i
  pointAlbedoFile = '/data/shunan/data/orbit/poiHSA5km.csv'


  if i==0:
      dfalbedo.dropna().to_csv(pointAlbedoFile, mode='w', index=False, header=True)
  else:
      dfalbedo.dropna().to_csv(pointAlbedoFile, mode='a', index=False, header=False)



# %%

