function draw_background_map(callback=undefined) {
  mapboxgl.accessToken = 'pk.eyJ1IjoiZGlyYW9sIiwiYSI6ImNpdjlweGl2bDAwamQyb3M5cmo2NmMzZnUifQ.QFVrOl-nUkV6D5RNoKmTJA';
  var map = new mapboxgl.Map({
        container: 'background-map',
        style: 'mapbox://styles/mapbox/dark-v9',
        center: [-97.8445676, 35.3437248],
        zoom: 4
      });
  window.background_map = map;
  if (callback) {
    callback();
  }
}
