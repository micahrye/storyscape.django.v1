PAGE_NAME = window.PAGE_NAME || "";
StoryScape = window.StoryScape || {};

$(document).ready(function () {
	switch (PAGE_NAME) {
		case "CREATE_STORY":
			StoryScape.initStoryCreation();
			StoryScape.initImageLibrary();
			break;
		case "IMAGE_LIBRARY":
			StoryScape.initImageLibrary();
			break;
		default:
			break;
	}
});

/******************** Pagination Helper Functions ****************************************/

/**
 * Generic function to load a new page of library contents. Usually, pages call this through a simple wrapper called StoryScape.reloadPaginatedContent()
 */
StoryScape.loadPaginatedContent = function(url, pageNumber, callback, data) {
	$("#pagination_content").addClass("hidden");
	$("#pagination_loader").removeClass("hidden");
	
	data = data || {};
	data['PAGE_NUMBER'] = pageNumber;
	data['NEED_ADD_BUTTONS'] = window.NEED_ADD_BUTTONS || false;
	
	$.ajax({
		type: "GET",
		url: url,
		data: data,
		success: function(result) {
			var data = JSON.parse(result);
			
			$("#pagination_loader").addClass("hidden");
			
			$("#pagination_content").html(data.content);
			$("#pagination_content").removeClass("hidden");
			
			StoryScape.NUMBER_OF_PAGES = data.pages;
			StoryScape.CURRENT_PAGE = data.current_page;
			
			callback();
		}
	});
	
}

/**
 * 
 */
StoryScape.initializePaginator = function(){
	StoryScape.NUMBER_OF_PAGES = StoryScape.NUMBER_OF_PAGES || 0;
	
    var pconfig = {
            count: StoryScape.NUMBER_OF_PAGES,
            start: StoryScape.CURRENT_PAGE,
            display: 10,
            border: false,
            images: false,
            mouse: 'press',
            onChange: function(pageNumber){
            	StoryScape.CURRENT_PAGE = pageNumber;
            	StoryScape.reloadPaginatedContent();
            }
          };

	$("#jpaginate").paginate(pconfig).click();
};  


/******************** Image Library ****************************************/

/**
 * 
 */
StoryScape.imageUpload = function(dataString) {
	var data = JSON.parse(dataString);
	var $form = $(data['form']);
	$form.find('form').ajaxForm({
		beforeSubmit: function() {
            return $form.find('form').validate().form();
        },
        success: function(dataString) {
        	StoryScape.imageUpload(dataString);
        	StoryScape.reloadPaginatedContent();
        }
    });
	$form.find('form').validate({
		rules: {
			mo_tags:{
				required:true   
			},
			upload_image: {
				accept: "image/*",
				required: true
	        }
		},
		messages: {
			mo_tags:{
				required: "Please enter tags for the image."
			},
			upload_image: {
				accept: "Only PNGs and JPEGs are currently allowed.",
				required: "Please upload an image."
			}
		}
	});
	$form.fancybox().click().unbind('click');
}

/**
 * Called on init on any page that has a media library
 */
StoryScape.initImageLibrary = function() {
	

	$("#image-upload").click(function(e) {
		e.preventDefault();
		$.ajax({
			type: "GET",
			url: '/medialibrary/image_upload/',
			data: {},
			success: StoryScape.imageUpload
		});
	});
	StoryScape.reloadPaginatedContent = function() {
		StoryScape.SEARCH_TERM = $("#search-field").val();
		var data = {'SEARCH_TERM': StoryScape.SEARCH_TERM, 'GET_ALL_IMAGES': StoryScape.ALL_IMAGES || false};
		StoryScape.loadPaginatedContent("/medialibrary/get_media_objects", StoryScape.CURRENT_PAGE, StoryScape.initializeMediaLibraryContent, data);
	}

	StoryScape.reloadPaginatedContent();
	
	$("#search-form").submit(function(e) {
		e.preventDefault();
		StoryScape.reloadPaginatedContent();
		return false;
	})
	$("#search-field").val(StoryScape.SEARCH_TERM);
	
	$(".image-type-nav").click(function(e) {
		e.preventDefault();
		$('.image-type-nav').parents("ul").find("li").removeClass("active");
		$(this).parent().addClass("active");
		StoryScape.ALL_IMAGES = $(this).attr("id") == "all-images-nav";
		StoryScape.reloadPaginatedContent();
	})
	
	var onSearchChange = function() {
		if ($(this).val()) {
			$("#search-form-cancel").css("display","inline-block");
		} else {
			$("#search-form-cancel").css("display","none");
		}
	}
	$("#search-field").keyup(onSearchChange).change(onSearchChange);
	$("#search-form-cancel").click(function() {
		$("#search-field").val("").keyup();
		StoryScape.reloadPaginatedContent();
	})

}

/**
 * Called after a page of Media Library content is loaded, which happens on page load or filtering or page changing
 */
StoryScape.initializeMediaLibraryContent = function() {
	$(".toggle-favorite").click(function(e) {
		e.preventDefault();
		var $this = $(this);
		var object_id = $this.parents('.thumbnail-container').data("mediaobject-id");
		$.ajax({
			type: "POST",
			url: '/medialibrary/toggle_favorite_mo/',
			data: {'MEDIA_OBJECT_ID': object_id},
			success: function() {
				$this.find('span').toggleClass('hidden');
			}
		});
	});
	StoryScape.initializePaginator();
	
	$(".tag-link").each(function() {
		var $this = $(this), $parent = $this.parent();
		var myRight = $this.position().left + $this.outerWidth();
		var parentRight = $parent.position().left + $parent.innerWidth() + ($parent.outerWidth() - $parent.innerWidth()) / 2;
		if (myRight > parentRight) {
			$this.remove();
		}
	});
	
	$(".tag-link").click(function() {
		$("#search-field").val($(this).html()).trigger('change');
		StoryScape.reloadPaginatedContent();
	})
	
	$(".image-thumbnail-link").fancybox({
    	openEffect	: 'elastic',
    	closeEffect	: 'elastic',

    	helpers : {
    		title : {
    			type : 'inside'
    		}
    	}
    });
	
	if (StoryScape.pageSpecificMediaInitialize) {
		StoryScape.pageSpecificMediaInitialize();
	}
	
}




/******************** Story Models (Requires Backbone.js) ****************************************/

/**
 * The class for a dumb model to hold the information of a media object.
 */
var MediaObject = Backbone.Model.extend({

});

/**
 * The class for a collection of MediaObjects
 */
var MediaObjectSet = Backbone.Collection.extend({
	  model: MediaObject
});

/**
 * The class that stores the information for a given page, including a MediaObjectSet.
 * 
 * This handles all the logic of handling the actual media objects rendered within the #builder-pane
 */
var Page = Backbone.Model.extend({

	constructor: function() {
	    Backbone.Model.apply(this, arguments);
	},
	initialize: function() {
		this.objects = new MediaObjectSet();
		this.width = $('#builder-pane').innerWidth();
		this.height = $('#builder-pane').innerHeight();
		
		$('body').mousedown(_.bind(function(e) {
			if ($(e.target).hasClass("control-panel") || $(e.target).parents().hasClass("control-panel")) {
				return;
			}
			this.trigger("deselect");
		}, this));
		
		$('#builder-pane').mousedown(function(e) {
			e.preventDefault();
		});
		
		this.on("deselect", function() {
			$('.media-object.selected').resizable( "destroy" );
			$('.media-object.selected textarea').blur();
			$('.media-object').removeClass('selected');
			
			$('.context-sensitive-menu').addClass("hidden");
			$('.story-menu').removeClass("hidden");
		})
	},
	
	addImage: function(objectId, objectURL) {
		var $img = $('<img src="' + objectURL + '">');
		var mediaObject = new MediaObject({width: $img.actual('width'),
											height: $img.actual('height'),
											type: "image",
											objectURL: objectURL,
											objectId: objectId,
											x:(this.width - $img.actual('width')) / 2,
											y:(this.height - $img.actual('height')) / 2});
		this.objects.add(mediaObject);
		
		this.createElForMediaObject(mediaObject);
	},
	
	addText: function() {
		var width = 200,
			height = 100;
		var mediaObject = new MediaObject({width: width,
											height: height,
											type: "text",
											text: "Add Your Text Here",
											fontSize: 18,
											fontColor: "#000",
											fontStyle: 'normal',
											x:(this.width - width) / 2,
											y:(this.height - height) / 2});
		this.objects.add(mediaObject);
		
		this.createElForMediaObject(mediaObject);
	},
	
	createElForMediaObject: function(mediaObject) {
		var $el = $('<div class="media-object"></div>');
		
		if (mediaObject.get("type") == "text") {
			var $textArea = $('<textarea>' + mediaObject.get("text") + '</textarea>');
			$el.append($textArea);
			$el.css({
				'font-size': mediaObject.get("fontSize"),
				'color': mediaObject.get("fontColor"),
				});
			$textArea.change(function(e) {
				mediaObject.set("text", $(this).val());
			});
			$textArea.click(function(e) {
				e.stopPropagation();
			})
		} else {
			$el.append($('<img src="' + mediaObject.get("objectURL") + '">'));
		}
		
		
		var $removeLink = $('<div class="remove-media-object"></div>');
		$el.append($removeLink);
		$el.data("mediaObject", mediaObject);
		
		$removeLink.click(_.bind(function() {
			this.objects.remove(mediaObject);
			$el.remove();
		}, this));
		
		$el.css({'width': mediaObject.get("width"),
			'height': mediaObject.get("height"),
			'left': mediaObject.get("x"),
			'top': mediaObject.get("y")});
		
		$el.drags();
		$el.mousedown(function(e) {
			e.stopPropagation();
			if ($(this).hasClass("selected")) {
				return;
			}
			StoryScape.currentStory.getCurrentPage().selectElement($(this));
		});
		
		$el.bind('stoppeddrag', function() {
			mediaObject.set('x', $(this).css('left'));
			mediaObject.set('y', $(this).css('top'));
		});
		
		$('#builder-pane').append($el);
		return $el;
	},
	
	selectElement: function($el) {
		var mediaObject = $el.data("mediaObject");
		
		StoryScape.currentStory.getCurrentPage().trigger("deselect");
		$el.addClass('selected');
		$el.resizable({
			containment: "#builder-pane",
			minHeight:48,
			minWidth:48,
			stop: function( event, ui ) {
				var $el = ui.element;
				mediaObject.set('width', $el.innerWidth());
				mediaObject.set('height', $el.innerHeight());
			},
			zIndex:0
		});
		
		$('.context-sensitive-menu').addClass("hidden");
		$('.image-menu').removeClass("hidden");
		$('.image-menu .btn').unbind('click');
		$('.image-menu select').unbind('change');
		
		$('.image-menu #send-forward').click(function() {
			StoryScape.currentStory.getCurrentPage().sendForward($el);
		});
		$('.image-menu #send-backward').click(function() {
			StoryScape.currentStory.getCurrentPage().sendBackward($el);
		});
		$('.image-menu #send-front').click(function() {
			StoryScape.currentStory.getCurrentPage().sendToFront($el);
		});
		$('.image-menu #send-back').click(function() {
			StoryScape.currentStory.getCurrentPage().sendToBack($el);
		});
		
		$('.image-menu #animation-select').val(mediaObject.get("action_code") || 0);
		$('.image-menu #animation-select').change(function() {
			$el.data("mediaObject").set("action_code", $(this).val());
		});
		$('.image-menu #animation-trigger-select').val(mediaObject.get("action_trigger_code") || ACTION_TRIGGER_CODES['Touch']);
		$('.image-menu #animation-trigger-select').change(function() {
			$el.data("mediaObject").set("action_trigger_code", $(this).val());
		});
		$('.image-menu #preview-animation-button').click(function() {
			var mediaObject = $el.data("mediaObject");
			StoryScape.animateElement($el, mediaObject.get("action_code"));
		});
	},
	
	createAllElements: function() {
		this.objects.forEach(_.bind(function(mediaObject) {
			this.createElForMediaObject(mediaObject);
		}, this));
	},
	
	sendForward: function($el) {
        $el.next().after($el);
        var mediaObject = $el.data("mediaObject");
        var index = this.objects.indexOf(mediaObject);
        this.objects.remove(mediaObject);
        this.objects.add(mediaObject, {at: index+1});
	},
	sendBackward: function($el) {
		$el.prev().before($el);
        var mediaObject = $el.data("mediaObject");
        var index = this.objects.indexOf(mediaObject);
        this.objects.remove(mediaObject);
        this.objects.add(mediaObject, {at: index-1});
	},
	sendToFront: function($el) {
		$('#builder-pane').append($el);
        var mediaObject = $el.data("mediaObject");
        this.objects.remove(mediaObject);
        this.objects.push(mediaObject);
	},
	sendToBack: function($el) {
		$('#builder-pane').prepend($el);
        var mediaObject = $el.data("mediaObject");
        this.objects.remove(mediaObject);
        this.objects.unshift(mediaObject);
	},

});

/**
 * Class for a collection of Pages
 */
var PageSet = Backbone.Collection.extend({
	  model: Page
});

/**
 * This class is the Story. There should only be one of these instantiated at a time, pointed to by StoryScape.currentStory.
 * 
 * This is where all the logic is contained about all the story structure and page list, and which page is currently being shown.
 */
var Story = Backbone.Model.extend({

	initialize: function() {
	    this.bind("change-num-pages", function() {
	    	$("#story-total-pages").html(this.getNumPages());
	    });
		
		this.bind("change-current-page", function() {
			$("#story-current-page").val(this.getIndex()+1);
			$('#builder-pane').empty();
			this.getCurrentPage().createAllElements();
	    });

		this.pages = new PageSet();
		this.insertNewPage();
	},
	
	getIndex: function() {
		return this.currentIndex;
	},
	
	getCurrentPage: function() {
		return this.pages.at(this.currentIndex);
	},
	
	changePage: function(index) {
		index = _.max([index, 0]);
		index = _.min([index, this.pages.length - 1]);
		this.getCurrentPage().trigger("deselect");

		this.oldIndex = this.currentIndex;
		this.currentIndex = index;
		this.trigger("change-current-page");
		return this.currentIndex;
	},
	
	getNumPages: function() {
		return this.pages.length;
	},

	insertNewPage: function() {
		this.pages.add(new Page(), {at: this.getIndex() + 1});
		this.trigger("change-num-pages");
		if (this.pages.length == 1) {
			this.currentIndex = 0;
			this.trigger("change-current-page");
		}
	},

	removePage: function() {
		this.pages.remove(this.pages.at(this.currentIndex));
		if (this.pages.length <= 0) {
			this.insertNewPage();
		}
		this.trigger("change-num-pages");
		this.changePage(this.getIndex());
	},

});

/******************** Story Creator ****************************************/

/**
 * Called on page load, before the media library is initiated
 */
StoryScape.initStoryCreation = function() {
	StoryScape.currentStory = new Story();
	
	$('#add-image').click(function(e){
		e.preventDefault();
		
		var top = $('#all-images-nav').offset().top - $('header').height() - 20;
		$('html,body').animate({scrollTop: top}, 300);
	});
	
	StoryScape.initStoryNavigation();
	
	$("#delete-page").click(function() {
		StoryScape.currentStory.removePage();
	});
	$("#add-page").click(function() {
		StoryScape.currentStory.insertNewPage();
	});
	
	$('#add-text').click(function(e){
		e.preventDefault();
		
		StoryScape.currentStory.getCurrentPage().addText();
	});


	/**
	 * Function called at the end of the Media Library Page Initialization
	 */
	StoryScape.pageSpecificMediaInitialize = function() {
		$(".thumbnail-frame").hover(function() {
			$(this).find('.add-button').css("display","block");
		}, function() {
			$(this).find('.media-overlay').css("display","none");
		});
		$('.add-button').click(function() {
			$(this).parent().find('.been-added').css("display","block");
			$(this).css("display","none");
			var $container = $(this).parents('.thumbnail-container');
			StoryScape.currentStory.getCurrentPage().addImage($container.data('mediaobject-id'), $container.data('mediaobject-url'));
		});
	};
}

/**
 * Called from an initialization function on a page, used to initialize the story navigation. Relies on there being a StoryScape.currentStory.
 */
StoryScape.initStoryNavigation = function() {
	$("#story-prev-page").click(function() {
		StoryScape.currentStory.changePage(StoryScape.currentStory.getIndex() - 1);
	})
	$("#story-next-page").click(function() {
		StoryScape.currentStory.changePage(StoryScape.currentStory.getIndex() + 1);
	})
	var setStoryPage = function() {
	}
	$("#story-current-page").change(function() {
		StoryScape.currentStory.changePage(parseInt($(this).val(), 10) - 1);
	});
};

/**
 * Helper function to animate an element based on an action code
 */
StoryScape.animateElement = function($el,code) {

	var animationTime = 1000;
	console.log($el, code);
	
	switch( parseInt(code, 10) ) {
		case ACTION_CODES["Fade Out"]:
			$el.animate({opacity: 0.25}, animationTime).delay(600).animate({opacity: 1},100); 
			break; 
		case ACTION_CODES["Toggle Fade"]:
			break; 
		case ACTION_CODES["Expand"]:
			break; 
		case ACTION_CODES["Shrink"]:
			break; 
		case ACTION_CODES["Expand-Shrink"]:
			break; 
		case ACTION_CODES["Horizontal Shake"]:
			break; 
		case ACTION_CODES["Vertical Shake"]:
			break; 
		case ACTION_CODES["Jump"]:
			break; 
		case ACTION_CODES["Spin"]:
			break; 
		case ACTION_CODES["Drag"]:
			break; 
		case ACTION_CODES["Rubberband"]:
			break; 
		case ACTION_CODES["Slide Left"]:
			break; 
		case ACTION_CODES["Slide Right"]:
			break;
		default:
	}

};

/**
 * Draggable plugin, modified to allow for remaining within the bounds of a specified area
 */
(function($) {
    $.fn.drags = function(opt) {

        opt = $.extend({handle:"",cursor:"move", area:$('#builder-pane')}, opt);

        if(opt.handle === "") {
            var $el = this;
        } else {
            var $el = this.find(opt.handle);
        }

        return $el.css('cursor', opt.cursor).on("mousedown", function(e) {
        	if ($(e.target).hasClass('ui-resizable-handle') || $(e.target).hasClass('remove-media-object')) {
        		return;
        	}
        	
            if(opt.handle === "") {
                var $drag = $(this).addClass('draggable');
            } else {
                var $drag = $(this).addClass('active-handle').parent().addClass('draggable');
            }
            var drg_h = $drag.outerHeight(),
	            drg_w = $drag.outerWidth(),
	    		pos_y = $drag.offset().top + drg_h - e.pageY,
            	pos_x = $drag.offset().left + drg_w - e.pageX;

            var onMouseMove = function(e) {
                var drg_h = $drag.outerHeight(),
	                drg_w = $drag.outerWidth(),
	        		top = e.pageY + pos_y - drg_h,
	        		left = e.pageX + pos_x - drg_w,
	        		area_top = opt.area.offset().top + (opt.area.outerHeight() - opt.area.height()) / 2,
	            	area_left = opt.area.offset().left + (opt.area.outerWidth() - opt.area.width()) / 2;
	        	top = _.max([top,area_top]);
	        	left = _.max([left,area_left]);
	        	top = _.min([top, area_top + opt.area.height() - drg_h]);
	        	left = _.min([left, area_left + opt.area.width() - drg_w]);
	            $('.draggable').offset({
	                top:top,
	                left:left
	            })
	            e.preventDefault();
	        };
            $drag.parents().on("mousemove", onMouseMove);
            $('body').on("mouseup", function() {
            	$drag.parents().unbind("mousemove", onMouseMove);
                $('.draggable').removeClass('draggable');
                $drag.trigger('stoppeddrag');
            });

            if (! $(e.target).is('textarea') ) {
                e.preventDefault();
            }
        })

    }
})(jQuery);

/******************** Django CSRF ****************************************/

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});


