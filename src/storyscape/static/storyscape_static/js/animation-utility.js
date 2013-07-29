
  // IMPORTANT: animation values should match values in 
  // reader 

  var BOUNCE_BACK_ACTION_REMOVE = 100; 
  var SLIDE_RIGHT_AND_RETURN_ACTION = 101; 
  var SLIDE_LEFT_AND_RETURN_ACTION = 116; 
  var EXPAND_ACTION = 102; 
  var SHRINK_ACTION = 103; 
  var EXPAND_SHRINK_ACTION = 104; 
  var FADE_ACTION = 105; 
  var VERTICAL_SQUASH_ACTION = 106; 
  var JUMP_ACTION = 107; 

  var DRAG_ACTION = 110; 
  var DRAG_GLID_BACK_ACTION = 111; 
  var SPIN_ACTION = 112;
  var FADE_IN_OUT_ACTION = 113; 
  var HORIZONTAL_SHAKE_ACTION = 114; 
  var VERTICAL_SHAKE_ACTION = 115; 
  var GOTO_ACTION = 200
  var animeCode = 'anime-code';
  var gotoAttr = 'goto-page';   
  var ON_TOUCH = 300; 
  var ON_SOUND = 301;
  var ON_SPEECH = 302;
  var animeTrigger = 'animate-on';

  //TODO: change, this is hard coded for dev should make 
  //sure match reader... SCALED valus
  var mTinyHop = (704+440)/64; 
  var mTinyHopNoScale = (1280+800)/64; //use for time
  var mSmallHop = (704+440)/8; 
  var mSmallHopNoScale = (1280+800)/8; //use for time
  var mBigHop = (704+440)/4; 
   
  function setAttr(elem, attr, action){
      if( $(elem).attr(attr)){
          $(elem).removeAttr(attr);
      }

      //DRAG_ACTION 
      //DRAG_GLID_BACK_ACTION 
      $(elem).attr(attr, action);
  }
  function setGoto(elem, page){
    $(elem).attr(gotoAttr, page); 
  }
  function setAnimation(elem, action){
      if( $(elem).attr(gotoAttr) ){
        $(elem).removeAttr(gotoAttr); 
      }
      if( $(elem).attr(animeCode)){
          $(elem).removeAttr(animeCode);
      }
      $(elem).attr(animeCode, action);
  }
  function setAnimationTrigger(elem, action){
      if( $(elem).attr(animeTrigger)){
          $(elem).removeAttr(animeTrigger);
      }
      $(elem).attr(animeTrigger, action);
  }
  function animate(el){
    var speed = 0;
    var action = parseInt($(el).attr(animeCode)); 
    if( $(el).attr("animated") == "true" ){
        return 1; 
    }else if( action == DRAG_ACTION || 
              action == DRAG_GLID_BACK_ACTION ) {
        alert("Drag actions are not animated."+
             " Drag allows the user to drag an"+
             " image in the finished story on a" +
             " mobile device using their finger."); 
        return 1;
    }else{
        $(el).attr("animated", "true"); 
        $(el).parent().draggable({disabled: true});
        $(el).parent().removeClass('ui-state-disabled');
    }
    switch( action ){
      /* while animating disable draggable, otherwise causes problems 
           if user draggs item. remove ui-state-disabled so that image 
           is not faded out. Again, we have to animate element parent 
           since image is containted in div for resize and draggable 
           properties.  
      */
      case FADE_ACTION:
        if( parseInt($(el).css("opacity")) >= 0.25 )
          $(el).animate({opacity: 0.25}, 1000, animationComplete); 
        else
          $(el).animate({opacity: 1}, 1000, animationComplete); 
        break; 
      case FADE_IN_OUT_ACTION: 
        $(el).fadeOut(1000).fadeIn(1500, animationComplete );
        break; 
      case SLIDE_LEFT_AND_RETURN_ACTION:
        $(el).parent().animate({ 'marginLeft' : '-='+mBigHop+'px'}, 1000);
        $(el).parent().animate({ 'marginLeft' : '+='+mBigHop+'px'}, 1000,
                        animationComplete );
        break;
      case SLIDE_RIGHT_AND_RETURN_ACTION:
        $(el).parent().animate({ 'marginLeft' : '+='+mBigHop+'px'}, 1000);
        $(el).parent().animate({ 'marginLeft' : '-='+mBigHop+'px'}, 1000,
                        animationComplete );
        break;
      case EXPAND_ACTION:
        speed = 1000; 
        expand(el, speed, 'ANIMATION_COMPLETE');
        break; 
      case SHRINK_ACTION: 
        speed = 1000; 
        shrink(el, speed, 'ANIMATION_COMPLETE');
        break; 
      case EXPAND_SHRINK_ACTION: 
        speed = 1000; 
        expand(el, speed, 'ANIMATION_CONTINUE');
        shrink(el, speed, 'ANIMATION_COMPLETE'); 
        break; 
      case JUMP_ACTION:
        speed = 2*mSmallHopNoScale;
        $(el).parent().effect('bounce', 
                        {times:1, distance:mSmallHop, 
                        direction:'up'}, speed,
                        animationComplete );
        break; 
      case VERTICAL_SHAKE_ACTION:
        /*$(el).parent().effect("bounce", 
                        {times: 3, distance:mTinyHop, 
                        direction:'up'}, 500,
                        animationComplete ); */
        speed = 2*mTinyHopNoScale;
        $(el).parent().effect("bounce", 
                        {times: 1, distance:mTinyHop, 
                        direction:'down'}, speed)
                      .effect('bounce',
                        {times:1, distance:mTinyHop, 
                        direction:'up'}, speed)
                      .effect('bounce',
                        {times:1, distance:mTinyHop, 
                        direction:'down'}, speed, animationComplete ); 
        break; 
      case HORIZONTAL_SHAKE_ACTION:
        speed = 2*mTinyHopNoScale;
        $(el).parent().effect("bounce", 
                        {times: 1, distance:mTinyHop, 
                        direction:'right'}, speed)
                      .effect('bounce',
                        {times:1, distance:mTinyHop, 
                        direction:'left'}, speed)
                      .effect('bounce',
                        {times:1, distance:mTinyHop, 
                        direction:'right'}, speed, animationComplete ); 
        break; 
      case SPIN_ACTION: 
        $(el).parent().rotate( {angle:0, animateTo:360, 
                                callback:animationComplete   });
        break; 
      default: 
        $(el).attr('animated', 'false');
        break;
        //
    }
    function animationComplete(){
        if( $(this).is("img") ){
          $(this).trigger("ANIME_COMPLETE"); 
          $(this).parent().draggable({disabled:false}); 
        }else if( $(this).is("div") ){
          // parent div of image media object, get mo
          $(this).draggable({disabled:false}); 
          mo = $(this).children()[0]; 
          if( $(mo).is("img") )
              $(mo).trigger("ANIME_COMPLETE"); 
        }
    }
    function expand(el, speed, directive){
        $(el).parent().effect('scale', {percent:200, origin:['middle', 'center'],
                        direction:'both'}, speed, function(){
                            endScale(this, 'ANIMATION_CONTINUE') })
                      .effect('scale', {percent:50, origin:['middle', 'center'],  
                        direction:'both'}, speed, 
                        function(){
                            endScale(this, directive) });  
    }
    function shrink(el, speed, directive){
        $(el).parent().effect('scale', {percent:50, origin:['middle', 'center'],
                        direction:'both'}, speed, function(){
                            endScale(this, 'ANIMATION_CONTINUE') })
                      .effect('scale', {percent:200, origin:['middle', 'center'],  
                        direction:'both'}, speed, 
                        function(){
                            endScale(this, directive) });  
    }
    function endScale(el, directive){ 
       if( $(el).is("div") ){
          $(el).width( $(el).find('.media-object').width() );
          $(el).height( $(el).find('.media-object').height() );
          if(directive === 'ANIMATION_COMPLETE'){
             resetPMO(el);
          }
       }
    }
    function resetPMO(el){
      $(el).draggable({disabled:false}); 
      mo = $(el).children()[0]; 
      if( $(mo).is("img") )
        $(mo).trigger("ANIME_COMPLETE"); 
    }
  }
