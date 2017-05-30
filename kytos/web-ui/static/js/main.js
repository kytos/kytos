function update_tabs_sizes(){
    width = $('.terminal-body').width();
    $('#tab_terminal').width(width);
    $('#tab_switches').width(width);
    $('#tab_context').width(width);
    $('#tab_logs').width(width);
    $('#tab_notifications').width(width);
    $('#tab_settings').width(width);
}

;(function() {

  $(".terminal").kterminal();

  $("[data-type='checkbox'], [type='radio']").bootstrapSwitch();

  $("a,div").focus(function(){
    $(this).blur();
  })

  // Change the selector if needed
  var $table = $('table.scroll'),
      $bodyCells = $table.find('tbody tr:first').children(),
      colWidth;

  update_tabs_sizes();

  function resize_topology_svg() {
    $("#topology-chart").width($('#chart').width());
    $("#topology-chart svg").attr("width", $('#chart').width());
  }

  function resize_chart_container() {
    $("#chart").height($(window).height() - $('.navbar').height());
    $("#background-map").height($(window).height() - $('.navbar').height());
    resize_topology_svg();
  }

  $(window).on('resize', function() {
    update_tabs_sizes();
    // Adjust the width of thead cells when window resizes
    // Get the tbody columns width array
    colWidth = $bodyCells.map(function() {
        return $(this).width();
    }).get();

    // Set the width of thead columns
    $table.find('thead tr').children().each(function(i, v) {
        $(v).width(colWidth[i]);
    });

    resize_chart_container();

  }).trigger('resize');

}());

$(window).ready(function(){
  update_tabs_sizes();

  if (default_settings.enable_log) {
    $('#enable_log').prop('checked', true).change();
  } else {
    $('#enable_log').prop('checked', false).change();
  }

  if (default_settings.show_topology) {
    $('#show_topology').prop('checked', true).change();
    $('#topology-chart').show();
  } else {
    $('#show_topology').prop('checked', false).change();
    $('#topology-chart').hide();
  }

  if (default_settings.show_map) {
    $('#show_map').prop('checked', true).change();
    $('#background-map').show();
  } else {
    $('#show_map').prop('checked', false).change();
    $('#background-map').hide();
  }

  $('#map_opacity').bootstrapSlider({
    formatter: function(value) {
      return "Map opacity of " + value;
    }
  })
    .on('slide', function(current) {
      $('#background-map').css('opacity', current.value);
    })
    .on('change', function(current) {
      $('#background-map').css('opacity', current.value.newValue);
    });

  load_layouts();
  draw_background_map(draw_topology);

})
