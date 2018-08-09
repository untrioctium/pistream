SettingsPane.prototype = new Pane();
SettingsPane.constructor = SettingsPane;

function SettingsPane()
{
	Pane.prototype.constructor.call(this, "settings", false);
	this.sidebar = "#sidebar_settings";
}

SettingsPane.prototype.enter = function()
{
	Pane.prototype.enter.call(this);
}

paneManager.add( new SettingsPane() );

$(function(){
$('body').on("click", "#pane_settings_login_href", 
	function(event)
	{
		window.open($(event.target).data("ps-url") );
	});
});
