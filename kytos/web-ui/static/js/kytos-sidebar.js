;(function(){
  $(".right-nav-toggle").click(function(e){
      e.stopPropagation();
      e.preventDefault();
      $('#sidebar-right').toggleClass('hidden');
//    $('.navbar-header').toggleClass('hidden');
      $('#terminal').toggleClass('with-out-left-bar')
  });
}());

$(function () {
	  $('[data-top="tooltip"]').tooltip()
})
