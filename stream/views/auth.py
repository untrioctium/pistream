from django.shortcuts import render_to_response
from django.http import HttpResponse
import lastfm
import logging
from stream.util import events

def auth( request ):
	if not "token" in request.GET or not request.session.session_key:
		return HttpResponse("<script>window.close()</script>")

	result = lastfm.get_auth_session(request.GET["token"])
	if result:
		request.session["scrobble.sk"] = result["key"]
		request.session["scrobble.user"] = result["name"]
		request.session.save()
		events.authenticated( request.session.session_key, result["name"] )

	return HttpResponse("<script>window.close()</script>")
