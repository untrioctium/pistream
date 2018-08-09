SearchPane.prototype = new Pane();
SearchPane.constructor = SearchPane;

function SearchPane()
{
	Pane.prototype.constructor.call(this, "search", false);
	this.sidebar = "#sidebar_search";
}

SearchPane.prototype.enter = function()
{
	Pane.prototype.enter.call(this);
}

paneManager.add( new SearchPane() );

