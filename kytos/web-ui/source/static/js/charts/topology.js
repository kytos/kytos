// Nodes vars
var charge = {'switch': 400,
              'interface': -20,
              'host': 20};

var size = {'switch': 20,
            'interface': 5,
            'host': 10};

var nodes_fill = {'switch': "#554077", // "rgba(255,255,255,0)",
                  'interface': "rgba(255,255,255,0.5)",
                  'host': "rgba(255,0,0,1)"};

var nodes_stroke = {'switch': "#554077", //"rgba(255,255,255,0.5)",
                    'interface': "rgba(255,255,255,0.5)",
                    'host': "rgba(255,255,255.0.5)"};

// Links vars
var strength = {'link': 0.001,
                'interface': 1,
                'host': 0.1};

var distance = {'link': 20 * size['switch'],
                'interface': size['switch'] + 10,
                'host': 1 * size['interface']};

var strokes = {'interface': 0,
               'link': 1,
               'host': 1};

function get_node_size(type) {
  return size[type];
}

function dragstarted(d) {
  if (!d3.event.active) simulation.alphaTarget(0.3).restart();
  if ( d.type == 'switch' ) {
    d.old_fx = d.x;
    d.old_fy = d.y;
    $.each(get_switch_interfaces(d), function(index, interface){
      interface.fx = interface.x;
      interface.fy = interface.y;
    });
  }
  d.fx = d.x;
  d.fy = d.y;
}

function dragged(d) {
  if ( d.type == 'switch' ) {
    d.old_fx = d.fx;
    d.old_fy = d.fy;
    d.fx = d3.event.x;
    d.fy = d3.event.y;
    delta_x = d.fx - d.old_fx;
    delta_y = d.fy - d.old_fy;
    $.each(get_switch_interfaces(d), function(index, interface){
      if (interface.fx == undefined) {
        interface.fx = interface.x;
        interface.fy = interface.y;
      }
      interface.fx += delta_x;
      interface.fy += delta_y;
    });
  } else if ( d.type == 'interface' ) {
    owner = get_interface_owner(d);
    if (owner.fx == undefined) {
      cx = owner.x;
      cy = owner.y;
    } else {
      cx = owner.fx;
      cy = owner.fy;
    }
    new_positions = radius_positioning(cx, cy, d3.event.x, d3.event.y);
    d.fx = new_positions[0]
    d.fy = new_positions[1]
  } else {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
  }
}

function dragended(d) {
  if (!d3.event.active) simulation.alphaTarget(0);
  // uncomment the lines below to disable de fixed drag behavior
  //if ( d.type == 'interface' ) {
      //release_node(d);
  //}
}

function release_node(d) {
  d.fx = null;
  d.fy = null;
  if (d.type == 'switch') {
    $.each(get_switch_interfaces(d), function(index, interface){
      interface.fx = null;
      interface.fy = null;
    });
  }
}

function get_interface_owner(d){
  /* Get the switch in which the 'd' interface is connected */
  if (d.type != 'interface') return null;
  searched_switch = null;
  $.each(simulation.nodes(), function(index, node) {
    if (node.id == d.switch) {
      searched_switch = node;
      return false;  // this just breaks the each loop.
    }
  });
  return searched_switch;
}

function get_switch_interfaces(d){
  /* Get all interfaces associated to the 'd' host */
  if (d.type != 'switch') return null;
  interfaces = []
  $.each(simulation.nodes(), function(index, node) {
    if (node.type == 'interface' && node.switch == d.id)
      interfaces.push(node);
  });
  return interfaces;
}

function get_nodes_by_type(type) {
  selected_nodes = [];
  $.each(simulation.nodes(), function(index, node){
      if (node.type == type) { selected_nodes.push(node); };
  });
  return selected_nodes;
}

function get_switch_by_dpid(dpid) {
  var switch_node = undefined;
  $.each(simulation.nodes(), function(index, node){
    if (node.type == 'switch' && node.dpid == dpid) { switch_node = node; }
  })
  return switch_node;
}

function get_interfaces() {
  return get_nodes_by_type('interface');
}

function get_hosts() {
  return get_nodes_by_type('host');
}

function get_switches() {
  return get_nodes_by_type('switch');
}

function get_node_links(node) {
  links = [];
  $.each(simulation.force('link').links(), function(index, link) {
    if (link.target == node || link.source == node )
      links.push(link);
  });
  return links;
}

function radius_positioning(cx, cy, x, y) {
  delta_x = x - cx;
  delta_y = y - cy;
  rad = Math.atan2(delta_y, delta_x);
  new_x = cx + Math.cos(rad) * distance['interface'];
  new_y = cy + Math.sin(rad) * distance['interface'];

  return [new_x, new_y];
}

function toggle_unused_interfaces(){
  show = $('#show_unused_interfaces')[0].checked;
  $.each(get_interfaces(), function(index, interface){
    unused = true;
    $.each(get_node_links(interface), function(index, link){
      if (link.type == 'link') unused = false;
    });
    if (unused) {
      d3.select("#node-interface-" + fix_name(interface.id))
        .classed('invisible', !show);
    }
  })
}

function toggle_disconnected_hosts(){
  show = $('#show_disconnected_hosts')[0].checked;
  $.each(get_hosts(), function(index, host){
    links = get_node_links(host);
    if (links.length == 0) {
      d3.select("#node-host-" + fix_name(host.id))
        .classed('invisible', !show);
    }
  })
}

function node_highlight(node) {
  d3.select("#node-" + node.type + "-" + fix_name(node.id))
    .classed('downlight', false);
}

function node_downlight(node) {
  d3.select("#node-" + node.type + "-" + fix_name(node.id))
    .selection.classed('downlight', true);
}

function highlight_all_switches() {
  d3.selectAll("[id^='node-switch-']").classed('downlight', false);
}

function highlight_all_interfaces() {
  d3.selectAll("[id^='node-interface-']").classed('downlight', false);
}

function highlight_all_nodes() {
  d3.selectAll("[id^='node-']").classed('downlight', false);
  dv = '<div id="orientation_text">Click on an element in the topology chart to show its context here.</div>'
  $('#context_target').html(dv);
  resize_terminal_available_area();
}

function downlight_all_switches() {
  d3.selectAll("[id^='node-switch-']").classed('downlight', true);
}

function downlight_all_interfaces() {
  d3.selectAll("[id^='node-interface-']").classed('downlight', true);
}

function highlight_switch(obj) {
  downlight_all_switches();
  downlight_all_interfaces();
  node_highlight(obj);
  $.each(get_switch_interfaces(obj), function(idx, interface){
    node_highlight(interface)
  });
}

function toggle_labels(node_type, label_type) {
  $('.' + node_type + '_label_group').fadeOut();
  $('.' + node_type + '_label_group.' + label_type + '_label').fadeIn()
}

function zoomed() {
  container.attr("transform", d3.event.transform);
}

function resetted() {
  container.transition()
    .duration(450)
    .call(zoom.transform, d3.zoomIdentity);
}

function show_context(d) {
  if (d.type == 'switch') {
    data = {'name': d.name,
            'id': d.id,
            'dpid': d.dpid,
            'connection': d.connection,
            'ofp_version': d.ofp_version,
            'hardware': d.hardware,
            'software': d.software,
            'manufacturer': d.manufacturer,
            'serial': d.serial};
    add_stats(data, show_switch_context);
    highlight_switch(d);
  }
}

function fix_name(name) {
  return name.toString().replace(/:/g, '__');
}

function unfix_name(name) {
  return name.toString().replace(/\_\_/g, ':');
}

function get_current_layout() {
  /*
    {
      nodes: {
        <node_name>: {
          type: ,
          x: ,
          y: ,
          fx: ,
          fy: ,
          downlight: ,
          invisible:
        },
        ...
      },
      other_settings: {
       .....
      }
    }
   */
  layout = {'nodes': {}, 'other_settings': {}};
  $.each(simulation.nodes(), function(idx, node) {
    d3node = d3.select('#node-' + node.type + '-' + fix_name(node.id));
    node_data = {
      'name': node.name,
      'id': node.id,
      'type': node.type,
      'x': node.x,
      'y': node.y,
      'fx': node.fx,
      'fy': node.fy,
      'downlight': d3node.classed('downlight'),
    };
    layout.nodes[node.id] = node_data;
  });
  layout.other_settings['show_unused_interfaces'] = $('#show_unused_interfaces')[0].checked;
  layout.other_settings['show_disconnected_hosts'] = $('#show_disconnected_hosts')[0].checked;
  layout.other_settings['show_topology'] = $('#show_topology')[0].checked;
  layout.other_settings['show_map'] = $('#show_map')[0].checked;
  layout.other_settings['map_center'] = background_map.getCenter();
  layout.other_settings['map_zoom'] = background_map.getZoom();
  layout.other_settings['topology_transformation'] = d3.select('#topology-chart svg g').attr('transform');
  return layout;
}

function save_layout() {
  layout_name = $('#layout_name').val();
  if (layout_name == '') {
    alert('Please, choose a name for the layout.');
  } else {
    layout = get_current_layout();
    data = JSON.stringify(layout);
    set_status('Trying to save layout: ' + layout_name);
    $.post({
      url: layouts_url + layout_name,
      data: data,
      contentType: "application/json",
      success: function(data, status, xhr) {
        appendLayoutListItem(layout_name);
        set_status('Layout saved as ' + layout_name);
        $('#saveLayout').modal('hide');
      },
      error: function(xhr, status, error){
        set_status('Error while trying to save layout', true);
        $('#saveLayout').modal('hide');
      },
      dataType: "json"
    });
  }
}

function get_saved_layouts() {
  $.ajax({
    async: false,
    dataType: "json",
    url: layouts_url,
    success: function(data) {
      return JSON.parse(data);
    },
    done : function(){
      scrollBehavior();
    }
  });
}

function load_layouts() {
  $.ajax({
    dataType: "json",
    url: layouts_url,
    success: function(layouts) {
      if (layouts == undefined) {
        alert("There isn't any saved layout to be loaded");
      } else {
        savedLayouts = $('#savedLayouts>ul');
        savedLayouts.empty();
        $.each(layouts, function (idx, item) {
          appendLayoutListItem(item);
        });
      }
    },
    done: function(){
      scrollBehavior();
    }
  });
}

function appendLayoutListItem(item){
  var savedLayouts = $('#savedLayouts>ul'),
      exists = false;

  savedLayouts.find('li').each(function(){
    if ($(this).text() == item) {
      exists = true;
    }
  });
  if (!exists){
    $('<li><a href="#" data-value="'+ item +'" onclick="restore_layout(\''+ item +'\')">'+ item +'</a></li>').appendTo(savedLayouts);
  }
}

function restore_layout(name) {
  if ( name === undefined ) name = $('#savedLayouts>ul>li:first').text();

  set_status('Trying to restore the layout: ' + name);

  $('#savedLayouts>button>span.layout-name').text(name);

  $.getJSON(layouts_url + name, function(layout) {
    $.each(simulation.nodes(), function(idx, node) {
      if (node.id in layout.nodes) {
        restored_node = layout.nodes[node.id];
        node.x = restored_node.x;
        node.y = restored_node.y;
        node.fx = restored_node.fx;
        node.fy = restored_node.fy;
        d3node = d3.select('#node-' + node.type + '-' + fix_name(node.id))
                      .classed('downlight', restored_node.downlight);
      }
    });

    $('#show_unused_interfaces')
        .prop('checked', layout.other_settings.show_unused_interfaces)
        .change();

    $('#show_disconnected_hosts')
        .prop('checked', layout.other_settings.show_disconnected_hosts)
        .change();

    if (layout.other_settings.topology_transformation) {
      d3.select('#topology-chart svg g')
          .attr('transform', layout.other_settings['topology_transformation']);
    }

    if (layout.other_settings.show_topology) {
      $('#show_topology').prop('checked', true).change();
      $('#topology-chart').show();
    } else {
      $('#show_topology').prop('checked', false).change();
      $('#topology-chart').hide();
    }

    if (layout.other_settings.show_map) {
      $('#show_map').prop('checked', true).change();
      $('#background-map').show();
    } else {
      $('#show_map').prop('checked', false).change();
      $('#background-map').hide();
    }
    background_map.flyTo({
      center: layout.other_settings.map_center,
      zoom: layout.other_settings.map_zoom
    })

    simulation.restart();

    window.location.hash = name;

  }).done(function(){set_status('Layout ' + name + ' restored.')});
}

function draw_topology() {

  // helper functions
  function topo_id(d) { return d.id; }
  function topo_strength(d) { return strength[d.type]; }
  function topo_distance(d) { return distance[d.type]; }
  function link_stroke_width(d){ return strokes[d.type]; }
  function gnode_radius(d) { return get_node_size(d.type); }
  function gnode_stroke(d) { return nodes_stroke[d.type]; }
  function gnode_fill(d) { return nodes_fill[d.type]; }
  function gnode_id(d) { return "node-" + d.type + "-" + fix_name(d.id); }

  // basic 'constants' and 'variables'
  var width = $("#topology-chart").parent().width(),
      height = $(window).height() - $('.navbar').height() - 5,
      color = d3.scaleOrdinal(d3.schemeCategory20);

  // main forceSimulation variable
  //  exposing it publicly in a way that some filtering can be done
  window.simulation = d3.forceSimulation()
                        .force("link", d3.forceLink().id(topo_id)
                                                     .strength(topo_strength)
                                                     .distance(topo_distance)
                        )
                        .force("charge", d3.forceManyBody().theta(1))
                        .force("center", d3.forceCenter(width/2, 0.4*height));

  window.zoom = d3.zoom()
                  .scaleExtent([0.2, 3])
                  .on("zoom", zoomed);

  var svg = d3.select("#topology-chart")
              .append("svg")
              .attr("width", width)
              .attr("height", height);

  var zoomer = svg.append("rect")
                  .attr("width", width)
                  .attr("height", height)
                  .classed('topology_zoom', true)
                  .call(zoom)
                  .on('click', highlight_all_nodes);

  window.container = svg.append('g')

  zoomer.call(zoom.transform, d3.zoomIdentity.translate(0,0));

  set_status('Loading topology ... ');
  d3.json(topology_url, function(error, graph) {
    if (error) {
      set_status(['Error while trying to load  the topology', error], true);
      throw error;
    };

    var link = container.append("g")
        .attr("class", "links")
      .selectAll("line")
      .data(graph.links)
      .enter().append("line")
        .attr("stroke-width", link_stroke_width)

    var gnodes = container.append("g")
        .classed("nodes", true)
      .selectAll("g.node")
      .data(graph.nodes)
      .enter()
        .append('g')
          .classed('gnode', true)
          .attr("id", gnode_id)
          .call(d3.drag()
                  .on("start", dragstarted)
                  .on("drag", dragged)
                  .on("end", dragended))
        .on('click', show_context)
        .on("dblclick", release_node);

    var node = gnodes.append("circle")
        .attr('class', 'node')
        .attr("r", gnode_radius)
        .attr("stroke", gnode_stroke)
        .attr("stroke-width", 2)
        .attr("fill", gnode_fill);

    /*******************
     * SWITCH LABELING *
     *******************/
    // only labeling switches, but not interfaces
    var switch_labeled_items = gnodes.filter(function(d) {return d.type == 'switch';});

    //
    // NAME LABEL
    //
    // creating a group for the NAME label
    var switch_name_label_group = switch_labeled_items
      .append('g')
      .classed('switch_label_group', true)
      .classed('name_label', true);

    // creating a rect to do some backgrounding on the label.
    var switch_name_label_rects = switch_name_label_group
        .append('rect')
          .attr('x', 0)
          .attr('y', 0)
          .attr('rx', 5)
          .attr('ry', 5)
          .style('fill', 'rgba(155,155,255,0.2)');

    // adding the NAME itself as a svg text element
    var switch_name_label_text = switch_name_label_group
        .append('text')
          .text(function(d){ return d.name; });

    // fixing the rect width and height according to the NAME size.
    switch_name_label_rects
      .attr('width', function(d) { return this.parentNode.getBBox().width + 8; })
      .attr('height', function(d) { return this.parentNode.getBBox().height + 8; })

    // fixing the NAME text element positioning to the center of the rect.
    switch_name_label_text
        .attr('x', function(d) { return 4; })
        .attr('y', function(d) { return this.parentNode.getBBox().height / 2; })

    //
    // ADDRESS LABEL
    //
    // creating a group for the ADDRESS label
    var switch_address_label_group = switch_labeled_items
      .append('g')
      .classed('switch_label_group', true)
      .classed('address_label', true);

    // creating a rect to do some backgrounding on the label.
    var switch_address_label_rects = switch_address_label_group
        .append('rect')
          .attr('x', 0)
          .attr('y', 0)
          .attr('rx', 5)
          .attr('ry', 5)
          .style('fill', 'rgba(155,155,255,0.2)');

    // adding the ip itself as a svg text element
    var switch_address_label_text = switch_address_label_group
        .append('text')
          .text(function(d){ return d.connection; });

    // fixing the rect width and height according to the ip size.
    switch_address_label_rects
      .attr('width', function(d) { return this.parentNode.getBBox().width + 8; })
      .attr('height', function(d) { return this.parentNode.getBBox().height + 8; })

    // fixing the IP text element positioning to the center of the rect.
    switch_address_label_text
        .attr('x', function(d) { return 4; })
        .attr('y', function(d) { return this.parentNode.getBBox().height / 2; })

    //
    // DPID LABEL
    //
    // creating a group for the DPID label
    var switch_dpid_label_group = switch_labeled_items
        .append('g')
          .classed('switch_label_group', true)
          .classed('dpid_label', true);

    // creating a rect to do some backgrounding on the label.
    var switch_dpid_label_rects = switch_dpid_label_group
        .append('rect')
          .attr('x', 0)
          .attr('y', 0)
          .attr('rx', 5)
          .attr('ry', 5)
          .style('fill', 'rgba(155,155,255,0.2)');

    // adding the DPID itself as a svg text element
    var switch_dpid_label_text = switch_dpid_label_group
        .append('text')
          .text(function(d){ return d.dpid; });

    // fixing the rect width and height according to the NAME size.
    switch_dpid_label_rects
      .attr('width', function(d) { return this.parentNode.getBBox().width + 8; })
      .attr('height', function(d) { return this.parentNode.getBBox().height + 8; })

    // fixing the NAME text element positioning to the center of the rect.
    switch_dpid_label_text
      .attr('x', function(d) { return 4; })
      .attr('y', function(d) { return this.parentNode.getBBox().height / 2; })

    /**************************
     * END OF SWITCH LABELING *
     **************************/

    /******************
     * HOSTS LABELING *
     ******************/
    // only labeling hostes, but not interfaces
    var host_labeled_items = gnodes.filter(function(d) {return d.type == 'host';});

    //
    // NAME LABEL
    //
    // creating a group for the NAME label
    var host_name_label_group = host_labeled_items
      .append('g')
      .classed('host_label_group', true)
      .classed('name_label', true);

    // creating a rect to do some backgrounding on the label.
    var host_name_label_rects = host_name_label_group
        .append('rect')
          .attr('x', 0)
          .attr('y', 0)
          .attr('rx', 5)
          .attr('ry', 5)
          .style('fill', 'rgba(155,155,255,0.2)');

    // adding the NAME itself as a svg text element
    var host_name_label_text = host_name_label_group
        .append('text')
          .text(function(d){ return d.name; });

    // fixing the rect width and height according to the NAME size.
    host_name_label_rects
      .attr('width', function(d) { return this.parentNode.getBBox().width + 8; })
      .attr('height', function(d) { return this.parentNode.getBBox().height + 8; })

    // fixing the NAME text element positioning to the center of the rect.
    host_name_label_text
        .attr('x', function(d) { return 4; })
        .attr('y', function(d) { return this.parentNode.getBBox().height / 2; })

    //
    // MAC LABEL
    //
    // creating a group for the ADDRESS label
    var host_mac_label_group = host_labeled_items
      .append('g')
      .classed('host_label_group', true)
      .classed('mac_label', true);

    // creating a rect to do some backgrounding on the label.
    var host_mac_label_rects = host_mac_label_group
        .append('rect')
          .attr('x', 0)
          .attr('y', 0)
          .attr('rx', 5)
          .attr('ry', 5)
          .style('fill', 'rgba(155,155,255,0.2)');

    // adding the ip itself as a svg text element
    var host_mac_label_text = host_mac_label_group
        .append('text')
          .text(function(d){ return d.mac; });

    // fixing the rect width and height according to the ip size.
    host_mac_label_rects
      .attr('width', function(d) { return this.parentNode.getBBox().width + 8; })
      .attr('height', function(d) { return this.parentNode.getBBox().height + 8; })

    // fixing the IP text element positioning to the center of the rect.
    host_mac_label_text
        .attr('x', function(d) { return 4; })
        .attr('y', function(d) { return this.parentNode.getBBox().height / 2; })

    //
    // ADDRESS LABEL
    //
    // creating a group for the address label
    var host_address_label_group = host_labeled_items
        .append('g')
          .classed('host_label_group', true)
          .classed('address_label', true);

    // creating a rect to do some backgrounding on the label.
    var host_address_label_rects = host_address_label_group
        .append('rect')
          .attr('x', 0)
          .attr('y', 0)
          .attr('rx', 5)
          .attr('ry', 5)
          .style('fill', 'rgba(155,155,255,0.2)');

    // adding the address itself as a svg text element
    var host_address_label_text = host_address_label_group
        .append('text')
          .text(function(d){ return d.address; });

    // fixing the rect width and height according to the NAME size.
    host_address_label_rects
      .attr('width', function(d) { return this.parentNode.getBBox().width + 8; })
      .attr('height', function(d) { return this.parentNode.getBBox().height + 8; })

    // fixing the NAME text element positioning to the center of the rect.
    host_address_label_text
      .attr('x', function(d) { return 4; })
      .attr('y', function(d) { return this.parentNode.getBBox().height / 2; })

    /*************************
     * END OF HOSTS LABELING *
     *************************/

    //
    simulation
        .nodes(graph.nodes)
        .on("tick", ticked);

    simulation.force("link")
        .links(graph.links);

    function ticked() {
      link
          .attr("x1", function(d) { return d.source.x; })
          .attr("y1", function(d) { return d.source.y; })
          .attr("x2", function(d) { return d.target.x; })
          .attr("y2", function(d) { return d.target.y; });

      gnodes.attr("transform", function(d) {
        if ( d.type == 'interface' ) {
          owner = get_interface_owner(d);
          if (owner.fx == undefined) {
            cx = owner.x;
            cy = owner.y;
          } else {
            cx = owner.fx;
            cy = owner.fy;
          }
          new_positions = radius_positioning(cx, cy, d.x, d.y);
          dx = new_positions[0]
          dy = new_positions[1]
          return "translate(" + [dx, dy] + ")";
        } else {
          return "translate(" + [d.x, d.y] + ")";
        }
      });
      gnodes.selectAll('[class$="_label_group"]')
        .attr('transform', function(d){
          return "translate(" + [gnode_radius(d) - 6, gnode_radius(d) - 6] + ")";
        })
    }

    set_status('Topology built. Have fun!');

    if (window.location.hash){
      if (window.location.hash.indexOf('#') == 0) {
        restore_layout(window.location.hash.split('#')[1]);
      } else {
        restore_layout(window.location.hash);
      }
    } else {
      // Load default settings defined at kytos-settings.js
      toggle_disconnected_hosts(default_settings.show_disconnected_hosts);
      toggle_unused_interfaces(default_settings.show_unused_interfaces);
    }

    toggle_labels('switch', 'name');
    toggle_labels('host', 'mac');

    populate_switches_carousel();

    });


}
