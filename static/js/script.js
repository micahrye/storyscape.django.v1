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




/******************** Story Creator ****************************************/

var MediaObject = Backbone.Model.extend({

});

var MediaObjectSet = Backbone.Collection.extend({
	  model: MediaObject
});

var Page = Backbone.Model.extend({

	constructor: function() {
		this.objects = new MediaObjectSet();
	    Backbone.Model.apply(this, arguments);
	},

});

var PageSet = Backbone.Collection.extend({
	  model: Page
});

var Story = Backbone.Model.extend({

	initialize: function() {
	    this.bind("change-num-pages", function() {
	    	$("#story-total-pages").html(this.getNumPages());
	    });
		
		this.bind("change-current-page", function() {
			$("#story-current-page").val(this.getIndex()+1);
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
		});
	};
}

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
		StoryScape.currentStory.changePage($(this).val());
	}).keyup(function(event){
	    if(event.keyCode == 13){
			StoryScape.currentStory.changePage($(this).val());
	    }
	});
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


