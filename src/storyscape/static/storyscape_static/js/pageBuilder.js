/* page container (div or other element that this is contained in)
   should have position of relative for absolute 
   position of media objects within it to function correctly
*/

( function( $ ){
  // there's no need to do $(this) because
  // "this" is already a jquery object

  // methods are methods that can be called externally 
  var methods = {
    init : function(options){
      return this.each(function() {
        page = options; 
        if(options == undefined) page = {}; 
        if(page.lastz == undefined) page.lastz = 0; 
        if(page.topz == undefined) page.topz = 100; 
        if(page.bottomz == undefined) page.bottomz = 100; 
        if(page.maxHeight == undefined) page.maxHeight = 500; 
        if(page.minHeight == undefined) page.minHeight = 48; 
        if(page.maxWidth == undefined) page.maxWidth = 800; 
        if(page.minWidth == undefined) page.minWidth = 48; 
        if(page.appendTop == undefined) page.appendTop = 100; 
        if(page.appendLeft == undefined) page.appendLeft = 200; 
      }); 
    }, 
    addElementToPage: function(el){
      if( page == undefined )
        alert(' page has not been configured ')  
      $clone = $(el).clone(true, true); 
	
      $clone.appendTo(this); 
    
      $clone.attr('pane', 'true');  
      // all object on a page will have class pb-meida-object
      $clone.addClass('pb-media-object'); 
  
      /* When adding resizable or draggable to object
         the orig obj, img in this case, is added to a
         div object that jquery uses for controll purposes. 
         Because of this if you are accessing the org img
         you may need to actuall set the img's parent, 
         i.e. the div to position it or otherwise. 
      */

     // var aspect = $.browser.mozilla ? false : true
     // SHOULD be fixed now that we are using PNG files
     var aspect = false; 
     if( $clone.is('img') || $clone.is('textarea') ){ 
       $clone.resizable(
               { handles:'all' , 
                 autoHide: false,
                 containment: this,
                 maxHeight: page.maxHeight, 
                 minHeight: page.minHeight,
                 maxWidth: page.maxWidth,
                 minWidth: page.minWidth,
                 aspectRatio: aspect,
                 padding:0,
                 stop: resizeStopped})
                  .parent()
                    .draggable(
                       {containment: this, 
                        padding:0,
                       });
       
       $clone.parent().css({
		  'position':'absolute', 
		  top:100, left:200,
		  margin:0,
		  'z-index':'0'}); 
      }else if( $clone.is('div') ){
        $clone.draggable(
                       {containment: this, 
                        padding:0,
                       });  
        $clone.css({
		  'position':'absolute', 
		  top:100, left:200,
		  margin:0,
		  'z-index':'0'
        });  
      }else if( $clone.is("textarea") ) {   
      // ISSUE with clone of textarea not having correct
      // width for div parent
        width = $clone.width(); 
        height = $clone.height(); 
        $clone.parent().css('width', width); 
        $clone.parent().css('height', height);
      }
      $clone.after('<div class="delete-pbmo">x</div>');
      return $clone; 
    }, 
    removeElementFromPage : function(el){
      // remove from DOM
      $(el).remove(); 
    },
    changeElementZindex : function(command){

    }, 
    pageDetails : function(){

    },
    pageDefaults : function(){
        // page is a {} 
        return page; 
    }
  }// end external methods 
  
  // This sets things up
  $.fn.pageBuilder = function( method ){
    if( methods[ method ] ){
      return methods[ method ].apply( this, 
              Array.prototype.slice.call( arguments, 1 ));
    }else if ( typeof method === 'object' || ! method ) {
      return methods.init.apply( this, arguments );
    } else {
      $.error( 'Method ' +  method + 
             ' does not exist on jQuery.pageBuilder' );
    } 
  }
  
  /* inner function */
  function resizeHappening(event, ui){
    obj_width = ui.originalElement.css('width', ui.element.css('width'));
    obj_height = ui.originalElement.css('height', ui.element.css('height'));
    con_w = ui.element.css('width'); 
    con_h = ui.element.css('height'); 
    $('#dev_output').text( obj_width+'/'+ 
                         obj_height+' : '+ con_w +'/'+ con_h); 
  }

  /* inner function */
  function resizeStopped(event, ui){
    // access user interface element for size and location info.
    obj_width = ui.originalElement.css('width'); 
    obj_height = ui.originalElement.css('height'); 
    obj_top = ui.element.css('top'); 
    obj_left = ui.element.css('left'); 
    // because image is in draggable/resizable div there is a slight
    // size issue, i.e. the outer div is the size we want. 
    if( parseInt(obj_width.substr(0, obj_width.length-2 )) >=
                    page.maxWidth - 15){
      ui.element.css('width', page.maxWidth); 
      ui.originalElement.css('width', page.maxWidth); 
    }
    if( parseInt(obj_height.substr(0, obj_height.length-2 )) >= 
        page.maxHeight - 5){
      ui.element.css('height', page.maxHeight); 
      ui.originalElement.css('height', page.maxHeight); 
    }
    $('#dev_output').text( obj_width+'/'+ 
                         obj_height+' : '+ obj_top+'/'+ obj_left); 
    
  }
  

       
})( jQuery ); 


