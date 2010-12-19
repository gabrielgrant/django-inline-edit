
jquery_wrapper($){
	$(function(){
		$("inline_edit_button").click(function(){
			editable = $(this).attr("href");
			$(editable).find("inline_editable_content").hide();
			$(editable).find("inline_editable_form").show();
		}
	});
)(jquery);
