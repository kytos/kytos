/////////////////////////////////////////////////////////
/////////////// The Radar Chart Function ////////////////
/////////////// Written by Nadieh Bremer ////////////////
////////////////// VisualCinnamon.com ///////////////////
/////////// Inspired by the code of alangrafu ///////////
/////////////////////////////////////////////////////////

function getMaxSpeed(ifaces) {
  var maxValue = 0;
  for (var i in ifaces) {
    if (ifaces[i].speed > maxValue) {
      maxValue = ifaces[i].speed;
    }
  }
  return maxValue;
}

function RadarChart(id, data) {

  // calculating reference sizes (width/height)

  var maxValue = 100,  //Utilization percentage
      //Speed multiplier to get radius of the external circles, proportional to
      //their area.
      speedScale = 7.0 / Math.pow(getMaxSpeed(data[0]),0.5),
      _w = $("#" + id).parent().width(),
      // 252 is the min height of a switch_card, by design. 198 because of some margins
      _h = Math.max($("#" + id).parent().height(), 198),
      ref_size = _w && _w > 0 ? Math.min(_w, _h) : _h,
      //var size = $("#" + id).parent().width() * 0.8;
      size = ref_size * 0.75,
      margin = ref_size * 0.125,
      cfg = {
       w: size,        //Width of the circle
       h: size,
       margin: {top: margin, right: margin, bottom: margin, left: margin}, //The margins of the SVG
       levels: 4,        //How many levels or inner circles should there be drawn
       maxValue: maxValue,       //What is the value that the biggest circle will represent
       labelFactor: 1.15,   //How much farther than the radius of the outer circle should the labels be placed
       wrapWidth: 60,     //The number of pixels after which a label needs to be given a new line
       opacityArea: 0.30,   //The opacity of the area of the blob
       dotRadius: 3,       //The size of the colored circles of each blog
       opacityCircles: 0.1,   //The opacity of the circles of each blob
       strokeWidth: 2,     //The width of the stroke around each blob
       roundStrokes: true,  //If true the area and stroke will follow a round path (cardinal-closed)
       color: d3.scaleOrdinal().range(["#549e9f","#b54872"])
      };

  var interfaceColor = d3.scaleLinear()
                         .domain([0, 12.5, 25, 37.5, 50, 62.5, 75, 87.5, 100])
                         .range(["#2d2d35", "#41414d","#616173","#77778c","#8d8da6","#a2a2bf","#adadcc","#c3c3e6","#d9d9ff"]);
                         //.range(["#2c7bb6", "#00a6ca","#00ccbc","#90eb9d","#ffff8c","#f9d057","#f29e2e","#e76818","#d7191c"]);

  var allAxis = (data[0].map(function(i, j) { return i } )),  //Names of each axis
    total = allAxis.length,          //The number of different axes
    radius = Math.min(size/2,size/2),   //Radius of the outermost circle
    angleSlice = Math.PI * 2 / total;    //The width in radians of each "slice"

  // Scale for the radius
  var rScale = d3.scaleLinear()
    .range([0, radius])
    .domain([0, maxValue]);

  // Initiate the radar chart SVG
  var svg = d3.select('#'+id).append("svg")
      .attr("width",  cfg.w + cfg.margin.left + cfg.margin.right)
      .attr("height", cfg.h + cfg.margin.top + cfg.margin.bottom)
      .attr("class", "radar-"+id);

  // Append a g element
  var g = svg.append("g")
      .attr("transform", "translate(" + (size + margin * 2) /2 + "," + (size + margin * 2)/2 + ")");

  /////////////////////////////////////////////////////////
  /////////////// Draw the Circular grid //////////////////
  /////////////////////////////////////////////////////////

  //Wrapper for the grid & axes
  var axisGrid = g.append("g").attr("class", "axisWrapper");

  //Draw the background circles
  axisGrid.selectAll(".levels")
     .data(d3.range(1,(cfg.levels+1)).reverse())
     .enter()
    .append("circle")
    .attr("r", function(d, i){return radius/cfg.levels*d;})
    .attr("class", "grid-lines");

  // Text indicating at what % each level is
  axisGrid.selectAll(".axisLabel")
     .data(d3.range(1, (cfg.levels + 1)).reverse())
     .enter().append("text")
     .attr("class", "axisLabel")
     .attr("x", 0)
     .attr("y", function(d){return - d * radius/cfg.levels;})
     .attr("dy", "1.5em")
     .text(function(d,i) { return (100 / cfg.levels) * d});

  // Create the straight lines radiating outward from the center
  var axis = axisGrid.selectAll(".axis")
    .data(allAxis)
    .enter()
    .append("g")
    .attr("class", "axis");

  // Append the lines
  axis.append("line")
    .attr("x1", function(d, i){ return rScale(d.value) * Math.cos(angleSlice*i - Math.PI/2); })
    .attr("y1", function(d, i){ return rScale(d.value) * Math.sin(angleSlice*i - Math.PI/2); })
    .attr("x2", function(d, i){ return rScale(maxValue) * Math.cos(angleSlice*i - Math.PI/2); })
    .attr("y2", function(d, i){ return rScale(maxValue) * Math.sin(angleSlice*i - Math.PI/2); })
    .attr("class", "line");


  // Append the interfaces circles at each axis
  axis.append("circle")
    .attr("class", "interface")
    .attr("r", function(d,i) { return Math.pow(d.speed,0.5) * speedScale })
    .attr("cx", function(d, i){ return rScale(maxValue * cfg.labelFactor) * Math.cos(angleSlice*i - Math.PI/2); })
    .attr("cy", function(d, i){ return rScale(maxValue * cfg.labelFactor) * Math.sin(angleSlice*i - Math.PI/2); })
    .style("fill", function(d,i) { return interfaceColor(d.value); });

  // The radial line function
  var radarLine = d3.radialLine()
    .curve(d3.curveCardinalClosed)
    .radius(function(d) { return rScale(d.value); })
    .angle(function(d,i) {  return i*angleSlice; })

  // Create a wrapper for the blobs
  var blobWrapper = g.selectAll(".radarWrapper")
    .data(data)
    .enter().append("g")
    .attr("class", "radarWrapper");

  // Append the backgrounds
  blobWrapper
    .append("path")
    .attr("class", "radarArea")
    .attr("d", function(d,i) { return radarLine(d); })
    .style("fill", function(d,i) { return cfg.color(i); })
    .style("fill-opacity", cfg.opacityArea);
/*
    .on('mouseover', function (d,i){
      //Dim all blobs
      d3.selectAll(".radarArea")
        .transition().duration(200)
        .style("fill-opacity", 0.1);
      //Bring back the hovered over blob
      d3.select(this)
        .transition().duration(200)
        .style("fill-opacity", 0.7);
    })
    .on('mouseout', function(){
      //Bring back all blobs
      d3.selectAll(".radarArea")
        .transition().duration(200)
        .style("fill-opacity", cfg.opacityArea);
    });
*/

  // Create the outlines
  blobWrapper.append("path")
    .attr("class", "radarStroke")
    .attr("d", function(d,i) { return radarLine(d); })
    .style("stroke-width", cfg.strokeWidth + "px")
    .style("stroke", function(d,i) { return cfg.color(i); })
    .style("fill", "none");
    // .style("filter" , "url(#glow)");

  // Append the circles
  blobWrapper.selectAll(".radarCircle")
    .data(function(d,i) { return d; })
    .enter().append("circle")
    .attr("class", "radarCircle")
    .attr("r", cfg.dotRadius)
    .attr("cx", function(d,i){ return rScale(d.value) * Math.cos(angleSlice*i - Math.PI/2); })
    .attr("cy", function(d,i){ return rScale(d.value) * Math.sin(angleSlice*i - Math.PI/2); })
    .style("fill", function(d,i,j) { return cfg.color(j); })
    .style("fill-opacity", 0.8);

  /////////////////////////////////////////////////////////
  //////// Append invisible circles for tooltip ///////////
  /////////////////////////////////////////////////////////

/*
  //Wrapper for the invisible circles on top
  var blobCircleWrapper = g.selectAll(".radarCircleWrapper")
    .data(data)
    .enter().append("g")
    .attr("class", "radarCircleWrapper");

  //Append a set of invisible circles on top for the mouseover pop-up
  blobCircleWrapper.selectAll(".radarInvisibleCircle")
    .data(function(d,i) { return d; })
    .enter().append("circle")
    .attr("class", "radarInvisibleCircle")
    .attr("r", cfg.dotRadius*4)
    .attr("cx", function(d,i){ return rScale(d.value) * Math.cos(angleSlice*i - Math.PI/2); })
    .attr("cy", function(d,i){ return rScale(d.value) * Math.sin(angleSlice*i - Math.PI/2); })
    .style("fill", "none")
    .style("pointer-events", "all")
    .on("mouseover", function(d,i) {
      newX =  parseFloat(d3.select(this).attr('cx')) - 10;
      newY =  parseFloat(d3.select(this).attr('cy')) - 10;

      tooltip
        .attr('x', newX)
        .attr('y', newY)
        .text(d.value)
        .transition().duration(200)
        .style('opacity', 1);
    })
    .on("mouseout", function(){
      tooltip.transition().duration(200)
        .style("opacity", 0);
    });
  //Set up the small tooltip for when you hover over a circle
  var tooltip = g.append("text")
    .attr("class", "tooltip")
    .style("opacity", 0);

*/

}//RadarChart
