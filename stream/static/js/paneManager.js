paneManager = {}
paneManager.panes = {}
paneManager.stack = []
paneManager.stack_pos = 0

function Pane( name, disposable )
{
	console.log("Pane.Pane(" + name + ")");
	this.name = name;
	this.div = "#pane_" + name;
	this.sidebar = "";
	this.disposable = disposable
}

Pane.prototype.enter = function()
{
	$(this.div).show();
	$("#window_title").text( $(this.div).children(".pane_title").text() );
	$("#sidebar_menu").children("li").removeClass("active");
	$(this.sidebar).addClass("active");
	$("#main_content").scrollTop(0);
	console.log( "Pane.enter(" + this.name + ")");
}

Pane.prototype.exit = function()
{
	console.log( "Pane.exit(" + this.name + ")");
}

Pane.prototype.popped = function()
{
	if( this.disposable )
	{
		console.log("Deleting " + this.name);
		$(this.div).remove();
		delete paneManager.panes[this.name];
	}
}

paneManager.createPaneDiv = function( name )
{
	if( !(name in paneManager.panes) )
	{
		var div = '<div id="pane_' + name + '" class="content_pane" style="display: none"></div>'
		$("#main_content_inner").append(div);
	}
	return "#pane_" + name;
}

paneManager.stackCurrent = function()
{
	return paneManager.panes[paneManager.stack[paneManager.stack.length - paneManager.stack_pos]];
}

paneManager.paneExists = function(pane)
{
	return pane in paneManager.panes;
}


paneManager.popStack = function()
{
	var removed = paneManager.stack.pop();
	if( paneManager.stack.indexOf(removed) == -1 )
	{
		paneManager.panes[removed].popped();
	}
}

paneManager.pushStack = function( pane )
{
	if( paneManager.stack.length > 0 && paneManager.stackCurrent().name == pane )
	{
		console.log("skipping duplicate");
		return;
	}

	if( !(pane in paneManager.panes) ) return;
	for( i = 0; i < paneManager.stack_pos - 1; i++ )
		paneManager.popStack()

	paneManager.stack_pos = 1;

	if( paneManager.stack.length != 0 )
	{
		paneManager.stackCurrent().exit();
	}

	paneManager.stack.push(pane);
	$(".content_pane").hide();

	paneManager.panes[pane].enter();
}

paneManager.add = function( pane )
{
	if( !(pane.name in paneManager.panes) )
		paneManager.panes[pane.name] = pane;
}

paneManager.back = function()
{
	if( paneManager.stack.length == 1 || paneManager.stack_pos == paneManager.stack.length ) return;

	$(".content_pane").hide();
	paneManager.stackCurrent().exit();
	paneManager.stack_pos++;
	paneManager.stackCurrent().enter();
}

paneManager.forward = function()
{
	if( paneManager.stack_pos == 1 ) return;

	$(".content_pane").hide();
	paneManager.stackCurrent().exit();
	paneManager.stack_pos--;
	paneManager.stackCurrent().enter();
}
