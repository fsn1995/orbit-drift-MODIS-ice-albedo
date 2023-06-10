var greenlandmask = ee.Image('OSU/GIMP/2000_ICE_OCEAN_MASK')
                   .select('ice_mask').eq(1); // #'ice_mask', 'ocean_mask'    

var imgfilter = ee.Filter.and(
    ee.Filter.date('2018-01-01', '2022-12-31'),
    ee.Filter.calendarRange(6, 8, 'month')
);
var dataset = ee.ImageCollection('MODIS/006/MOD10A1')
                .filter(imgfilter)
                .select("Snow_Albedo_Daily_Tile");

// // define landtrendr parameters
// var runParams = { 
//   timeSeries:             dataset,    
//   maxSegments:            6,
//   spikeThreshold:         0.9,
//   vertexCountOvershoot:   3,
//   preventOneYearRecovery: true,
//   recoveryThreshold:      0.25,
//   pvalThreshold:          0.05,
//   bestModelProportion:    0.75,
//   minObservationsNeeded:  6
// };
// var lt = ee.Algorithms.TemporalSegmentation.LandTrendr(runParams);

// define ccdc parameters
var runParams = {
    collection: dataset,
    breakpointBands: null, // only 1 band available
    tmaskBands: null, // Tmask cloud detection, not needed
    minObservations: 6, // The number of observations required to flag a change.
    chiSquareProbability: 0.5, // [0, 1]
    minNumOfYearsScaler: 1.22, // Factors of minimum number of years to apply new fitting.
    dateFormat: 2, // 0 = jDays, 1 = fractional years, 2 = unix time in milliseconds.
}

var imgtrend = ee.Algorithms.TemporalSegmentation.Ccdc(runParams).updateMask(greenlandmask);

Map.addLayer(imgtrend);
Map.addLayer(imgtrend.select("tBreak"));
