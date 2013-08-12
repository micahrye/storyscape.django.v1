(function($) {
	$.fn.paginate = function(options) {
		var opts = $.extend({}, $.fn.paginate.defaults, options);
		return this.each(function() {
			$this = $(this);
			var o = $.meta ? $.extend({}, opts, $this.data()) : opts;
			var selectedpage = o.start;
			$.fn.paginate.draw(o,$this,selectedpage);	
		});
	};
	$.fn.paginate.defaults = {
		count 		: 5,
		start 		: 12,
		display  	: 5,
		onChange				: function(){return false;}
	};
	$.fn.paginate.draw = function(o,obj,selectedpage){
		if(o.display > o.count)
			o.display = o.count;
		$this.empty();
		if(o.images){
			var spreviousclass 	= 'jPag-sprevious-img';
			var previousclass 	= 'jPag-previous-img';
			var snextclass 		= 'jPag-snext-img';
			var nextclass 		= 'jPag-next-img';
		}
		else{
			var spreviousclass 	= 'jPag-sprevious';
			var previousclass 	= 'jPag-previous';
			var snextclass 		= 'jPag-snext';
			var nextclass 		= 'jPag-next';
		}
		var prevEl = selectedpage > 1 ? 'a' : 'span';
		var _first		= $(document.createElement(prevEl)).addClass('jPag-first').addClass('jPag-control').html('First');
		var _prev		= $(document.createElement(prevEl)).addClass('jPag-prev').addClass('jPag-control').html('Prev');
		
		var _divwrapleft	= $(document.createElement('div')).addClass('jPag-control-back');
		_divwrapleft.append(_first).append(_prev);
		
		var _ulwrapdiv	= $(document.createElement('div'));
		var _ul			= $(document.createElement('ul')).addClass('jPag-pages')
		var selobj;
		var first = Math.max(0, selectedpage - 6),
			last = Math.min(o.count, selectedpage + 5);
		if (first > 0) {
			_ul.append($("<li>...</li>"));
		}
		for(var i = first; i < last; i++){
			var val = i+1;
			if(val == selectedpage){
				var _obj = $(document.createElement('li')).html('<span class="jPag-current">'+val+'</span>');
				selobj = _obj;
			}	
			else{
				var _obj = $(document.createElement('li')).addClass("page-number").html('<a>'+ val +'</a>');
			}
			_obj.data("pageNumber", val);
			_ul.append(_obj);
			
		}		
		if (last < o.count) {
			_ul.append($("<li>...</li>"));
		}
		_ulwrapdiv.append(_ul);
		
		var nextEl = selectedpage < o.count ? 'a' : 'span';
		var _next		= $(document.createElement(nextEl)).addClass('jPag-next').addClass('jPag-control').html('Next');
		var _last		= $(document.createElement(nextEl)).addClass('jPag-last').addClass('jPag-control').html('Last');
		var _divwrapright	= $(document.createElement('div')).addClass('jPag-control-front');
		_divwrapright.append(_next).append(_last);
		
		//append all:
		$this.addClass('jPaginate').append(_divwrapleft).append(_ulwrapdiv).append(_divwrapright);
			
		//first and last:
		$('a.jPag-first').click(function(e){
			o.onChange(0);	
		});
		$('a.jPag-prev').click(function(e){
			o.onChange(Math.max(selectedpage - 1, 0));	
		});
		$('a.jPag-next').click(function(e){
			o.onChange(Math.min(selectedpage + 1, o.count));	
		});
		$('a.jPag-last').click(function(e){
			o.onChange(o.count);	
		});
		
		//click a page
		_ulwrapdiv.find('li.page-number').click(function(e){
			o.onChange($(this).data("pageNumber"));	
		});
		
	}

})(jQuery);