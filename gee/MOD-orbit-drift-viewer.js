/**
 * This app would allow users to explore the orbit drift effect of MOD albedo and obtain time sereis of MOD and MYD albedo data. 
 * shunan.feng@envs.au.dk 
 */


/**
 * Data Preparation and Processing
 */

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


var palettes = require('users/gena/packages:palettes');
var dtvis = {min:-0.15, max:0.15, palette: palettes.colorbrewer.RdBu[11]};
Map.setCenter(-41.0, 74.0, 4);
Map.setOptions('TERRAIN');
Map.addLayer(dt.updateMask(iceMask), dtvis , 'd(t)');

/**
* Webapp UI
*/

var drawingTools = Map.drawingTools();

drawingTools.setShown(false);

while (drawingTools.layers().length() > 0) {
var layer = drawingTools.layers().get(0);
drawingTools.layers().remove(layer);
}

var dummyGeometry =
ui.Map.GeometryLayer({geometries: null, name: 'geometry', color: '23cba7'});

drawingTools.layers().add(dummyGeometry);

function clearGeometry() {
var layers = drawingTools.layers();
layers.get(0).geometries().remove(layers.get(0).geometries().get(0));
}

function drawRectangle() {
clearGeometry();
drawingTools.setShape('rectangle');
drawingTools.draw();
}

function drawPolygon() {
clearGeometry();
drawingTools.setShape('polygon');
drawingTools.draw();
}

function drawPoint() {
clearGeometry();
drawingTools.setShape('point');
drawingTools.draw();
}

var chartPanel = ui.Panel({
style:
  {height: '235px', width: '600px', position: 'middle-right', shown: false}
});
var chartPanel2 = ui.Panel({
  style:
    {height: '235px', width: '600px', position: 'bottom-right', shown: false}
});

Map.add(chartPanel);
Map.add(chartPanel2);

function chartTimeSeries() {
// Make the chart panel visible the first time a geometry is drawn.
if (!chartPanel.style().get('shown')) {
chartPanel.style().set('shown', true);
}

if (!chartPanel2.style().get('shown')) {
chartPanel2.style().set('shown', true);
}
// Get the drawn geometry; it will define the reduction region.
var aoi = drawingTools.layers().get(0).getEeObject();

// Set the drawing mode back to null; turns drawing off.
drawingTools.setShape(null);

var chart =
  ui.Chart.image
      .series({
        imageCollection: dataset,
        region: aoi,
        reducer: ee.Reducer.mean(),
        scale: 500,
        xProperty: 'system:time_start'
      })
      .setSeriesNames(['MODalbedo', 'MYDalbedo'])
      .setChartType('ScatterChart')
      .setOptions({
        title: 'Time series of MOD and MYD albedo',
        hAxis: {title: 'Date', titleTextStyle: {italic: false, bold: true}},
        vAxis: {
          title: 'Albedo',
          titleTextStyle: {italic: false, bold: true}
        },
      //   lineWidth: 5,
        colors: ['e37d05', '1d6b99'],
      //   curveType: 'function'
      pointSize: 6,
      dataOpacity: 0.5
      });
// Replace the existing chart in the chart panel with the new chart.
chartPanel.widgets().reset([chart]);

var chart2 =
  ui.Chart.image
      .series({
        imageCollection: dtSeries.select('dt'),
        region: aoi,
        reducer: ee.Reducer.mean(),
        scale: 500,
        xProperty: 'system:time_start'
      })
      .setSeriesNames(['d(t)'])
      .setChartType('ScatterChart')
      .setOptions({
        title: 'Orbit drift effect on time series of MOD albedo',
        hAxis: {title: 'Date', titleTextStyle: {italic: false, bold: true}},
        vAxis: {
          title: 'd(t)',
          titleTextStyle: {italic: false, bold: true}
        },
        lineWidth: 5,
        colors: ['e37d05'],
        curveType: 'function'
      // pointSize: 6,
      // dataOpacity: 0.5
      });
// Replace the existing chart in the chart panel with the new chart.
chartPanel2.widgets().reset([chart2]);

}


// print(chart);

drawingTools.onDraw(ui.util.debounce(chartTimeSeries, 500));
drawingTools.onEdit(ui.util.debounce(chartTimeSeries, 500));


var symbol = {
rectangle: '⬛',
polygon: '🔺',
point: '📍',
line: '📍',
};



// The namespace for our application.  All the state is kept in here.
var app = {};

/** Creates the UI panels. */
app.createPanels = function() {
/* The introduction section. */
app.intro = {
  panel: ui.Panel([
    ui.Label({
      value: 'MODIS Orbit Drift Effect',
      style: {fontWeight: 'bold', fontSize: '24px', margin: '10px 5px'}
    }),
    ui.Label('This app allows you to visualize the orbit drift effect (d(t)) on time series of albedo and obtain summer time series of MOD (MOD10A1.006) and MYD (MYD10A1.006) albedo. ' +
             'Simply click and draw a point on the map! ' ),
    ui.Label('NOTE: this web app calculates d(t) at pixel level for the entire Greenland Ice Sheet and glaciers recorded in the GLIMS database. '+
             'So the median\u0394\u03B1 is adjusted for each pixel individually.')             
  ])
};

/* The collection filter controls. */
app.filters = {
  // mapCenter: ui.Checkbox({label: 'Filter to map center', value: true}),
  // scalem: ui.Textbox('scale', '30'),
  // applyButton: ui.Button('Apply Scale', app.applyPoint),
  // loadingLabel: ui.Label({
  //   value: 'Loading...',
  //   style: {stretch: 'vertical', color: 'gray', shown: false}
  // }),
  drawline: ui.Button({
      label: symbol.point + 'Draw a point',
      onClick: drawPoint,
      style: {stretch: 'horizontal'}
    }),
};



/* The panel for the filter control widgets. */
app.filters.panel = ui.Panel({
  widgets: [
    ui.Label('Define point of interest', {fontWeight: 'bold'}),
  //   ui.Label('Scale'), app.filters.scalem,
    // app.filters.mapCenter,
    ui.Panel([
      // app.filters.applyButton,
      // app.filters.loadingLabel,
      app.filters.drawline,
    ], 
    ui.Panel.Layout.flow('horizontal'))
  ],
  style: app.SECTION_STYLE
});

/*  panel for logo and deep purple website */
var logo = ee.Image('projects/ee-deeppurple/assets/dplogo').visualize({
  bands:  ['b1', 'b2', 'b3'],
  min: 0,
  max: 255
  });
var thumb = ui.Thumbnail({
  image: logo,
  params: {
      dimensions: '107x111',
      format: 'png'
      },
  style: {height: '107px', width: '111px',padding :'0'}
  });

app.deeppurple ={
  logo: ui.Panel(thumb, 'flow', {width: '120px'}),
  panel: ui.Panel([
    ui.Label("The Deep Purple project receives funding from the European Research Council (ERC) under the European Union's Horizon 2020 research and innovation programme under grant agreement No 856416."),
    ui.Label("https://www.deeppurple-ercsyg.eu/home", {}, "https://www.deeppurple-ercsyg.eu/home"),
    ui.Label("https://github.com/fsn1995/orbit-drift-MODIS-ice-albedo", {}, "https://github.com/fsn1995/orbit-drift-MODIS-ice-albedo")
  ])
};
}


//   /* The panel for the export section with corresponding widgets. */
//   app.export.panel = ui.Panel({
//     widgets: [
//       ui.Label('4) Start an export', {fontWeight: 'bold'}),
//       app.export.button
//     ],
//     style: app.SECTION_STYLE
//   });
// };

/** Creates the app helper functions. */
app.createHelpers = function() {
/**
 * Enables or disables loading mode.
 * @param {boolean} enabled Whether loading mode is enabled.
 */
app.setLoadingMode = function(enabled) {
  // Set the loading label visibility to the enabled mode.
  app.filters.loadingLabel.style().set('shown', enabled);
  // Set each of the widgets to the given enabled mode.
  var loadDependentWidgets = [
    // app.vis.select,
  //   app.filters.scalem,
  //   app.filters.applyButton,
    app.filters.drawline,
    // app.picker.select,
    // app.picker.centerButton,
    // app.export.button
  ];
  loadDependentWidgets.forEach(function(widget) {
    widget.setDisabled(enabled);
  });
};

/** Applies the selection filters currently selected in the UI. */
//   app.applyPoint = function() {
//     app.setLoadingMode(false);
//     var scalem = ee.Number.parse(app.filters.scalem.getValue());
//   };

};


/** Creates the app constants. */
app.createConstants = function() {
// app.COLLECTION_ID = 'LANDSAT/LC08/C01/T1_RT_TOA';
app.SECTION_STYLE = {margin: '20px 0 0 0'};
app.HELPER_TEXT_STYLE = {
    margin: '8px 0 -3px 8px',
    fontSize: '12px',
    color: 'gray'
};
};

/*
* Legend setup
*/

// Creates a color bar thumbnail image for use in legend from the given color
// palette.
function makeColorBarParams(palette) {
return {
  bbox: [0, 0, 1, 0.1],
  dimensions: '100x10',
  format: 'png',
  min: 0,
  max: 1,
  palette: palette,
};
}

// Create the color bar for the legend.
var colorBar = ui.Thumbnail({
image: ee.Image.pixelLonLat().select(0),
params: makeColorBarParams(dtvis.palette),
style: {stretch: 'horizontal', margin: '0px 8px', maxHeight: '24px'},
});

// Create a panel with three numbers for the legend.
var legendLabels = ui.Panel({
widgets: [
  ui.Label(dtvis.min, {margin: '4px 8px'}),
  ui.Label(
      (0),
      {margin: '4px 8px', textAlign: 'center', stretch: 'horizontal'}),
  ui.Label(dtvis.max, {margin: '4px 8px'})
],
layout: ui.Panel.Layout.flow('horizontal')
});

var legendTitle = ui.Label({
value: 'Map Legend: Orbit Drift Effect d(t)',
style: {fontWeight: 'bold'}
});

var legendPanel = ui.Panel([legendTitle, colorBar, legendLabels]);




/** Creates the application interface. */
app.boot = function() {
app.createConstants();
app.createHelpers();
app.createPanels();
var main = ui.Panel({
  widgets: [
    app.intro.panel,
    app.filters.panel,
    legendPanel,
    app.deeppurple.logo,
    app.deeppurple.panel
  ],
  style: {width: '320px', padding: '8px'}
});
ui.root.insert(0, main);

};

app.boot();
