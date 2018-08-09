PlaylistPane.prototype = new Pane();
PlaylistPane.constructor = PlaylistPane;

function PlaylistPane()
{
	Pane.prototype.constructor.call(this, "playlist", false);
	this.sidebar = "#sidebar_playlist";
}

PlaylistPane.prototype.enter = function()
{
	Pane.prototype.enter.call(this);
}

paneManager.add( new PlaylistPane() );

