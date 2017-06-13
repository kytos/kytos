KYTOS_HELPER = {}

KYTOS_HELPER.loadTemplate = function(target, data, path_template){
  /* Carrega template mustache */
  target.load(path_template,function(){
    var this_obj = $(this),
        template = this_obj.context.innerHTML,
        output   = Mustache.render(template, data);
        this_obj.removeClass("loading").hide();
        this_obj.html(output);
        this_obj.fadeIn("slow");
    });

}

function scrollBehavior(){
  // custom scroolbar
  $(".customScroll").mCustomScrollbar({
    scrollButtons:{enable:true},
    theme:"light-thick",
    scrollbarPosition:"outside"
  });
}

;(function() {
  api_led = $('#statusicons .api-status');
  function update_api_status(){
    $.get(api_status)
      .done(function() {
        api_led.addClass('status-online').removeClass('status-offline');
      })
      .fail(function(){
        //console.log("Kyco API offline or inacessible!");
        api_led.removeClass('status-online').addClass('status-offline');
      });
    }

  setInterval(update_api_status, 2000);
}());
