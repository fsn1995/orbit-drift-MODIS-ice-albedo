/**
 * This app would allow users to explore the orbit drift effect of MOD albedo and obtain time sereis of MOD and MYD albedo data. 
 * shunan.feng@envs.au.dk 
 */


/**
 * Data Preparation and Processing
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
var imgfilter = ee.Filter.and(
  ee.Filter.date(ee.Date.fromYMD(2000, 1, 1), ee.Date(Date.now())),
  ee.Filter.calendarRange(6, 8, 'month')
);

var greenlandmask = ee.Image('OSU/GIMP/2000_ICE_OCEAN_MASK')
                    .select('ice_mask'); //'ice_mask', 'ocean_mask'
var glims = ee.Image().paint(ee.FeatureCollection('GLIMS/current'), 1);          
var iceMask = ee.ImageCollection([
  greenlandmask,
  glims.rename('ice_mask')
]).mosaic().eq(1);

var mod = ee.ImageCollection('MODIS/006/MOD10A1').filter(imgfilter)
              .map(function(image){
                  return image.select(['Snow_Albedo_Daily_Tile'])
                              .rename('MODalbedo')
                              .divide(100)
                              .copyProperties(image, ['system:time_start'])
                              .set('SATELLITE', 'MOD');
                              // .set({date: ee.Date(image.get('system:time_start')).format('YYYY-MM-DD')});
                });       

var myd = ee.ImageCollection('MODIS/006/MYD10A1').filter(imgfilter)
              .map(function(image){
                  return image.select(['Snow_Albedo_Daily_Tile'])
                              .rename('MYDalbedo')
                              .divide(100)
                              .copyProperties(image, ['system:time_start'])
                              .set('SATELLITE', 'MYD');
                              // .set({date: ee.Date(image.get('system:time_start')).format('YYYY-MM-DD')});
                });             


var joinedMODIS = ee.ImageCollection(ee.Join.inner().apply({
primary: mod,
secondary: myd,
condition: ee.Filter.equals({leftField: 'system:index', rightField: 'system:index'})
}));             

// Map a function to merge the results in the output FeatureCollection.
var dataset = joinedMODIS.map(function(feature) {
  return ee.Image.cat(feature.get('primary'), feature.get('secondary'));
});

var imDiff = dataset.map(function(image){
  var imDiff = image.select('MODalbedo').subtract(image.select('MYDalbedo')).rename('imDiff');
  var imMean = (image.select('MODalbedo').add(image.select('MYDalbedo'))).multiply(0.5);
  var imNoise = imDiff.abs().divide(imMean.abs());
  var immask = imNoise.lt(1);
  return image.addBands(imDiff.updateMask(immask));
});

var medianDelta = imDiff.filterDate("2002-01-01", "2019-12-31").select('imDiff').median(); // experiment at pixel level 
// var medianDelta = ee.Image(0); // if we use the value for the GrIS. 

var dtSeries = imDiff.filterDate("2020-01-01", "2020-12-31").map(function(image){
  var imDiff = image.select('imDiff').subtract(medianDelta).rename('dt');
  return image.addBands(imDiff);
});

var dt = dtSeries.select('dt').median();

// Export the image, specifying the CRS, transform, and region.
Export.image.toDrive({
  image: dt,
  description: 'dt',
  crs: 'EPSG:3411',
  scale: 500,
  // crsTransform: projection.transform,
  region: aoi
});