PAGE_NAME = window.PAGE_NAME || "";
StoryScape = window.StoryScape || {};

$(document).ready(function () {
	switch (PAGE_NAME) {
		case "CREATE_STORY":
			StoryScape.initToastr();
			StoryScape.initStoryCreation();
			StoryScape.initImageLibrary();
			break;
		case "IMAGE_LIBRARY":
			StoryScape.initImageLibrary();
			break;
		case "PREVIEW_STORY":
			StoryScape.initToastr();
			StoryScape.initStoryPreview();
			break;
		case "STORY_LIBRARY":
			StoryScape.initStoryLibrary();
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
 * Called from the initialization function of any library
 */
StoryScape.initGenericLibrary = function() {
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
	$(".active .image-type-nav").click();
	
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
	
	StoryScape.initGenericLibrary();
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


/******************** Stories Library ****************************************/

/**
 * Called on init on the story library page
 */
StoryScape.initStoryLibrary = function() {
	
	StoryScape.pageSpecificMediaInitialize = function() {
		
	}
	
	StoryScape.reloadPaginatedContent = function() {
		StoryScape.SEARCH_TERM = $("#search-field").val();
		var data = {'SEARCH_TERM': StoryScape.SEARCH_TERM, 'GET_ALL_STORIES': StoryScape.ALL_IMAGES || false};
		StoryScape.loadPaginatedContent("/storyscape/stories/", StoryScape.CURRENT_PAGE, StoryScape.initializeMediaLibraryContent, data);
	}
	StoryScape.initGenericLibrary();
}


/******************** Story Models (Requires Backbone.js) ****************************************/

/**
 * The class for a dumb model to hold the information of a media object.
 */
var MediaObject = Backbone.Model.extend({
	
	constructor : function ( attributes, options ) {

		var scaleX = $('#builder-pane').innerWidth() / StoryScape.DEVICE_WIDTH,
			scaleY = $('#builder-pane').innerHeight() / StoryScape.DEVICE_HEIGHT;

		if (attributes) {
			if (attributes.x) {
				attributes.x *= scaleX;
			}
			if (attributes.y) {
				attributes.y *= scaleY;
			}
			if (attributes.width) {
				attributes.width *= scaleX;
			}
			if (attributes.height) {
				attributes.height *= scaleX;
			}
			if (attributes.font_size) {
				attributes.font_size *= Math.ceil(attributes.font_size * scaleX);
			}
		}
		
		Backbone.Model.apply( this, arguments );
		
	},

	toJSON: function(){
		var json = this.attributes;
		
		var scaleX = StoryScape.DEVICE_WIDTH / $('#builder-pane').innerWidth(),
			scaleY = StoryScape.DEVICE_HEIGHT / $('#builder-pane').innerHeight();
		
		json.x *= scaleX;
		json.y *= scaleY;
		json.width *= scaleX;
		json.height *= scaleY;
		  
		if (json.font_size) {
			json.font_size = Math.floor(json.font_size * scaleX);
		}
		  
		return json;

	},

	getX: function() {
		return this.get("x");
	},
	setX: function(val) {
		this.set("x",val);
	},
	getY: function() {
		return this.get("y");
	},
	setY: function(val) {
		this.set("y",val);
	},
	getWidth: function() {
		return this.get("width");
	},
	setWidth: function(val) {
		this.set("width",val);
	},
	getHeight: function() {
		return this.get("height");
	},
	setHeight: function(val) {
		this.set("height",val);
	},
	getFontSize: function() {
		return this.get("font_size");
	},
	setFontSize: function(val) {
		this.set("font_size",val);
	},
	getColor: function() {
		return this.get("color");
	},
	setColor: function(val) {
		this.set("color",val);
	},
	getActionCode: function() {
		return this.get("action_code");
	},
	setActionCode: function(val) {
		this.set("action_code",val);
	},
	getActionTriggerCode: function() {
		return this.get("action_trigger_code");
	},
	setActionTriggerCode: function(val) {
		this.set("action_trigger_code",val);
	},
	getPageOnTouch: function() {
		return this.get("page_on_touch");
	},
	setPageOnTouch: function(val) {
		this.set("page_on_touch",val);
	},
	getType: function() {
		return this.get("type");
	},
	setType: function(val) {
		this.set("type",val);
	},
	getText: function() {
		return this.get("text");
	},
	setText: function(val) {
		this.set("text",val);
	},
	getURL: function() {
		return this.get("url");
	},
	setURL: function(val) {
		this.set("url",val);
	},
	getObjectId: function() {
		return this.get("object_id");
	},
	setObjectId: function(val) {
		this.set("object_id",val);
	},
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

	constructor : function ( attributes, options ) {
		
		if (attributes && attributes.media_objects) {
			this.objects = new MediaObjectSet(attributes.media_objects);
		} else {
			this.objects = new MediaObjectSet();
		}
		Backbone.Model.apply( this, arguments );
		
	},
	initialize: function() {
		this.width = $('#builder-pane').innerWidth();
		this.height = $('#builder-pane').innerHeight();
		
		$('body').mousedown(_.bind(function(e) {
			if ($(e.target).hasClass("control-panel") || $(e.target).parents().hasClass("control-panel") || $(e.target).parents().hasClass("sp-container")) {
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
		
		for (var i = 0; i < this.objects.models.length; i++) {
			this.createElForMediaObject(this.objects.models[i]);
		}
	},
	
	toJSON: function(){
		  var json = this.attributes;
		  var objectlist = [];
		  for (var i = 0; i < this.objects.models.length; i++) {
			  objectlist.push(this.objects.models[i].toJSON());
		  }
		  json['media_objects'] = objectlist;
		  return json;

	},

	
	addImage: function(objectId, objectURL) {
		var $img = $('<img src="' + objectURL + '">');
		
		var mediaObject = new MediaObject();
		
		mediaObject.setX((this.width - $img.actual('width')) / 2);
		mediaObject.setY((this.height - $img.actual('height')) / 2);
		mediaObject.setWidth($img.actual('width'));
		mediaObject.setHeight($img.actual('height'));
		mediaObject.setType("image");
		mediaObject.setObjectId(objectId);
		mediaObject.setURL(objectURL);

		this.objects.add(mediaObject);
		
		this.createElForMediaObject(mediaObject);
	},
	
	addText: function() {
		var width = 200,
			height = 100;
		var mediaObject = new MediaObject();
		
		mediaObject.setX((this.width - width) / 2);
		mediaObject.setY((this.height - height) / 2);
		mediaObject.setWidth(width);
		mediaObject.setHeight(height);
		mediaObject.setType("text");
		mediaObject.setFontSize(18);
		mediaObject.setColor("#000");
		mediaObject.setText("Add Your Text Here");
		
		this.objects.add(mediaObject);
		
		this.createElForMediaObject(mediaObject);
	},
	
	createElForMediaObject: function(mediaObject) {
		var $el = $('<div class="media-object"></div>');
		if (mediaObject.getType() == "text") {
			var $textArea = $('<textarea>' + mediaObject.getText() + '</textarea>');
			$el.append($textArea);
			$el.css({
				'font-size': mediaObject.getFontSize(),
				'color': mediaObject.getColor(),
				});
			$textArea.change(function(e) {
				mediaObject.setText($(this).val());
			});
			$textArea.click(function(e) {
				e.stopPropagation();
			})
		} else {
			$el.append($('<img src="' + mediaObject.getURL() + '">'));
		}
		
		
		var $removeLink = $('<div class="remove-media-object"></div>');
		$el.append($removeLink);
		$el.data("mediaObject", mediaObject);
		
		$removeLink.click(_.bind(function() {
			this.objects.remove(mediaObject);
			$el.remove();
		}, this));
		
		$el.css({'width': mediaObject.getWidth(),
			'height': mediaObject.getHeight(),
			'left': mediaObject.getX(),
			'top': mediaObject.getY()});

		StoryScape.finishMediaObjectElInit($el,mediaObject);
		
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
				mediaObject.setWidth( $el.innerWidth());
				mediaObject.setHeight( $el.innerHeight());
			},
			zIndex:0
		});
		
		$('.context-sensitive-menu').addClass("hidden");
		$('.image-menu').removeClass("hidden");
		$('.image-menu .btn').unbind('click');
		$('.image-menu select').unbind('change');
		$('.image-menu #color-picker').unbind('change');
		
		if (mediaObject.getType() == "image") {
			$('.image-menu .settings-title').html("Image Settings");
			$('.image-menu .text-settings').css('display', 'none');
		} else {
			$('.image-menu .settings-title').html("Text Settings");
			$('.image-menu .text-settings').css('display', 'block');
			
			$('.image-menu #font-size').val(mediaObject.getActionCode() || "18");
			$('.image-menu #font-size').change(function() {
				mediaObject.setFontSize( $(this).val());
				$el.css("font-size", $(this).val()+"px");
			});
			
			$('.image-menu #color-picker').val(mediaObject.getColor() || "#000000");
			$('.image-menu #color-picker').change(function() {
				mediaObject.setColor( $(this).val());
				$el.css("color", $(this).val());
			});
		}
		
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
		
		$('.image-menu #animation-select').val(mediaObject.getActionCode() || 0);
		$('.image-menu #animation-select').change(function() {
			mediaObject.setActionCode($(this).val());
			mediaObject.setActionTriggerCode($('#animation-trigger-select').val());
		});
		$('.image-menu #animation-trigger-select').val(mediaObject.getActionTriggerCode() || ACTION_TRIGGER_CODES['Touch']);
		$('.image-menu #animation-trigger-select').change(function() {
			mediaObject.setActionCode($("#animation-select").val());
			mediaObject.setActionTriggerCode($(this).val());
		});
		$('.image-menu #preview-animation-button').click(function() {
			StoryScape.animateElement($el, mediaObject.getActionCode());
		});
		
		$('.image-menu #goto-on-touch-select').val(mediaObject.getPageOnTouch() || '');
		$('.image-menu #goto-on-touch-select').change(function() {
			mediaObject.setPageOnTouch($(this).val());
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

	url: "/storyscape/save/",

	constructor : function ( attributes, options ) {
		
		if (attributes) {
			this.pages = new PageSet(attributes.pages);
		} else {
			this.pages = new PageSet();
		}
		
		Backbone.Model.apply( this, arguments );
		
		if (attributes) {
			this.setTags(attributes.tags.join(" "));
		}
	},
	initialize: function() {
	    this.bind("change-num-pages", function() {
	    	$("#story-total-pages").html(this.getNumPages());
	    	$("#goto-on-touch-select").empty();
	    	$("#goto-on-touch-select").append("<option></option>");
	    	for (var i = 1; i <= this.getNumPages(); i++) {
		    	$("#goto-on-touch-select").append('<option value="' + i + '">' + i + '</option>');
	    	}
	    });
		
		this.bind("change-current-page", function() {
			$("#story-current-page").val(this.getIndex()+1);
			$('#builder-pane').empty();
			this.getCurrentPage().createAllElements();
	    });

		if (! this.pages.length) {
			this.insertNewPage();
		}
		this.currentIndex = 0;
		this.trigger("change-current-page");
		this.trigger("change-num-pages");
		
		$('#story-title').val(this.getTitle());
		$('#story-genre').val(this.getGenre());
		$('#story-description').val(this.getDescription());
		$('#story-tags').val(this.getTags());
		
		$("#story-controls .btn").removeClass("disabled");
		if (! this.getStoryId()) {
			$("#publish-story").addClass("disabled");
			$("#delete-story").addClass("disabled");
			$("#preview-story").addClass("disabled");
		}
		
	},
	
	toJSON: function(){
		  var json = _.clone(this.attributes);
		  var pagelist = [];
		  for (var i = 0; i < this.pages.models.length; i++) {
			  pagelist.push(this.pages.models[i].toJSON());
		  }
		  json['pages-info'] = pagelist;
		  
		  return {'story': JSON.stringify(json)};

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
		if (this.getCurrentPage()) {
			this.getCurrentPage().trigger("deselect");
		}

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
	},

	removePage: function() {
		this.getCurrentPage().trigger("deselect");
		this.pages.remove(this.pages.at(this.currentIndex));
		if (this.pages.length <= 0) {
			this.insertNewPage();
		}
		this.trigger("change-num-pages");
		this.changePage(this.getIndex());
	},
	
	setTitle: function(value) {
		this.set("title", value);
	},
	getTitle: function() {
		return this.get("title");
	},
	setGenre: function(value) {
		this.set("genre", value);
	},
	getGenre: function() {
		return this.get("genre");
	},
	setDescription: function(value) {
		this.set("description", value);
	},
	getDescription: function() {
		return this.get("description");
	},
	setTags: function(value) {
		this.set("tags", value);
	},
	getTags: function() {
		return this.get("tags");
	},
	setStoryId: function(value) {
		this.set("story_id", value);
	},
	getStoryId: function() {
		return this.get("story_id");
	},

});

/******************** Story Creator ****************************************/


StoryScape.DEVICE_WIDTH = 1280;
StoryScape.DEVICE_HEIGHT = 800;

/**
 * Should be called before Story Creator init, and Story Preview init, or anything that needs toastr
 */
StoryScape.initToastr = function() {
	toastr.options = {
			  "debug": false,
			  "positionClass": "toast-top-full-width",
			  "onclick": null,
			  "fadeIn": 300,
			  "fadeOut": 1000,
			  "timeOut": 5000,
			  "extendedTimeOut": 1000
	}
}

/**
 * Called at the end of Page.createElForMediaObject, for initializations specific to the page
 */
StoryScape.finishMediaObjectElInit = function($el, mediaObject) {
	
}

/**
 * Called on page load, before the media library is initiated
 */
StoryScape.initStoryCreation = function() {
	
	StoryScape.finishMediaObjectElInit = function($el, mediaObject) {
		$el.drags();
		$el.mousedown(function(e) {
			e.stopPropagation();
			if ($(this).hasClass("selected")) {
				return;
			}
			StoryScape.currentStory.getCurrentPage().selectElement($(this));
		});
		
		$el.bind('stoppeddrag', function() {
			mediaObject.setX( $(this).position().left);
			mediaObject.setY( $(this).position().top);
		});

	}
	
	if (window.LOAD_STORY_ID) {
		StoryScape.loadStory(window.LOAD_STORY_ID);		
	} else {
		StoryScape.currentStory = new Story();
	}
	
	
	StoryScape.initStoryNavigation();
	
	$("#delete-page").click(function() {
		StoryScape.currentStory.removePage();
	});
	$("#add-page").click(function() {
		StoryScape.currentStory.insertNewPage();
	});
	
	
	$("#color-picker").spectrum({
	    color: "#000"
	});
	
	$('#add-text').click(function(e){
		e.preventDefault();
		
		StoryScape.currentStory.getCurrentPage().addText();
	});
	
	$('#add-image').click(function(e){
		e.preventDefault();
		
		var top = $('#all-images-nav').offset().top - $('header').height() - 20;
		$('html,body').animate({scrollTop: top}, 300);
	});

	$('#story-title').change(function(e) {
		StoryScape.currentStory.setTitle($(this).val());
	});
	$('#story-description').change(function(e) {
		StoryScape.currentStory.setDescription($(this).val());
	});
	$('#story-genre').change(function(e) {
		StoryScape.currentStory.setGenre($(this).val());
	});
	$('#story-tags').change(function(e) {
		StoryScape.currentStory.setTags($(this).val());
	});
	
	$("#save-story").click(function() {
		var data = StoryScape.currentStory.toJSON();
		$.ajax("/storyscape/save/",
			{
				type: "POST",
				data:data,
				success:function(response) {
					var responseData = JSON.parse(response);
					StoryScape.currentStory.setStoryId(responseData['story_id']);
					toastr["success"]("Story successfully saved!");
					$("#publish-story").removeClass("disabled");
					$("#delete-story").removeClass("disabled");
					$("#preview-story").removeClass("disabled");
				},
		});
	});

	$("#new-story").click(function() {
		StoryScape.currentStory = new Story();
		toastr["success"]("Created a new story!");
	});

	$("#delete-story").click(function() {
		if ($(this).hasClass("disabled")) {
			return;
		}
		$.ajax("/storyscape/delete/",
			{
				type: "POST",
				data:{story_id: StoryScape.currentStory.getStoryId()},
				success:function(response) {
					StoryScape.currentStory = new Story();
					toastr["success"]("Story successfully deleted!");
				},
		});
	});
	$("#publish-story").click(function() {
		if ($(this).hasClass("disabled")) {
			return;
		}
		$.ajax("/storyscape/publish/",
			{
				type: "POST",
				data:{story_id: StoryScape.currentStory.getStoryId()},
				success:function(response) {
					toastr["success"]("Story successfully published to the app!");
				},
		});
	});
	$("#open-story").click(function() {
		$.ajax("/storyscape/my_stories/",
			{
				type: "GET",
				success:function(response) {
					var data = JSON.parse(response),
						$modal = $(("<div class='story-list'><h3>Your Stories</h3></div>")),
						template_text = $("#story-list-item").html();
					for (var i = 0; i < data.length; i++) {
						$modal.append(_.template(template_text, data[i]));
					}
					$modal.fancybox().click().unbind('click');
					$modal.find('.load-story-option').click(function() {
						StoryScape.loadStory($(this).data("story-id"), true);
						$.fancybox.close();
					});
				},
		});
	});
	
	$("#preview-story").click(function() {
		if ($(this).hasClass("disabled")) {
			return;
		}
		window.location = "/storyscape/preview/"+StoryScape.currentStory.getStoryId()+"/";
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
 * Helper function used to load a new story that we know the ID of. Can be called at any time for any reason.
 */
StoryScape.loadStory = function(storyId, showToast) {
	$.ajax("/storyscape/load/",
		{
			type: "GET",
			data: {story_id:storyId},
			success:function(response) {
				var data = JSON.parse(response);
				StoryScape.currentStory = new Story(data);
				if (showToast) {
					toastr["success"]("Story loaded!");
				}
			},
	});
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
 * Helper function to animate an element based on an action code. Uses Jquery UI, and Transit
 */
StoryScape.animateElement = function($el,code) {

	var tinyHopDistance = (704+440)/64,
		tinyHopTime = (1280+800)/64,
		smallHopDistance = (704+440)/8, 
		smallHopTime = (1280+800)/8,
		bigHopDistance = (704+440)/4; 

	var animationTime = 1000;
	
	var width = $el.width(),
		height = $el.height();
	
	switch( parseInt(code, 10) ) {
		case ACTION_CODES["Fade Out"]:
			$el.animate({opacity: 0.25}, animationTime).delay(600).animate({opacity: 1},100); 
			break; 
		case ACTION_CODES["Toggle Fade"]:
			$el.fadeOut(animationTime).fadeIn(animationTime * 1.5);
			break; 
		case ACTION_CODES["Expand"]:
			$el.transition({'scale':2},animationTime, 'linear').transition({'scale':1},animationTime);
			break; 
		case ACTION_CODES["Shrink"]:
			$el.transition({'scale':.5},animationTime, 'linear').transition({'scale':1},animationTime);
			break; 
		case ACTION_CODES["Expand-Shrink"]:
			$el.transition({'scale':2},animationTime, 'linear').transition({'scale':.5},animationTime, 'linear').transition({'scale':1},animationTime, 'linear');
			break; 
		case ACTION_CODES["Horizontal Shake"]:
	        var speed = 2 * tinyHopTime;
	        $el.effect("bounce", {times: 1, distance:tinyHopDistance, direction:'right'}, speed)
               .effect('bounce', {times:1, distance:tinyHopDistance, direction:'left'}, speed)
               .effect('bounce', {times:1, distance:tinyHopDistance, direction:'right'}, speed); 

			break; 
		case ACTION_CODES["Vertical Shake"]:
	        var speed = 2 * tinyHopTime;
	        $el.effect("bounce", {times: 1, distance:tinyHopDistance, direction:'down'}, speed)
               .effect('bounce', {times:1, distance:tinyHopDistance, direction:'up'}, speed)
               .effect('bounce', {times:1, distance:tinyHopDistance, direction:'down'}, speed); 
			break; 
		case ACTION_CODES["Jump"]:
	        var speed = 2 * smallHopTime;
	        $el.effect('bounce', {times:1, distance:smallHopDistance, direction:'up'}, speed);
			break; 
		case ACTION_CODES["Spin"]:
			$el.transition({rotate: "360deg"}, animationTime);
			break; 
		case ACTION_CODES["Drag"]:
			toastr["info"]("This element will be draggable in the app.");
			break; 
		case ACTION_CODES["Rubberband"]:
			toastr["info"]("This element will be draggable in the app, and will snap back to its origin when released.");
			break; 
		case ACTION_CODES["Slide Left"]:
			$el.animate({ 'marginLeft' : '-='+bigHopDistance+'px'}, animationTime)
				.animate({ 'marginLeft' : '+='+bigHopDistance+'px'}, animationTime);
        	break; 
		case ACTION_CODES["Slide Right"]:
			$el.animate({ 'marginLeft' : '+='+bigHopDistance+'px'}, animationTime)
				.animate({ 'marginLeft' : '-='+bigHopDistance+'px'}, animationTime);
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


/******************** Story Preview ****************************************/

/**
 * Called on page load
 */
StoryScape.initStoryPreview = function() {
	
	StoryScape.finishMediaObjectElInit = function($el, mediaObject) {
		$el.mousedown(function(e) {
			e.stopPropagation();
			e.preventDefault();
			if (mediaObject.getActionTriggerCode() == ACTION_TRIGGER_CODES['Touch']) {
				StoryScape.animateElement($el, mediaObject.getActionCode());
			}
			if (mediaObject.getPageOnTouch() >= 1) {
				StoryScape.currentStory.changePage(mediaObject.getPageOnTouch());
			}
		});
		
	}
	
	$("#make-sound").click(function () {
		$(".media-object").each(function () {
			var mediaObject = $(this).data("mediaObject");
			if (mediaObject.getActionTriggerCode() == ACTION_TRIGGER_CODES['Sound']) {
				StoryScape.animateElement($(this), mediaObject.getActionCode());
			}
		});
	});
	
	$(document).keydown(function(e){
	    if (e.keyCode == 37) { 
			StoryScape.currentStory.changePage(StoryScape.currentStory.getIndex() - 1);
	    	return false;
	    }
	    if (e.keyCode == 39) { 
			StoryScape.currentStory.changePage(StoryScape.currentStory.getIndex() + 1);
	    	return false;
	    }
	});

	
	StoryScape.initStoryNavigation();
	StoryScape.loadStory(window.LOAD_STORY_ID);

}


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


