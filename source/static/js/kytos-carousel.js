function build_switches_carousel(settings){
  $('.owl-carousel').owlCarousel(settings);
}

function plot_carousel_card_radar(dpid, ifaces) {
  rx = [];
  tx = [];
  for (var i in ifaces) {
    iface = ifaces[i];
    rx.push({'value': iface.rx_util,
             'speed': iface.speed});
    tx.push({'value': iface.tx_util,
             'speed': iface.speed});
  }
  radar_data = [rx, tx];
  RadarChart("switch-chart-"+dpid, radar_data);
}

function rebuild_switches_carousel() {
  settings = default_settings.switches_carousel;
  var terminal = $('#terminal'),
      items = $('#tab_switches .item'),
      available_size = $('.terminal-body').height();

  if (!available_size || available_size <= 252) {
    settings.owlNrowNumberOfRows = 1;
  } else {
    settings.owlNrowNumberOfRows = Math.floor(available_size / 252);
  }
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
    var data = {
        switches: switches,
        fix_name: function() {
          return function(text, render) {
            return fix_name(render(text));
          }
        }
    }
    Mustache.parse(template);   // optional, speeds up future uses
    var rendered = Mustache.render(template, data);
    container.html(rendered);  //.attr("data-data", JSON.stringify(data, null, 2) );
    $.each(switches, function(index, item){
      var interfaces = get_switch_interfaces(item);
      plot_carousel_card_radar(fix_name(item.dpid), interfaces);
    })
  });

  setTimeout(function(){
    rebuild_switches_carousel();
  }, 600);
}
