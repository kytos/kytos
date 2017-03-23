Number.prototype.zeroPad = function() {
   return ('0'+this).slice(-2);
};

var Chart = function(id, attributes, data, svg, options) {
  this.id = id;
  this.name = attributes['name'];
  this.port_number = attributes['port_number'];
  this.speed = attributes['speed'];
  this.data = data;
  this.svg = svg;

  this.formatDate = d3.timeParse("%Y-%m-%d %H:%M:%S");

  this.width = options.width;
  this.height = options.height;
  this.margin = options.margin;

  this.data.forEach(function(d) {
    d.date = this.formatDate(d.date);
    d.value = +d.value;
  });

  this.xScale = d3.scaleTime()
                        .range([0, this.width])
                        .domain(d3.extent(this.data, function(d) { return d.date; } ));
  
  this.yScale = d3.scaleLinear()
                        .range([this.height,0])
                        .domain(d3.extent(this.data, function(d) { return d.value;} ));

  this.xAxisTop = d3.axisBottom().scale(this.xScale).ticks(8);

  var xS = this.xScale;
  var yS = this.yScale;
  
  this.area = d3.area()
                    .curve(d3.curveBasis)
                    .x(function(d) { return xS(d.date); })
                    .y0(this.height)
                    .y1(function(d) { return yS(d.value); });

  this.svg.append("defs").append("clipPath")
                          .attr("id", "clip-" + this.id)
                          .append("rect")
                            .attr("width", this.width)
                            .attr("height", this.height);
  /*
    Assign it a class so we can assign a fill color
    And position it on the page
  */
  var trans1 = this.margin.left;
  var trans2 = (this.margin.top + (this.height * this.id) + (10 * this.id));

  this.chart = svg.append("g")
                  .attr('class',this.name.toLowerCase())
                  .attr("transform", "translate(" + trans1 + "," + trans2 + ")");

  /* We've created everything, let's actually add it to the page */
  this.chart.append("path")
            .data([this.data])
            .attr("class", "chart")
            .attr("clip-path", "url(#clip-" + this.id + ")")
            .attr("d", this.area);
                  
/*
  if (this.id == 0) {
    this.chart.append("g")
          .attr("class", "x axis top")
          .attr("transform", "translate(0,-30)")
          .call(this.xAxisTop);
  }
*/
  this.chart.append("text")
            .attr("class","interface-number")
            .attr("transform", "translate(-120,22)")
            .text(this.port_number.zeroPad());
 
  this.chart.append("text")
            .attr("class","interface-name")
            .attr("transform", "translate(-80, 10)")
            .text(this.name);

  this.chart.append("text")
            .attr("class","interface-speed")
            .attr("transform", "translate(-80, 24)")
            .text(this.speed);

}
