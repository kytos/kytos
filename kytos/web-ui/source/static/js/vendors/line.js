var margin2 = {top: 20, right: 0, bottom: 30, left: 120},
    width2 = $(".lineChart").parent().width() - margin2.left - margin2.right,
    height2 = 200 - margin2.top - margin2.bottom;

var formatDate = d3.timeParse("%Y-%m-%d %H:%M:%S");

var x = d3.scaleTime()
    .range([0, width2]);

var y = d3.scaleLinear()
    .range([height2, 0]);

var xAxis = d3.axisBottom()
    .scale(x)
    .ticks(8);

var yAxis = d3.axisLeft()
    .scale(y)
    .ticks(4);

var line = d3.line()
    .curve(d3.curveBasis)
    .x(function(d) { return x(d.date); })
    .y(function(d) { return y(d.value); });

var svg = d3.select(".lineChart").append("svg")
    .attr("width", width2 + margin2.left + margin2.right)
    .attr("height", height2 + margin2.top + margin2.bottom)
  .append("g")
    .attr("transform", "translate(" + margin2.left + "," + margin2.top + ")");

d3.json("static/data/line.json", function(error, data) {
  if (error) throw error;

    data.forEach(function(d) {
        d.date = formatDate(d.date);
        d.value = +d.value;
    });

  x.domain(d3.extent(data, function(d) { return d.date; }));
  y.domain(d3.extent(data, function(d) { return d.value; }));


  svg.append("rect")
      .attr("x", 0)
      .attr("y", height2)
      .attr("width", width2)
      .attr("height", 30)
      .attr("class", "xaxisframe");

  svg.append("g")         // Add the X Axis
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height2 + ")")
      .call(xAxis);

/*
  svg.append("g")         // Add the Y Axis
      .attr("class", "y axis")
      .call(yAxis);
*/

  svg.append("path")      // Add the valueline path.
			.datum(data)
      .attr("class", "line")
      .attr("d", line);
});
