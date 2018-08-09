$.widget( "custom.catcomplete", $.ui.autocomplete, {
	_create: function() {
		this._super();
		this.widget().menu( "option", "items", "> :not(.ui-autocomplete-category)" );
	},
	_renderMenu: function( ul, items ) {
		var that = this, currentCategory = "";
		$.each( items, function( index, item ) {
			var li;
			if ( item.category != currentCategory ) {
				ul.append( "<li class='ui-autocomplete-category'>" + item.category + "</li>" );
				currentCategory = item.category;
			}
			li = that._renderItemData( ul, item );
			if ( item.category ) {
				li.attr( "aria-label", item.category + " : " + item.label );
			}
		});
	}
});

$(function() {
	$( "#q" ).catcomplete({
		source: function( request, response ) {
			$.getJSON( "/json/", 
				   {"method": "autocomplete", "term": request.term}, 
				   function( data ){
					response(data);
				   }
			)
		},
		delay: 0,
		minLength: 3,
		select: function( event, ui ) {
			this.value = "";

			if( ui.item.type == "track"){
				Playlist.add( "track", ui.item.id )
			}
			else if( ui.item.type == "artist" || ui.item.type == "album" ) {
				BrowsePane.makeChild( {"id": ui.item.id, "type": ui.item.type}, true, function() {});
			}
			
			return false;
		},
	});
});

 $(function() {

$("#pos_slider").slider({
  min: 0,
  max: 1,
  step: 0.001,
  slide: function( e, ui ){
	$(this).data("sliding", true);
  },
  stop: function( e, ui ){
	$(this).data("sliding", false);
	Playlist.seek( $(this).slider("value") );
  }
});
$("#pos_slider").bind("timeUpdate", ".song_position", function( event, p, m, s ) {
	if( $(this).data("sliding") != true ) $(this).slider("value", p);
});
//$(".footer_lower .song_position").on("timeUpdate", function(event, p, m, s) { $(this).text(p); });

paneManager.pushStack("playlist");

ws4redis = WS4Redis({
        uri: 'ws://stream.numerat.us:8000/ws/events?subscribe-broadcast&subscribe-session',
        receive_message: events.handle_event,
    });

});

