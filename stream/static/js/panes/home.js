HomePane.prototype = new Pane();
HomePane.constructor = HomePane;

function HomePane()
{
	Pane.prototype.constructor.call(this, "home", false);
	this.sidebar = "#sidebar_home";
}

HomePane.prototype.enter = function()
{
	Pane.prototype.enter.call(this);
}

paneManager.add( new HomePane() );

$(function(){

	events.register_handler("track_changed", function(p)
	{
		if( jQuery.isEmptyObject(p) )
			$("#home_content").text("Nothing is playing");
		else
		{
			$("#home_content").text(p.title + " by " + p.artist);
		}
	});

});
