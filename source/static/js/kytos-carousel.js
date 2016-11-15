function build_switches_carousel(settings){
  $('.owl-carousel').owlCarousel(settings);
}

function rebuild_switches_carousel() {
  settings = default_settings.switches_carousel;
  var terminal = $('#terminal')
  if (terminal.hasClass('maximized')) {
      settings.owlNrowNumberOfRows = default_settings.switches_carousel_maximized;
  } else {
      settings.owlNrowNumberOfRows = default_settings.switches_carousel_normal;
  }
  var items = $('#tab_switches .item');
  $('#tab_switches').empty();
  $('#tab_switches').append('<div class="owl-carousel owl-theme"></div>');
  $('.owl-carousel').append(items);
  build_switches_carousel(settings);
}

function populate_switches_carousel() {
    var container = $('.owl-carousel'),
        switches = get_switches();

  $.get(mustache_dir + 'switch_card.template', function(template, textStatus, jqXhr) {
    template = $(template).filter('#switch-list-cards').html();
    Mustache.parse(template);   // optional, speeds up future uses
    var rendered = Mustache.render(template, {switches: switches});
    container.html(rendered);  //.attr("data-data", JSON.stringify(data, null, 2) );
    //$.each(switches, function(index, item){
      //var interfaces = get_switch_interfaces(item);
      //plot_context_radar(item.dpid, interfaces);
    //})
  });

  setTimeout(function(){
    rebuild_switches_carousel();
  }, 600);
}
