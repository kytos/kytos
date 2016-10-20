/*
	Autor : Erik Niebla A.
	Mail: 	ep_niebla@hotmail.com,ep.niebla@gmail.com
	Fecha: 	08/08/2015
	Requiere:	Jquery,Font Awesome
*/
(function( $ ) {
	$.fn.SetRatingStar = function(o,val) {
	  var $this=this.find('span'),v=parseFloat(val),s=0;
	  if(typeof o.callback!=='undefined'){if(parseFloat(this.find(o.input).val())!==v)o.callback(v);}       
	  $this.each(function() {    
		s=parseInt($(this).data('rating'));$(this).removeClass('full');$(this).removeClass('half');
		if (Math.ceil(v)>=s){if(Math.ceil(v)>=s&&v<(s)){$(this).addClass('half');}else{$(this).addClass('full');}}
	  });this.find(o.input).val(v);this.attr('data-val',v);
	};
	$.fn.RatingStar = function(options) {
		if(this.find('span').length===0){
			var $this=this,html=(typeof $this.data('input')==='undefined')?'<input type="hidden" name="vue" class="rating-value" />':'';$this.parent().addClass('vcenter');
			var o=$.extend({           
				stars:(typeof $this.data('stars')==='undefined')?5:parseInt($this.data('stars')),
				val:(typeof $this.data('val')==='undefined')?0:parseFloat($this.data('val')),
				change:(typeof $this.data('change')==='undefined')?true:$this.data('change'),
				input:(typeof $this.data('input')==='undefined')?'.rating-value':$this.data('input')
			}, options );$this.attr('data-input',o.input);/*console.log(o);*/
			for(var i=o.stars;i>0;i--)html=html+"<span class='"+(o.change?'star':'static')+"' data-rating='"+i+"'"+(o.change?' title="'+i+'"':'')+" ></span>"; $this.append(html);	
			if(o.change) $this.find('span').on('click', function() {$this.SetRatingStar(o,$(this).data('rating'));});
			$this.SetRatingStar(o,o.val);return $this;
		}
	}
}(jQuery));