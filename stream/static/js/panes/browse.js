BrowsePane.prototype = new Pane();
BrowsePane.constructor = BrowsePane;

function BrowsePane()
{
	Pane.prototype.constructor.call(this, "browse", false);
	this.sidebar = "#sidebar_browse";
}

BrowsePane.prototype.enter = function()
{
	Pane.prototype.enter.call(this);
}

BrowsePane.makeChild = function( data, show, success )
{
	var name = "browse_" + data.type + "_" + data.id;
	if( paneManager.paneExists( name ) )
	{
		if(show) paneManager.pushStack( name );
		return;
	}

	var id = data.id;
	var child = new BrowsePane();
	child.name = name;
	child.sidebar = "#sidebar_browse";
	child.disposable = true;

	child.div = paneManager.createPaneDiv( child.name );
	paneManager.add( child );

	$.get( "/template/", {"t": "info", "type": data.type, "id": data.id}, function(t)
	{
		$(child.div).html(t);

		if( show )
			paneManager.pushStack( child.name )

		success( child.name );
	});
}

paneManager.add( new BrowsePane() );
$(function(){

// Anything with a "browsable" class will bring up the appropriate browse pane
// based on data-ps-model and data-ps-id; tracks will add to the playlist instead
$('body').on("click", ".browsable", 
	function(event)
	{
		var target = $(event.target);
		var model = target.data("ps-model");
		var id = target.data("ps-id");
		BrowsePane.makeChild( {"id": id, "type": model}, true, function() {});
	});

$("body").on("click", ".pane_browse_sort",
	function(event)
	{
		var target = $(event.target);
		var type = target.data("ps-sort");

		var payload = {"name": {data: "ps-ascii", order:"asc"},
			       "length": {data: "ps-length", order:"desc"},
			       "playcount": {selector: ".playcount", order:"desc"}}

		$("#pane_browse_list").children().tsort(payload[type]);
	});

	$("#pane_browse_list").children().tsort({data: "ps-ascii", order:"asc"});
});
