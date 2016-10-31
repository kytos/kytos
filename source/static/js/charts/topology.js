function get_node_size(type) {
  return size[type];
}

var charge = {'switch': 400,
              'host': 20,
              'interface': -20};

var size = {'switch': 20,
            'host': 10,
            'interface': 5};

// Links vars
var strength = {'link': 0.001,
                'interface': 2,
                'host': 0.05};

var distance = {'link': 20 * size['switch'],
                'interface': size['switch'] + 10,
                'host': 5 * size['interface']};

var strokes = {'interface': 0,
               'link': 1,
               'host': 1};

var nodes_fill = {'switch': "rgba(255,255,255,0)",
                  'interface': "rgba(255,255,255,0.5)",
                  'host': "rgba(255,0,0,1)"
                 };

var nodes_stroke = {'switch': "rgba(255,255,255,0.5)",
                    'interface': "rgba(255,255,255,0.5)",
                    'host': "rgba(255,255,255.0.5)"
                 };


var width = $("#topology-chart").parent().width();
var height = 600;

var svg = d3.select("#topology-chart")
             .append("svg")
             .attr("width", width)
             .attr("height", height);

// Adds Pan and Zoom
// svg.call(d3.zoom().on("zoom", function () {
//             svg.attr("transform", d3.event.transform)
//     }))

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

  var link = svg.append("g")
      .attr("class", "links")
    .selectAll("line")
    .data(graph.links)
    .enter().append("line")
      .attr("stroke-width", function(d) { return strokes[d.type]; })

  var node = svg.append("g")
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
          .on("dblclick", releaseNode);

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

function dragstarted(d) {
  if (!d3.event.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x;
  d.fy = d.y;
}

function dragged(d) {
  d.fx = d3.event.x;
  d.fy = d3.event.y;
}

function dragended(d) {
  if (!d3.event.active) simulation.alphaTarget(0);
  // uncomment the lines bellow to disable de fixed drag behavior
  if ( d.type == 'interface' ) {
      releaseNode(d);
  }
}

function releaseNode(d) {
  d.fx = null;
  d.fy = null;
}

function getInterfaceHost(d){
  /* Get the host in which the 'd' interface is connected */
  return null;
}

function getHostInterfaces(d){
  /* Get all interfaces associated to the 'd' host */
  return null;
}
