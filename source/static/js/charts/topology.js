// Nodes vars
var charge = {'switch': 400,
              'interface': -20,
              'host': 20};

var size = {'switch': 20,
            'interface': 5,
            'host': 10};

var nodes_fill = {'switch': "rgba(255,255,255,0)",
                  'interface': "rgba(255,255,255,0.5)",
                  'host': "rgba(255,0,0,1)"};

var nodes_stroke = {'switch': "rgba(255,255,255,0.5)",
                    'interface': "rgba(255,255,255,0.5)",
                    'host': "rgba(255,255,255.0.5)"};

// Links vars
var strength = {'link': 0.001,
                'interface': 2,
                'host': 0.05};

var distance = {'link': 6 * size['switch'],
                'interface': size['switch'] + 10,
                'host': 5 * size['interface']};

var strokes = {'interface': 0,
               'link': 1,
               'host': 1};

var width = $("#topology-chart").parent().width();
var height = 600;

var zoom = d3.zoom()
            .scaleExtent([0.2, 3])
            //.translateExtent([[-100, -100], [width + 90, height + 100]])
            .on("zoom", zoomed);

var svg = d3.select("#topology-chart")
             .append("svg")
             .attr("width", width)
             .attr("height", height);

var zoomer = svg.append("rect")
                .attr("width", width)
                .attr("height", height)
                .style("fill", "none")
                .style("pointer-events", "all")
                .call(zoom);

var container = svg.append('g')

zoomer.call(zoom.transform, d3.zoomIdentity.translate(150,0));

var color = d3.scaleOrdinal(d3.schemeCategory20);

var simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(function(d) { return d.name; })
                                 .strength(function(d) { return strength[d.type]; })
                                 .distance(function(d) { return distance[d.type]; })
          )
    .force("charge", d3.forceManyBody().strength(function(d) {return 10^-16;}))
    .force("center", d3.forceCenter(width / 2, height / 2));

d3.json("/static/data/topology.json", function(error, graph) {
  if (error) throw error;

  var link = container.append("g")
      .attr("class", "links")
    .selectAll("line")
    .data(graph.links)
    .enter().append("line")
      .attr("stroke-width", function(d) { return strokes[d.type]; })

  var node = container.append("g")
      .attr("class", "nodes")
    .selectAll("circle")
    .data(graph.nodes)
    .enter().append("circle")
      .attr("r", function(d) { return get_node_size(d.type); })
      .attr("stroke", function(d) { return nodes_stroke[d.type]; })
      .attr("stroke-width", 2)
      .attr("fill", function(d) { console.log(d.type); return nodes_fill[d.type]; })
      .call(d3.drag()
          .on("start", dragstarted)
          .on("drag", dragged)
          .on("end", dragended))
          .on("dblclick", release_node);

  node.append("title")
      .text(function(d) { return d.name; });

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

    node
        .attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; });
  }
});

function get_node_size(type) {
  return size[type];
}

function dragstarted(d) {
  if (!d3.event.active) simulation.alphaTarget(0.3).restart();
  if ( d.type == 'switch' ) {
    d.old_fx = d.x;
    d.old_fy = d.y;
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
  // uncomment the lines bellow to disable de fixed drag behavior
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
  searched_switch = null;
  $.each(simulation.force('link').links(), function(index, link) {
    if (link.type == 'interface' && link.target.name == d.name) {
      searched_switch = link.source;
    }
  });
  return searched_switch;
}

function get_switch_interfaces(d){
  /* Get all interfaces associated to the 'd' host */
  interfaces = []
  $.each(simulation.force('link').links(), function(index, link) {
    if (link.type == 'interface' && link.source.name == d.name) {
      interfaces.push(link.target);
    }
  });
  return interfaces;
}

function radius_positioning(cx, cy, x, y) {
  delta_x = x - cx;
  delta_y = y - cy;
  rad = Math.atan2(delta_y, delta_x);
  new_x = cx + Math.cos(rad) * distance['interface'];
  new_y = cy + Math.sin(rad) * distance['interface'];

  return [new_x, new_y];
}

function zoomed() {
  container.attr("transform", d3.event.transform);
}

function resetted() {
  container.transition()
    .duration(450)
    .call(zoom.transform, d3.zoomIdentity);
}
