var default_settings = {
      /* Topology settings */
      show_unused_interfaces: true,
      show_disconnected_hosts: true,
      show_topology: true,
      topology_transformation: 'translate(0,0) scale(1)',
      /* Map settings */
      show_map: true,
      map_opacity: 0.4,
      map_center: [-97.8445676, 35.3437248],
      map_zoom: 4,
      /* Switch carousel and card settings */
      switches_carousel: {
        margin: 10,
        nav: true,
        owlNrow: true, // enable plugin
        owlNrowTarget: 'item',    // class for items in carousel div
        owlNrowContainer: 'owlNrow-item', // class for items container
        owlNrowDirection: 'ltr', // utd or ltr : directions
        owlNrowNumberOfRows: 1,
        responsive: {
          0: {
            items: 3 // 3 items on the screen per row
          }
        }
      },
      /* Other settings */
      enable_log: false,
    },
    server_host = window.location.hostname,
    api_url = "http://" + server_host + ":8181/kytos/",
    api_stats = api_url + 'stats/',
    api_status = api_url + 'status/',
    layouts_url = api_url + "web/topology/layouts/",
    topology_url = api_url + "topology",
    log_server_url = "ws://" + server_host + ":8765",
    mustache_dir = '/static/js/templates/';
