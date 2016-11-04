;(function() {

$(".terminal").kterminal();

$("[type='checkbox'], [type='radio']").bootstrapSwitch();

$("a,div").focus(function(){
  $(this).blur();
})

}());
