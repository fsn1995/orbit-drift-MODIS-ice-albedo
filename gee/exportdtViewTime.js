/**
 * This script would allow users to explore the orbit drift effect of MOD albedo and obtain time sereis of MOD and MYD albedo data. 
 * 
 * shunan.feng@envs.au.dk 
 */


/**
 * Preparation
 */
var aoi = /* color: #ffc82d */ee.Geometry.Polygon(
  [[[-36.29516924635421, 83.70737243835941],
    [-51.85180987135421, 82.75597137647488],
    [-61.43188799635421, 81.99879137488564],
    [-74.08813799635422, 78.10103528196419],
    [-70.13305987135422, 75.65372336709613],
    [-61.08032549635421, 75.71891096312955],
    [-52.20337237135421, 60.9795530382023],
    [-43.41430987135421, 58.59235996703347],
    [-38.49243487135421, 64.70478286561182],
    [-19.771731746354217, 69.72271161037442],
    [-15.728762996354217, 76.0828635948066],
    [-15.904544246354217, 79.45091003031243],
    [-10.015872371354217, 81.62328742628017],
    [-26.627200496354217, 83.43179828852398],
    [-31.636966121354217, 83.7553561747887]]]); // whole greenland


var greenlandmask = ee.Image('OSU/GIMP/2000_ICE_OCEAN_MASK')
                    .select('ice_mask'); //'ice_mask', 'ocean_mask'
// var glims = ee.Image().paint(ee.FeatureCollection('GLIMS/current'), 1);          
// var iceMask = ee.ImageCollection([
//   greenlandmask,
//   glims.rename('ice_mask')
// ]).mosaic().eq(1);

/**
 * Export view time of MOD data
 */

var modPreFilter = ee.Filter.and(
  ee.Filter.date(ee.Date.fromYMD(2002, 1, 1), ee.Date.fromYMD(2020, 1, 1)),
  ee.Filter.calendarRange(6, 8, 'month')
);
var modPreDrift = ee.ImageCollection('MODIS/061/MOD11A1')
                  .filter(modPreFilter)
                  .filterBounds(aoi)
                  .select("Day_view_time"); 
var modImgPreDrift = modPreDrift.mean().updateMask(greenlandmask);

var modPostFilter = ee.Filter.and(
  ee.Filter.date(ee.Date.fromYMD(2022, 1, 1), ee.Date.fromYMD(2022, 12, 31)),
  ee.Filter.calendarRange(6, 8, 'month')
);
var modPostDrift = ee.ImageCollection('MODIS/061/MOD11A1')
                  .filter(modPostFilter)
                  .filterBounds(aoi)
                  .select("Day_view_time");
var modImgPostDrift = modPostDrift.mean().updateMask(greenlandmask);

// Export the image, specifying the CRS, transform, and region.
Export.image.toDrive({
  image: modImgPreDrift,
  description: 'modImgPreDrift',
  crs: 'EPSG:3411',
  scale: 500,
  // crsTransform: projection.transform,
  region: aoi
});
Export.image.toDrive({
  image: modImgPostDrift,
  description: 'modImgPostDrift',
  crs: 'EPSG:3411',
  scale: 500,
  // crsTransform: projection.transform,
  region: aoi
});

/**
 * Export view time of MYD data
 */

var mydPreFilter = ee.Filter.and(
  ee.Filter.date(ee.Date.fromYMD(2002, 1, 1), ee.Date.fromYMD(2020, 1, 1)),
  ee.Filter.calendarRange(6, 8, 'month')
);
var mydPreDrift = ee.ImageCollection('MODIS/061/MYD11A1')
                  .filter(mydPreFilter)
                  .filterBounds(aoi)
                  .select("Day_view_time");
var mydImgPreDrift = mydPreDrift.mean().updateMask(greenlandmask);

var mydPostFilter = ee.Filter.and(
  ee.Filter.date(ee.Date.fromYMD(2022, 1, 1), ee.Date.fromYMD(2022, 12, 31)),
  ee.Filter.calendarRange(6, 8, 'month')
);
var mydPostDrift = ee.ImageCollection('MODIS/061/MYD11A1')
                  .filter(mydPostFilter)
                  .filterBounds(aoi)
                  .select("Day_view_time");
var mydImgPostDrift = mydPostDrift.mean().updateMask(greenlandmask);

// Export the image, specifying the CRS, transform, and region.
Export.image.toDrive({
  image: mydImgPreDrift,
  description: 'mydImgPreDrift',
  crs: 'EPSG:3411',
  scale: 500,
  // crsTransform: projection.transform,
  region: aoi
});
Export.image.toDrive({
  image: mydImgPostDrift,
  description: 'mydImgPostDrift',
  crs: 'EPSG:3411',
  scale: 500,
  // crsTransform: projection.transform,
  region: aoi
});