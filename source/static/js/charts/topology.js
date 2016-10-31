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
var strength = {'link': 0.0001,
                'interface': 2,
                'host': 0.05};

var distance = {'link': 6 * size['switch'],
                'interface': size['switch'],
                'host': 5 * size['interface']};

var svg = d3.select("#topology-chart svg"),
    width = +svg.attr("width"),
    height = +svg.attr("height");

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
    .force("charge", d3.forceManyBody())
    .force("center", d3.forceCenter(width / 2, height / 2));

d3.json("/static/data/topology.json", function(error, graph) {
  if (error) throw error;

  var link = svg.append("g")
      .attr("class", "links")
    .selectAll("line")
    .data(graph.links)
    .enter().append("line")
      .attr("stroke-width", function(d) { return Math.sqrt(d.value); });

  var node = svg.append("g")
      .attr("class", "nodes")
    .selectAll("circle")
    .data(graph.nodes)
    .enter().append("circle")
      .attr("r", function(d) { return get_node_size(d.type); })
      .attr("fill", function(d) { return color(d.group); })
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
  //d.fx = null;
  //d.fy = null;
}

function releaseNode(d) {
    d.fx = null;
    d.fy = null;
}

