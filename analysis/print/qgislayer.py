'''
This part of script is to compare the spatial resolution of harmonized multisat
albedo and MODIS albedo product.
Users will need QGIS and the qgis-earthengine-plugin: https://gee-community.github.io/qgis-earthengine-plugin/

Shunan Feng (shunan.feng@envs.au.dk)
'''
#%% import library and prepare mask
import ee
from ee_plugin import Map


#%% 
greenlandmask = ee.Image('OSU/GIMP/2000_ICE_OCEAN_MASK') \
                   .select('ice_mask').eq(1) #'ice_mask', 'ocean_mask'



cellSize = 5000
seed = 2022
projcrs = "EPSG:3411"

def randomOffset(projection, seed):
  values = ee.FeatureCollection([ee.Feature(None, None)]) \
    .randomColumn('x', seed) \
    .randomColumn('y', seed) \
    .first()
  return projection.translate(values.get("x"), values.get("y"))

def displayGrid(proj, mask):
  cells = ee.Image.pixelCoordinates(proj.scale(2,2))
  return cells.subtract(cells.round()).zeroCrossing().reduce('sum').selfMask().updateMask(mask)

grid = randomOffset(ee.Projection(projcrs).atScale(cellSize), seed)
Map.addLayer(displayGrid(grid, greenlandmask), {'palette': ['#92222244']}, 'Strict Grid')

# %%
