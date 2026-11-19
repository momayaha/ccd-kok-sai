// CCD project: water-aperture extraction, version 2.0
// Paste into https://code.earthengine.google.com/ and Run.
// All candidate rows are retained, including those with zero valid pixels.
var observations = ee.FeatureCollection(
  'projects/YOUR_EE_PROJECT/assets/CCD_GEE_observations');
var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED');
var bands = ['B2', 'B3', 'B4', 'B8'];
var radii = ee.List([20, 30, 50]);
var maxSearchDays = 4;  // search envelope only; not a temporal acceptance rule
var firstRound = 1;
var lastRound = 22;
var rounds = ee.List.sequence(firstRound, lastRound);

// Same grid and common pixel mask for all four spectral bands.
var reducer = ee.Reducer.percentile([25, 50, 75]).unweighted()
  .combine({reducer2: ee.Reducer.count(), sharedInputs: true});

function extractRound(r) {
  var points = observations.filter(ee.Filter.eq('round', r));
  var first = ee.Feature(points.first());
  // Asset start_ms/end_ms are midnight UTC representations of Thai dates.
  // Convert interval boundaries to actual local midnight (UTC+7).
  var t0 = ee.Date(ee.Number(first.get('start_ms')))
      .advance(-7, 'hour').advance(-maxSearchDays, 'day');
  var t1 = ee.Date(ee.Number(first.get('end_ms')))
      .advance(-7, 'hour').advance(maxSearchDays + 1, 'day');

  var regions = ee.FeatureCollection(radii.map(function(radius) {
    return points.map(function(f) {
      f = ee.Feature(f);
      var point = f.geometry().transform('EPSG:4326', 1);
      var xy = ee.List(point.coordinates());
      return f.set({radius_m: radius,
                    reference_longitude: xy.get(0),
                    reference_latitude: xy.get(1)})
              .setGeometry(point.buffer(ee.Number(radius), 1));
    });
  })).flatten();

  var images = s2.filterBounds(regions.geometry(1)).filterDate(t0, t1);
  var extracted = images.toList(images.size().max(1)).map(function(item) {
    var im = ee.Image(item);
    var refl = im.select(bands).multiply(0.0001);
    var scl = im.select('SCL');  // native 20 m; nearest-neighbour on 10 m grid
    var available = refl.mask().reduce(ee.Reducer.min()).gt(0);
    var positive = refl.gt(0).reduce(ee.Reducer.min());
    var water = scl.eq(6);
    var valid = available.and(positive).and(water);
    var one = refl.select('B2').multiply(0).add(1).updateMask(available);
    var stack = refl.updateMask(valid)
      .addBands(one.rename('coverage'))
      .addBands(one.updateMask(water).rename('SCL6'));
    var stats = stack.reduceRegions({
      collection: regions.filterBounds(im.geometry()),
      reducer: reducer,
      crs: im.select('B2').projection(),
      scale: 10,
      tileScale: 4
    });
    var date = ee.Date(im.get('system:time_start'));
    return stats.map(function(f) {
      return ee.Feature(f).set({
        satellite_date_th: date.format('YYYY-MM-dd', 'Asia/Bangkok'),
        satellite_time_th: date.format('HH:mm:ss', 'Asia/Bangkok'),
        satellite_ms: date.millis(),
        image_id: im.get('system:index'),
        cloud_tile: im.get('CLOUDY_PIXEL_PERCENTAGE')
      });
    });
  });
  return ee.FeatureCollection(extracted).flatten();
}

var results = ee.FeatureCollection(rounds.map(extractRound)).flatten();
Map.centerObject(observations, 9);
Map.addLayer(observations, {color: 'red'}, 'Reference stations');
print('Observations in selected rounds:', observations.filter(
  ee.Filter.inList('round', rounds)).size());
print('Rounds to process:', rounds);
print('Open Tasks and run the export.');

var taskName = 'CCD_Sentinel2_aperture_v2_r' + firstRound + '_r' + lastRound;
Export.table.toDrive({
  collection: results,
  description: taskName,
  folder: 'CCD_Arsenic',
  fileNamePrefix: taskName,
  fileFormat: 'CSV',
  selectors: [
    'observation_id', 'station', 'river', 'round',
    'sampling_start', 'sampling_end', 'sampling_window_days',
    'coordinate_status', 'reference_latitude', 'reference_longitude',
    'radius_m', 'satellite_date_th', 'satellite_time_th', 'satellite_ms',
    'image_id', 'cloud_tile', 'coverage_count', 'SCL6_count',
    'B2_count', 'B3_count', 'B4_count', 'B8_count',
    'B2_p25', 'B2_p50', 'B2_p75',
    'B3_p25', 'B3_p50', 'B3_p75',
    'B4_p25', 'B4_p50', 'B4_p75',
    'B8_p25', 'B8_p50', 'B8_p75'
  ]
});
