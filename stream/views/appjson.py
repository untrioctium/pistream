from django.shortcuts import render_to_response
from stream.models import Artist, Track, Album, MusicTag
from django.http import HttpResponse
from django.template import Context, loader
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from unidecode import unidecode
from stream.util import events

import json
import lastfm
import time

# dictionary of string representation of objects and their python object
object_types = { "artist": Artist, "album": Album, "track": Track }

# dictionary of valid parameter types for json requests
# key is the type, value is a function that returns if the given string value is convertable to the type
param_types = {"int": unicode.isdigit, 
	       "string": lambda x: True,
	       "object_type": lambda x: x in object_types }

# dictionary of valid json methods
# the value of each key is a dictionary of expected parameters and their types
methods = {"autocomplete": {"term": "string"}, 
	   "info": {"id": "int", "type": "object_type" },
	   "register_play": {"id": "int"},
	   "now_playing": {"id": "int"},
	   "scrobble": {"id": "int"},
	   "clear_session": {},
	   "ping": {},}

# return a json error for the given reason
def make_error(reason):
	return HttpResponse(json.dumps({"error": reason}))

def dispatch( request ):
	if not "method" in request.GET:
		return make_error( "no method specified" )

	if not request.GET["method"] in methods:
		return make_error( "unknown JSON method '%s'" % request.GET["method"] )

	method = methods[request.GET["method"]]

	for arg, t in method.iteritems():
		if not arg in request.GET or len(request.GET[arg]) == 0:
			return make_error("missing parameter for '%s': %s" % (request.GET["method"], arg))
		if not param_types[t](request.GET[arg]):
			return make_error("invalid value for '%s' parameter '%s': %s (expected %s)" % (request.GET["method"], arg, request.GET[arg], t))

	return globals()[request.GET["method"]](request)

def autocomplete(request):
	compiled = list()
	term = unidecode(request.GET.get("term"))

	if len(term) < 3:
		return HttpResponse("[]")

	auto_types = dict()
	auto_types["track"] = {"field": "ascii_title", "make_label": lambda o: "%s by %s" % (o.title, o.artist.name)}
	auto_types["album"] = {"field": "ascii_name", "make_label": lambda o: "%s (%s)" % (o.name, o.artist.name)}
	auto_types["artist"] = {"field": "ascii_name", "make_label": lambda o: o.name}

	for t, i in auto_types.iteritems():
		field = i["field"] + "__istartswith"
		pretty_cat = t.capitalize() + "s"

		for o in object_types[t].objects.filter(**{ field: term }):
			compiled.append({ "category": pretty_cat, "label": i["make_label"](o) , "type": t, "id": o.id })

	return HttpResponse(json.dumps(compiled))

def info( request ):
	try:
		i = object_types[request.GET["type"]].objects.get(pk=int(request.GET["id"])).info()
		return HttpResponse( json.dumps(i) )
	except ObjectDoesNotExist:
		return make_error( "unknown %s id %s" % (request.GET["type"], request.GET["id"]) )

def register_play( request ):
	try:
		t = Track.objects.get(pk=int(request.GET["id"]))
		t.register_play()
		return HttpResponse( json.dumps( {"playcount": t.playcount} ) )
	except ObjectDoesNotExist:
		return make_error( "unknown track id %s" % request.GET["id"] )

def now_playing( request ):
	t = None
	try:
		t = Track.objects.get(pk=int(request.GET["id"]))
	except ObjectDoesNotExist:
		return make_error( "unknown track id %s" % request.GET["id"] )		

	request.session["scrobble.start_time"] = int(time.time())
	request.session["scrobble.track_id"] = int(request.GET["id"])

	if not "scrobble.sk" in request.session:
		return make_error( "user is not logged in to last.fm" )

	if not lastfm.now_playing( t.artist.name, t.title, request.session["scrobble.sk"] ):
		return make_error( "last.fm error" )
	else:
		return HttpResponse( json.dumps({"status": "update_ok"}) )	

def scrobble( request ):

	if not "scrobble.start_time" in request.session or not "scrobble.track_id" in request.session:
		return make_error( "no playing track" )

	if not request.session["scrobble.track_id"] == int(request.GET["id"]):
		return make_error( "track to scrobble does not match previously stored value" )

	t = None
	try:
		t = Track.objects.get(pk=int(request.GET["id"]))
	except ObjectDoesNotExist:
		return make_error( "unknown track id %s" % request.GET["id"] )	

	elapsed_time = int(time.time()) - request.session["scrobble.start_time"]
	track_length = t.length

	if track_length < 30:
		return make_error( "track too short (%s sec)" % track_length )

	if not (elapsed_time >= 240 or elapsed_time >= track_length / 2 - 5):
		return make_error( "too little time elapsed (%d)" % elapsed_time )

	t.register_play()
	events.track_played(t)

	if not "scrobble.sk" in request.session:
		return make_error( "user is not logged in to last.fm" )

	if not lastfm.scrobble( t.artist.name, t.title, request.session["scrobble.start_time"], request.session["scrobble.sk"] ):
		return make_error( "lastfm error" )

	del request.session["scrobble.start_time"]
	del request.session["scrobble.track_id"]

	return HttpResponse( json.dumps({"status": "scrobble_ok"}) )

def ping( request ):
	events.pinged( request.session.session_key )
	return HttpResponse( json.dumps({}) )

def clear_session( request ):
	request.session.flush()
	return HttpResponse( json.dumps({}) )
