/*
MODIS albedo
*/
var poi = ee.FeatureCollection("projects/ee-deeppurple/assets/orbitdrift/randomGrIS5km");

var imgfilter = ee.Filter.and(
    ee.Filter.date('2000-01-01', '2022-12-31'),
    ee.Filter.calendarRange(6, 8, 'month')
);
var dataset = ee.ImageCollection('MODIS/006/MOD10A1')
                .filter(imgfilter)
                .select("Snow_Albedo_Daily_Tile"); // Snow_Albedo_Daily_Tile_Class


// var datasetRename = dataset.map(function(img){
//   var timestr = ee.String(img.get('system:time_start'));
//   return img.rename(timestr);
// });
// var imgMODIS = datasetRename.toBands();  
var imgMODIS = dataset.toBands();  

// // Computed value is too large. (Error code: 3)
// var poiAlbedo = imgMODIS.reduceRegions({
//   collection: poi,
//   reducer: ee.Reducer.mean(),
//   scale: 500,
//   // crs: "EPSG:3411",
//   tileScale: 16
// });
// this will solve the error code: 3
var poiAlbedo = poi.map(function(feature) {
  return feature.set(imgMODIS.reduceRegion({
    reducer: ee.Reducer.mean(),
    scale: 500,
    tileScale:16,
    // crs: "EPSG:3411",
    geometry: feature.geometry()
  }));
});

Export.table.toDrive({
  collection: poiAlbedo,
  folder: "gee",
  description:'poiMODIS',
  fileFormat: 'CSV'
});

Export.table.toDrive({
  collection: poi,
  folder: "gee",
  description:'poiOrbitDrift',
  fileFormat: 'SHP'
});


/*
Harmonized Satellite Albedo
*/
var date_start = ee.Date.fromYMD(2000, 1, 1),
    date_end = ee.Date.fromYMD(2022, 1, 1);

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

/*
prepare harmonized satellite data
*/

// Function to get and rename bands of interest from OLI.
function renameOli(img) {
  return img.select(
    ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'QA_PIXEL', 'QA_RADSAT'], // 'QA_PIXEL', 'QA_RADSAT'
    ['Blue',  'Green', 'Red',   'NIR',   'QA_PIXEL', 'QA_RADSAT']);//'QA_PIXEL', 'QA_RADSAT';
}
// Function to get and rename bands of interest from ETM+, TM.
function renameEtm(img) {
  return img.select(
    ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'QA_PIXEL', 'QA_RADSAT'], //#,   'QA_PIXEL', 'QA_RADSAT'
    ['Blue',  'Green', 'Red',   'NIR',   'QA_PIXEL', 'QA_RADSAT']); // #, 'QA_PIXEL', 'QA_RADSAT'
}
// Function to get and rename bands of interest from Sentinel 2.
function renameS2(img) {
  return img.select(
    ['B2',   'B3',    'B4',  'B8',  'QA60', 'SCL'],
    ['Blue', 'Green', 'Red', 'NIR', 'QA60', 'SCL']
    //['B2',     'B3',      'B4',    'B8',    'B11',     'B12',     'QA60', 'SCL'],
    //['BlueS2', 'GreenS2', 'RedS2', 'NIRS2', 'SWIR1S2', 'SWIR2S2', 'QA60', 'SCL']
  );
}

/* RMA transformation */
var rmaCoefficients = {
  itcpsL7: ee.Image.constant([-0.0084, -0.0065, 0.0022, -0.0768]),
  slopesL7: ee.Image.constant([1.1017, 1.0840, 1.0610, 1.2100]),
  itcpsS2: ee.Image.constant([0.0210, 0.0167, 0.0155, -0.0693]),
  slopesS2: ee.Image.constant([1.0849, 1.0590, 1.0759, 1.1583])
}; // #rma

function oli2oli(img) {
  return img.select(['Blue', 'Green', 'Red', 'NIR'])
            .toFloat();
}

function etm2oli(img) {
  return img.select(['Blue', 'Green', 'Red', 'NIR'])
    .multiply(rmaCoefficients.slopesL7)
    .add(rmaCoefficients.itcpsL7)
    .toFloat();
}
function s22oli(img) {
  return img.select(['Blue', 'Green', 'Red', 'NIR'])
    .multiply(rmaCoefficients.slopesS2)
    .add(rmaCoefficients.itcpsS2)
    .toFloat();
}

function imRangeFilter(image) {
  var maskMax = image.lte(1);
  var maskMin = image.gt(0);
  return image.updateMask(maskMax).updateMask(maskMin);
}


/* 
Cloud mask for Landsat data based on fmask (QA_PIXEL) and saturation mask 
based on QA_RADSAT.
Cloud mask and saturation mask by sen2cor.
Codes provided by GEE official.
*/

// This example demonstrates the use of the Landsat 8 Collection 2, Level 2
// QA_PIXEL band (CFMask) to mask unwanted pixels.

function maskL8sr(image) {
  // Bit 0 - Fill
  // Bit 1 - Dilated Cloud
  // Bit 2 - Cirrus
  // Bit 3 - Cloud
  // Bit 4 - Cloud Shadow
  var qaMask = image.select('QA_PIXEL').bitwiseAnd(parseInt('11111', 2)).eq(0);
  var saturationMask = image.select('QA_RADSAT').eq(0);

  // Apply the scaling factors to the appropriate bands.
  // var opticalBands = image.select(['Blue', 'Green', 'Red', 'NIR']).multiply(0.0000275).add(-0.2);
  // var thermalBands = image.select('ST_B.*').multiply(0.00341802).add(149.0);

  // Replace the original bands with the scaled ones and apply the masks.
  return image.select(['Blue', 'Green', 'Red', 'NIR']).multiply(0.0000275).add(-0.2)
      // .addBands(thermalBands, null, true)
      .updateMask(qaMask)
      .updateMask(saturationMask);
}

// This example demonstrates the use of the Landsat 4, 5, 7 Collection 2,
// Level 2 QA_PIXEL band (CFMask) to mask unwanted pixels.

function maskL457sr(image) {
  // Bit 0 - Fill
  // Bit 1 - Dilated Cloud
  // Bit 2 - Unused
  // Bit 3 - Cloud
  // Bit 4 - Cloud Shadow
  var qaMask = image.select('QA_PIXEL').bitwiseAnd(parseInt('11111', 2)).eq(0);
  var saturationMask = image.select('QA_RADSAT').eq(0);

  // Apply the scaling factors to the appropriate bands.
  // var opticalBands = image.select('SR_B.').multiply(0.0000275).add(-0.2);
  // var thermalBand = image.select('ST_B6').multiply(0.00341802).add(149.0);

  // Replace the original bands with the scaled ones and apply the masks.
  return image.select(['Blue', 'Green', 'Red', 'NIR']).multiply(0.0000275).add(-0.2)
      // .addBands(thermalBand, null, true)
      .updateMask(qaMask)
      .updateMask(saturationMask);
}


/**
 * Function to mask clouds using the Sentinel-2 QA band
 * @param {ee.Image} image Sentinel-2 image
 * @return {ee.Image} cloud masked Sentinel-2 image
 */
function maskS2sr(image) {
  var qa = image.select('QA60');

  // Bits 10 and 11 are clouds and cirrus, respectively.
  var cloudBitMask = 1 << 10;
  var cirrusBitMask = 1 << 11;
  // 1 is saturated or defective pixel
  var not_saturated = image.select('SCL').neq(1);
  // Both flags should be set to zero, indicating clear conditions.
  var mask = qa.bitwiseAnd(cloudBitMask).eq(0)
      .and(qa.bitwiseAnd(cirrusBitMask).eq(0));

  // return image.updateMask(mask).updateMask(not_saturated);
  return image.updateMask(mask).updateMask(not_saturated).divide(10000);
}

// narrow to broadband conversion
function addVisnirAlbedo(image) {
  var albedo = image.expression(
    '0.7963 * Blue + 2.2724 * Green - 3.8252 * Red + 1.4143 * NIR + 0.2053',
    {
      'Blue': image.select('Blue'),
      'Green': image.select('Green'),
      'Red': image.select('Red'),
      'NIR': image.select('NIR')
    }
  ).rename('visnirAlbedo');
  return image.addBands(albedo).copyProperties(image, ['system:time_start']);
}


/* get harmonized image collection */

// Define function to prepare OLI images.
function prepOli(img) {
  var orig = img;
  img = renameOli(img);
  img = maskL8sr(img);
  img = oli2oli(img);
  //img = addTotalAlbedo(img);
  img = imRangeFilter(img);
  img = addVisnirAlbedo(img);
  return ee.Image(img.copyProperties(orig, orig.propertyNames()));
}
// Define function to prepare ETM+/TM images.
function prepEtm(img) {
  var orig = img;
  img = renameEtm(img);
  img = maskL457sr(img);
  img = etm2oli(img);
  //img = addTotalAlbedo(img);
  img = imRangeFilter(img);
  img = addVisnirAlbedo(img);
  return ee.Image(img.copyProperties(orig, orig.propertyNames()));
}
// Define function to prepare S2 images.
function prepS2(img) {
  var orig = img;
  img = renameS2(img);
  img = maskS2sr(img);
  img = s22oli(img);
  // img = addTotalAlbedo(img)
  img = imRangeFilter(img);
  img = addVisnirAlbedo(img);
  return ee.Image(img.copyProperties(orig, orig.propertyNames()).set('SATELLITE', 'SENTINEL_2'));
}

var colFilter = ee.Filter.and(
  ee.Filter.bounds(aoi),
  ee.Filter.date(date_start, date_end),
  ee.Filter.calendarRange(6, 8, 'month')
);

var s2colFilter =  ee.Filter.and(
  ee.Filter.bounds(aoi),
  ee.Filter.date(date_start, date_end),
  ee.Filter.calendarRange(6, 8, 'month'),
  ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 50)
);

var oli2Col = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2') 
    .filter(colFilter) 
    .map(prepOli)
    .select(['visnirAlbedo']); //# .select(['totalAlbedo']) or  .select(['visnirAlbedo'])
var oliCol = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') 
    .filter(colFilter) 
    .map(prepOli)
    .select(['visnirAlbedo']); //# .select(['totalAlbedo']) or  .select(['visnirAlbedo'])
var etmCol = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2') 
    .filter(colFilter) 
    .filter(ee.Filter.calendarRange(1999, 2020, 'year')) // filter out L7 imagaes acquired after 2020 due to orbit drift
    .map(prepEtm)
    .select(['visnirAlbedo']); // # .select(['totalAlbedo']) or  .select(['visnirAlbedo'])
var tmCol = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2') 
    .filter(colFilter) 
    .map(prepEtm)
    .select(['visnirAlbedo']); //# .select(['totalAlbedo']) or  .select(['visnirAlbedo'])
var tm4Col = ee.ImageCollection('LANDSAT/LT04/C02/T1_L2') 
    .filter(colFilter) 
    .map(prepEtm)
    .select(['visnirAlbedo']); //# .select(['totalAlbedo']) or  .select(['visnirAlbedo'])
var s2Col = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    .filter(s2colFilter) 
    .map(prepS2)
    .select(['visnirAlbedo']); //# .select(['totalAlbedo']) or  .select(['visnirAlbedo'])

var landsatCol = oliCol.merge(etmCol).merge(tmCol).merge(tm4Col).merge(oli2Col);
var multiSat = landsatCol.merge(s2Col).sort('system:time_start', true);

// Difference in days between start and finish
var diff = date_end.difference(date_start, 'day');

// Make a list of all dates
var dayNum = 1; // steps of day number
var range = ee.List.sequence(0, diff.subtract(1), dayNum).map(function(day){return date_start.advance(day,'day')});

// Function for iteration over the range of dates
var day_mosaics = function(date, newlist) {
  // Cast
  date = ee.Date(date)
  newlist = ee.List(newlist)

  // Filter collection between date and the next day
  var filtered = multiSat.filterDate(date, date.advance(dayNum,'day'));
  // Make the mosaic
  var image = ee.Image(
      filtered.mean().copyProperties(filtered.first()))
      .set({date: date.format('yyyy-MM-dd')})
      .set('system:time_start', filtered.first().get('system:time_start'));

  // Add the mosaic to a list only if the collection has images
  return ee.List(ee.Algorithms.If(filtered.size(), newlist.add(image), newlist));
};
var l9dayCol = ee.ImageCollection(ee.List(range.iterate(day_mosaics, ee.List([]))));

var datasetRename = l9dayCol.map(function(img){
  var timestr = ee.String(img.get('date'));
  return img.rename(timestr);
});
var imgHSA = datasetRename.toBands();  


var poiAlbedo = poi.map(function(feature) {
  return feature.set(imgHSA.reduceRegion({
    reducer: ee.Reducer.mean(),
    scale: 500,
    tileScale:16,
    // crs: "EPSG:3411",
    geometry: feature.geometry()
  }));
});

Export.table.toDrive({
  collection: poiAlbedo,
  folder: "gee",
  description:'poiHSA',
  fileFormat: 'CSV'
});

