from django.shortcuts import render_to_response
from stream.models import Artist, Track, Album
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import strip_tags
import lastfm
import json

object_types = { "artist": Artist, "album": Album, "track": Track }
field_types = {"int": unicode.isdigit, 
	       "string": lambda x: True, 
               "object_type": lambda x: x in object_types, 
               "int_array": lambda x: all(unicode.isdigit(t) for t in x.split(","))}
templates = { "playlist_item": {"id": "int_array", "model": "object_type"}, "info": {"id": "int", "type": "object_type"} }

def dispatch( request ):
	if not "t" in request.GET or not request.GET["t"] in templates:
		return HttpResponse()

	template = templates[request.GET["t"]]

	for arg, t in template.iteritems():
		if not arg in request.GET or len(request.GET[arg]) == 0:
			return HttpResponse()

		if not field_types[t](request.GET[arg]):
			return HttpResponse()

	return globals()[request.GET["t"]](request)

def playlist_item( request ):
	try:
		if request.GET["model"] == "track":
			tracks = [Track.objects.get(pk=int(t)).info() for t in request.GET["id"].split(",")]
			return render_to_response( "playlist_item.html", {"tracks": tracks} )

		if request.GET["model"] == "album":
			albums = [Album.objects.get(pk=int(a)) for a in request.GET["id"].split(",")]			
			tracks = []
			for a in albums:
				tracks.extend( [t.info() for t in a.children] )

			return render_to_response( "playlist_item.html", {"tracks": tracks} )

	except ObjectDoesNotExist:
		return HttpResponse()

def info( request ):
	o = None
	t = request.GET["type"]
	try:
		o = object_types[t].objects.get(pk=int(request.GET["id"]))
	except ObjectDoesNotExist:
		return HttpResponse()
	
	param = {}
	param["o"] = o
	param["my_type"] = o.__class__.__name__.lower()
	param["children"] = o.children
	if param["children"] is not None:
		param["children_type"] = param["children"][0].__class__.__name__.lower()
	param["image"] = "/image/%s/%d/large/" % (t, o.id)

	lfmi = o.lastfm_info()
	wiki_lookup = {"album": "wiki", "artist": "bio", "track": "wiki"}
	if wiki_lookup[t] in lfmi:
		info = lfmi[wiki_lookup[t]]["content"]
		param["info_long"] = info[:info.find("Read more")]
		param["info_long"] = strip_tags(param["info_long"].replace("\n\n", "{newline}").replace("\n", "{newline}")).replace("{newline}", "<br />")
		print param["info_long"]
		param["info_short"] = "<br /><br />".join(param["info_long"].split("<br />")[:2])
	else:
		param["info_long"] = ""
		param["info_short"] = ""

	tree = []
	node = o
	while node is not None:
		tree.insert(0, unicode(node))
		node = node.parent			

	param["tree"] = tree

	return render_to_response("info.html", param)

