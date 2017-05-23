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
