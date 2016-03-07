$(document).ready(function(){
    //  When user clicks on tab, this code will be executed
    $("#tab-links li").click(function() {
        //  First remove class "active" from currently active tab
        $("#tab-links li").removeClass('active');

        //  Now add class "active" to the selected/clicked tab
        $(this).addClass("active");

        //  Hide all tab content
        $(".tab").hide();

        //  Here we get the href value of the selected tab
        var selected_tab = $(this).find("a").attr("href");

        //  Show the selected tab content
        $(selected_tab).fadeIn();

        //  At the end, we add return false so that the click on the link is not executed
        return false;
    });
});

function enable_text(status)
{
status=!status;
	document.form.input.disabled = status;
}