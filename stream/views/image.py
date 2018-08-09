from django.shortcuts import render_to_response
from stream.models import Artist, Track, Album, MusicTag
from django.http import HttpResponse
from django.template import Context, loader
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist

import lastfm

def image( request, model, id, size ):
	album = None
	artist = None

	if model == "track":
		model = "album"
		id = Track.objects.get(pk=id).parent.id

	base = Artist.objects if model == "artist" else Album.objects

	try:
		obj = base.get(pk=id)
	except ObjectDoesNotExist:
		return HttpResponse("not found")

	if model == "album":
		artist = obj.artist.name
		album = obj.name
	else:
		artist = obj.name

	data = lastfm.image(artist=artist, album=album, size=size)
	if not data:
		if model == "album":
			return image( request, "artist", obj.artist.id, size )

		return HttpResponse("no image")
	mime = "image/" + data["type"]
	return HttpResponse( data["content"], content_type=mime )

