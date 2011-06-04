/*Load jQuery if not already loaded*/
if(typeof jQuery == 'undefined'){
	document.write("<script type=\"text/javascript\" src=\"http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js\"></script>");
	var __noconflict = true;
}
//'<div class="context-loader">Saving&hellip;</div>'


(function ($){
	$(function(){
		var getEditableSelector = function(button){
			var editable_sel = $(button).attr("data-edit-selector");
			if (editable_sel == undefined){
				editable_sel = $(button).attr("href");
			}
			return editable_sel
		}
		// do visibility setup
		$(".iedit_form").hide();
		$(".iedit_button").click(function(){
			var editable_sel = getEditableSelector(this);
			var editable = $(editable_sel).find("*").andSelf();
			duration = $(this).attr("data-edit-slide");
			if (duration == undefined){
				editable.filter(".iedit_content").toggle();
				editable.filter(".iedit_form").toggle();
			}
			else {
				editable.filter(".iedit_content").slideToggle(duration);
				editable.filter(".iedit_form").slideToggle(duration);
			}
			return false;
		});

		// do form submission setup
		if ( !!$['ajaxForm'] ){
			var forms = $("form.iedit_form").add(
				$(".iedit_form").parents("form")  // parent forms
			).add(
				$(".iedit_form form")  // child forms
			);
			forms.ajaxForm(function() {
				alert("Successfully saved.");
			});
		}

		// show the forms that contain errors
		var error_form_buttons = $(".iedit_button").filter(function(){
			return $(getEditableSelector(this)).has(".errorlist li");
		});
		error_form_buttons.each(function(i, v){
				var editable = $(getEditableSelector(v));
				editable.filter(".iedit_content").hide();
				editable.filter(".iedit_form").show();
		});
	});
})(jQuery);
