$(".leftsidebar_box dt").css({"background-color":"rgba(0,0,0,0.5)"});
$(".leftsidebar_box dt images").attr("src","{% static 'enhanced_ui/custom-imgages/select_xl01.png' %}");
$(function(){
	$(".leftsidebar_box dd").hide();
	$(".leftsidebar_box dt").click(function(){
		$(".leftsidebar_box dt").css({"background-color":"rgba(0,0,0,0)"})
		$(this).css({"background-color": "rgba(0,0,0,0)"});
		$(this).parent().find('dd').removeClass("menu_chioce");
		$(".leftsidebar_box dt images").attr("src","{% static 'enhanced_ui/custom-imgages/select_xl01.png' %}");
		$(this).parent().find('images').attr("src","{% static 'enhanced_ui/custom-imgages/select_xl.png' %}");
		$(".menu_chioce").slideUp();
		$(this).parent().find('dd').slideToggle();
		$(this).parent().find('dd').addClass("menu_chioce");
	});
})