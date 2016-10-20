KYTOS_HELPER = {}

KYTOS_HELPER.ratings = function() {
  /* Atualiza votação na listagem */
  $('.rating').each(function(){
    var thisObj = $(this),
        thisVal = thisObj.attr('data-value'),
        thisStars = thisObj.attr('data-star'),
        thisChange = thisObj.attr('data-change');

    thisObj.RatingStar({
      val: thisVal,
      stars: thisStars,
      change:thisChange
    });
  });
}

KYTOS_HELPER.alert = function(target, type, status, message){

  data = {
      "type" : type,
      "status": status,
      "message": message
    }

  path_template = "/static/js/mustache-tpl/alert.html"

  KYTOS_HELPER.loadTemplate(target, data, path_template)
  /* Hide alert after 10 seconds */
  setTimeout(function(){
    target.fadeOut("slow");
  }, 10000);

}

KYTOS_HELPER.loadNapps = function(url,target, path_template){
  $.ajax({
        url: url,
        type: 'GET',
        dataType: 'json',
        success: function(data) {
          // Napps List
          if (typeof(data['napps']) == "object") {
            for (var i = 0; i < data['napps'].length; i++) {
              data['napps'][i]['tags'] = data['napps'][i]['tags'].split(',');
            }
          }
          // Napp Detail
          if (typeof(data['tags'])=="string") {
            data['tags'] = data['tags'].split(',');
          }
          KYTOS_HELPER.loadTemplate(target, data, path_template);
        },
        complete: function() {
          setTimeout(function(){
            KYTOS_HELPER.ratings();
          }, 600);
        }
    });
}

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
