;(function() {

  $(".terminal").kterminal();

  $("[type='checkbox'], [type='radio']").bootstrapSwitch();

  $("a,div").focus(function(){
    $(this).blur();
  })

  // carroussel
  $('.owl-carousel').owlCarousel({
    margin:10,
    nav:true,
  });

  // Change the selector if needed
  var $table = $('table.scroll'),
      $bodyCells = $table.find('tbody tr:first').children(),
      colWidth;

  function resize_topology_svg() {
    $("#topology-chart").width($('#chart').width());
    $("#topology-chart svg").attr("width", $('#chart').width());
  }

  function resize_chart_container() {
    $("#chart").height($(window).height() - $('.navbar').height());
    $("#background-map").height($(window).height() - $('.navbar').height());
  }

  $(window).on('resize', function() {
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
    resize_topology_svg();

  }).trigger('resize');

}());

$(window).ready(function(){
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

  $('#map_opacity').slider({
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

  // Load default settings defined at kytos-settings.js
  toggle_disconnected_hosts(default_settings.show_disconnected_hosts);
  toggle_unused_interfaces(default_settings.show_unused_interfaces);

  if (window.location.hash){
    if (window.location.hash.indexOf('#') == 0) {
      restore_layout(window.location.hash.split('#')[1]);
    } else {
      restore_layout(window.location.hash);
    }
  }

})
