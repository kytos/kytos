var default_settings = {
      show_unused_interfaces: true,
      show_disconnected_hosts: true,
      show_topology: true,
      topology_transformation: 'translate(0,0) scale(1)',
      show_map: true,
      map_opacity: 0.4,
      enable_log: true,
      map_center: [-97.8445676, 35.3437248],
      map_zoom: 4,
      switches_carousel_maximized: 4,
      switches_carousel_normal: 1,
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
                items: 1
            },
            1000: {
                items: 2
            }
        }
      }
    },
    server_host = window.location.hostname,
    api_url = "http://" + server_host + ":8181/kytos/",
    api_status = api_url + 'status/',
    layouts_url = api_url + "web/topology/layouts/",
    topology_url = api_url + "topology",
    log_server_url = "ws://" + server_host + ":8765";
