function Playlist() {};

Playlist.playingChild = false;
Playlist.states = { Stopped: 0, Playing: 1, Paused: 2 }
Playlist.state = Playlist.states.Stopped;
Playlist.songStartTime = -1;
Playlist.totalElapsed = 0;
Playlist.lastTime = -1;
Playlist.scrobbled = false;

Playlist.setState= function( state )
{
	Playlist.state = state;
	if( state == Playlist.states.Stopped )
	{
		console.log("Setting state: stopped");
		Playlist.p.children().removeClass("playlistPlaying");
		Playlist.state = Playlist.states.Stopped;
		$("#playlist .song_position").hide();
		$("#button_playpause").text("Play");
		Playlist.audio.pause();
		Playlist.seek(0);
		$("title").text("PiStream");
		Playlist.totalElapsed = 0;
		Playlist.lastTime = -1;
		Playlist.scrobbled = false;
		return;
	}
	if( state == Playlist.states.Playing )
	{
		console.log("Setting state: playing");
		Playlist.p.children().removeClass("playlistPlaying");
		this.playingChild.addClass("playlistPlaying");
		$("#playlist .song_position").hide();
		$("#button_playpause").text("Pause");
		this.playingChild.children(".song_position").show();
		Playlist.update();
		$("title").text( "PiStream: " + this.playingChild.find(".artist").text() + " - " + this.playingChild.find(".title").text() );
		Playlist.audio.play();
		Playlist.lastTime = -1;	
		return;
	}
	if( state == Playlist.states.Paused )
	{
		console.log("Setting state: paused");
		Playlist.audio.pause();
		$("#button_playpause").text("Play");
		Playlist.lastTime = -1;
		return;
	}
}

Playlist.initalize = function()
{
	this.audio = $('#player')[0];
	this.p = $('#playlist');

	this.audio.onended = function()
	{ 
		Playlist.next() 
	}
	this.audio.ontimeupdate = function() { Playlist.update() } 	
}

Playlist.next = function()
{
	Playlist.play( Playlist.playingChild.next() );
}

Playlist.prev = function()
{
	Playlist.play( Playlist.playingChild.prev() );	
}

Playlist.togglePause = function()
{
	if( Playlist.state == Playlist.states.Playing )
	{
		Playlist.setState( Playlist.states.Paused );
		return;
	}

	if( Playlist.state == Playlist.states.Paused );
		Playlist.setState( Playlist.states.Playing );
}

Playlist.seek = function( per )
{
	//if( this.state != this.states.Stopped )
		Playlist.audio.currentTime = per * Playlist.audio.duration;
}

Playlist.update = function() 
{
	if( Playlist.state != Playlist.states.Playing ) return;
	if( Playlist.lastTime == -1 ) Playlist.lastTime = Date.now();
	var per = this.audio.currentTime / this.audio.duration;
	var pos = Math.floor(Playlist.audio.currentTime);
	var t_min = Math.floor( pos / 60.0 );
	var t_sec = pos % 60;

	var now = Date.now();
	this.totalElapsed += now - Playlist.lastTime;
	Playlist.lastTime = now;

	if( (this.audio.duration / 2.0 < this.totalElapsed / 1000.0 || 
	     this.totalElapsed / 1000.0 > 240) && !this.scrobbled )
	{
		this.scrobbled = true;
		json_query("scrobble", {id: Playlist.playingChild.attr("value")}, function() {console.log("Scrobbled");});
	}
	$(".song_position").trigger( "timeUpdate", [per, t_min, t_sec] );
}

Playlist.add = function( model, id )
{
	if( id instanceof Array ) id = id.join(",");

	$.get( "/template/", {"t": "playlist_item", "id": id, "model": model}, function(data) {
		var element = Playlist.p.children().first();
		var autoplay = false;

		if( element.val() == -1 )
		{
			element.remove();
			autoplay = true;
		}

		Playlist.p.append(data);
		for( element = Playlist.p.children(".first"); element.length != 0; element = element.next() )
		{
			element.children(".song_position").hide();
			element.dblclick( element, function(event) { Playlist.play( event.data ); } );
			element.children(".remove").click( element, function(event) { Playlist.remove(element); });
		}
	
		if( autoplay ) Playlist.play(Playlist.p.children(".first"));
		Playlist.p.children(".first").removeClass("first");
	});
}

Playlist.remove = function( track )
{
	var active_track = track == this.playingChild;
	var total_tracks = this.p.length;
	var next_track = this.playingChild.next();

	track.remove();
	if( active_track && next_track.length != 0 && this.state != this.states.Stopped )
	{
		this.play( next_track );
	}
	else if( total_tracks == 0 )
	{
		Playlist.p.append("<li value=\"-1\">The playlist is empty. Search and add tracks.</li>");
		this.playingChild = false;
		this.setState( this.states.Stopped );
	}
	else if( active_track && next_track.length == 0 )
	{
		this.playingChild = this.p.first();
		this.setState( this.states.Stopped );
	}
}

Playlist.play = function( track )
{
	if( track.length == 0 )
	{
		this.setState( this.states.Stopped );
		return;		
	}

	this.playingChild = track;
	var base = window.location.href;
	if( base.indexOf(":8000") > -1 )
	{
		base = base.slice( 0, base.indexOf(":8000") );
	}

	if( base.indexOf("#") > -1 )
		base = base.slice( 0, base.indexOf("#") );

	Playlist.audio.src = base + "/static/music/" + encodeURIComponent(track.children(".path").text());
	Playlist.setState( Playlist.states.Playing );
	Playlist.lastTime = -1;
	this.totalElapsed = 0;
	Playlist.scrobbled = false;
	json_query( "now_playing", {id: track.attr("value")}, function(){} );
}

 $(function() {

$('body').on("click", ".playable", 
	function(event)
	{
		var target = $(event.target);
		var model = target.data("ps-model");
		var id = target.data("ps-id");
		Playlist.add(model, id);
		
	});

$( "#playlist" ).sortable({ axis: "y" });
$( "#playlist" ).disableSelection();

Playlist.initalize();

$("#playlist").on("timeUpdate", ".song_position", function( event, p, m, s ) {
	if( s < 10 ) s = "0" + s;
	$(this).text( m + ":" + s + "/" );
});

function handle_sidebar_click(event) {
	var val;
	if( event.currentTarget.id == "sidebar_settings" ) val = "settings";
	else
		val = $("#" + event.currentTarget.id).children("a").attr("href").slice(1); 

	paneManager.pushStack(val);
	event.preventDefault();
 }

$("#sidebar_menu").children("li").click(handle_sidebar_click);
$("#sidebar_settings").click(handle_sidebar_click);

$("#button_back").click(function(event) {
	paneManager.back();
 });

$("#button_forward").click(function(event) {
	paneManager.forward();
 });

$("#button_tracknext").click(function(event) {
	Playlist.next();
 });

$("#button_trackprev").click(function(event) {
	Playlist.prev();
 });

$("#button_playpause").click(function(event) {
	Playlist.togglePause();
 });

$("#button_stop").click(function(event) {
	Playlist.setState( Playlist.states.Stopped );
 });

paneManager.pushStack("playlist");

});
