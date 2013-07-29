$(function() {
//IMPORTANT:
//NOTE: is this being used? 


    $('#upload-image-form').validate({
        messages: {
            mo_tags: "Please enter tags"
        }
    });

    $.validator.addMethod("acceptImageTypes", $.validator.methods.accept, "Selected File must be an image.");
    $.validator.addClassRules("#upload-image-form", {
        acceptImageTypes: "jpg|png|gif"

    });

});
