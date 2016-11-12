var default_settings = {
      'show_unused_interfaces': true,
      'show_disconnected_hosts': true,
      'show_topology': true,
      'show_map': true,
      'map_opacity': 0.4,
      'enable_log': true,
      'map_center': [-97.8445676, 35.3437248],
      'map_zoom': 4
    },
    server_host = window.location.hostname,
    api_url = "http://" + server_host + ":8181/kytos/",
    api_status = api_url + 'status/',
    layouts_url = api_url + "web/topology/layouts/",
    topology_url = api_url + "topology",
    log_server_url = "ws://" + server_host + ":8765";
