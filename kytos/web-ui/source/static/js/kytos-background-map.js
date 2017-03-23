function draw_background_map(callback=undefined) {
  set_status('Loading Map...');

  if (mapboxgl.supported()) {
    mapboxgl.accessToken = 'pk.eyJ1IjoiZGlyYW9sIiwiYSI6ImNpdjlweGl2bDAwamQyb3M5cmo2NmMzZnUifQ.QFVrOl-nUkV6D5RNoKmTJA';
    var map = new mapboxgl.Map({
          container: 'background-map',
          style: 'mapbox://styles/mapbox/dark-v9',
          center: default_settings.map_center,
          zoom: default_settings.map_zoom,
    }).on('load', function(){ if (callback) { callback(); }
    });
    window.background_map = map;
  } else {
    // as webGL is not supported (or, at least, mapboxgl) we will use
    // the older mapbox js lib, which is slower.

    // Loading the css
    var head  = document.getElementsByTagName('head')[0];
    var link  = document.createElement('link');
    link.id   = 'mapbox.css';
    link.rel  = 'stylesheet';
    link.type = 'text/css';
    link.href = 'static/css/vendors/mapbox.css';
    link.media = 'all';
    head.appendChild(link);

    // Loading the js lib
    $.getScript("static/js/vendors/mapbox.js", function(){
      L.mapbox.accessToken = 'pk.eyJ1IjoiZGlyYW9sIiwiYSI6ImNpdjlweGl2bDAwamQyb3M5cmo2NmMzZnUifQ.QFVrOl-nUkV6D5RNoKmTJA';
      var map = L.mapbox.map('background-map', 'mapbox.dark', {
          scrollWheelZoom: true,
          maxZoom: 20,
          minZoom: 2,
          loadingControl: true
      }).on('load', function(){ if (callback) { callback(); }
      }).setView([default_settings.map_center[1], default_settings.map_center[0]],
                 default_settings.map_zoom);

      window.background_map = map;
    });
  }
}
