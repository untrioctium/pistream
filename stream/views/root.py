from django.shortcuts import render_to_response
from stream.models import Artist, Track
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.db.models import Sum
import lastfm

import logging

panes = [["home", "Home"], 
	 ["playlist", "Playlist"], 
	 ["search", "Search"], 
	 ["browse", "Browse"],
	 ["settings", "Settings"]]

def root( request ):
	logging.getLogger(__name__).debug(request.session.session_key)
	if not request.session.session_key:
		request.session["nasty_hack_to_get_a_session"] = "why_django?"
		request.session.save()

	if (not "password" in request.GET or request.GET["password"] != "sudo") and not "scrobble.sk" in request.session:
		return render_to_response("noaccess.html", {})

	pane_list = []
	for p in panes:
		pane_list.append({"template": "panes/" + p[0] + ".html", "name": p[0], "sidebar": p[1], "js": "static/js/panes/" + p[0] + ".js" })

	response_param = {"panes": pane_list}
	response_param["artists"]= Artist.objects.order_by("name").annotate(plays=Sum("track__playcount"))

	if "scrobble.user" in request.session:
		response_param["settings_lfmuser"] = request.session["scrobble.user"]
	else:
		callback_uri = request.build_absolute_uri().split("?")[0] + "auth/"
		response_param["settings_lfmlogin"] = lastfm.LOGIN_URL + callback_uri

	return render_to_response("root.html", response_param)
