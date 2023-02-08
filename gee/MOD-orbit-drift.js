

var imgfilter = ee.Filter.and(
    ee.Filter.date(ee.Date.fromYMD(2000, 1, 1), ee.Date(Date.now())),
    ee.Filter.calendarRange(6, 8, 'month')
);

var greenlandmask = ee.Image('OSU/GIMP/2000_ICE_OCEAN_MASK')
                      .select('ice_mask').eq(1); //'ice_mask', 'ocean_mask'
var mod = ee.ImageCollection('MODIS/006/MOD10A1').filter(imgfilter)
                .map(function(image){
                    return image.select(['Snow_Albedo_Daily_Tile'])
                                .rename('MODalbedo')
                                .divide(100)
                                .copyProperties(image, ['system:time_start'])
                                // .set({date: ee.Date(image.get('system:time_start')).format('YYYY-MM-DD')});
                  });       

var myd = ee.ImageCollection('MODIS/006/MYD10A1').filter(imgfilter)
                .map(function(image){
                    return image.select(['Snow_Albedo_Daily_Tile'])
                                .rename('MYDalbedo')
                                .divide(100)
                                .copyProperties(image, ['system:time_start'])
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
    return image.addBands(imDiff);
});

// var medianDelta = imDiff.filterDate("2002-01-01", "2019-12-31").select('imDiff').median(); // experiment at pixel level 
var medianDelta = ee.Image(0);

var dt = imDiff.filterDate("2020-01-01", "2020-12-31").map(function(image){
    var imDiff = image.select('imDiff').subtract(medianDelta).rename('dt');
    return image.addBands(imDiff);
}).select('dt').median();

var palettes = require('users/gena/packages:palettes');
Map.addLayer(dt.updateMask(greenlandmask), {min:-0.2, max:0.2, palette: palettes.colorbrewer.RdBu[11]}, 'd(t)');