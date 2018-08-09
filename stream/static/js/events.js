events = {}
events.handlers = {}

events.register_handler = function( name, func ) 
{
	if( !(name in events.handlers) )
		events.handlers[name] = [];

	events.handlers[name].push(func);
}

events.handle_event = function( msg )
{
	event = JSON.parse(msg);
	events.fire( event.name, event.payload );
	
}

events.fire = function(name, payload)
{
	if( !(name in events.handlers) )
	{
		console.log("Ignoring event '" + name + "' (no handler)");
		return;
	}

	console.log("Handling event: " + name);
	console.log(payload);
	for( var e = 0; e < events.handlers[name].length; e++ )
		events.handlers[name][e]( payload );
}

// Event fired when someone plays a track. 
//
// Expected payload:
// track_id: the id of the track that was played
// track_playcount: the new playcount for the track
// album_id: the album id the track was off of
// album_playcount: the new playcount for the album
// artist_id: the artist id of the track
// artist_playcount: the new playcount for that artist
events.register_handler( "track_played", function(p)
{
	$(".playcount[data-ps-model=track][data-ps-id=" + p.track_id + "]").text(p.track_playcount);
	$(".playcount[data-ps-model=album][data-ps-id=" + p.album_id + "]").text(p.album_playcount);
	$(".playcount[data-ps-model=artist][data-ps-id=" + p.artist_id + "]").text(p.artist_playcount);
});

events.register_handler( "authenticated", function(p)
{
	$("#pane_settings_login").text("You are logged in as " + p.username + ".");
});

events.register_handler( "pinged", function(p)
{
	console.log("Pong!");
});

