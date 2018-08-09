import requests
import hashlib
import os
import json
import time
import pprint
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

def track_info( artist, track ):
	r = json_request( "track.getInfo", { 'artist': artist, 'track': track, 'autocorrect': "1" })
	return False if "error" in r else r["track"]

def artist_info( artist ):
	r = json_request( "artist.getInfo", { 'artist': artist, 'autocorrect': "1" })
	return False if "error" in r else r["artist"]
	
def album_info( artist, album ):
	r = json_request( "album.getInfo", { 'artist': artist, 'album': album, 'autocorrect': "1" })
	return False if "error" in r else r["album"]	

def now_playing( artist, track, key ):
	r = json_request_signed( "track.updateNowPlaying", { 'artist': artist, 'track': track }, key )
	return False if "error" in r else r["nowplaying"]

def generate_auth_token():
	r = json_request_signed( "auth.getToken", {} )
	return False if "error" in r else r["token"]

def get_auth_session(token):
	r = json_request_signed( "auth.getSession", {"token": token} )
	return False if "error" in r else r["session"]

def scrobble( artist, track, start_time, session_key ):
	r = json_request_signed( "track.scrobble", {"artist": artist, "track": track, "timestamp": start_time}, session_key )
 	return False if "error" in r else r["scrobbles"]["scrobble"]

def tags( artist, track = False, album = False, thresh = 4 ):
	method = None
	param = {"artist": artist}
	if not album and not track:
		method = "artist.getTopTags"
	elif not track:
		method = "album.getTopTags"
		param["album"] = album
	else:
		method = "track.getTopTags"
		param["track"] = track

	r = json_request( method, param )
	if "error" in r:
		return []

	ignore_expressions = [".*\d{1}.*$", 
			      ".*album.*", 
			      "seen live$", 
			      ".*%s.*$" % artist,
			      "guilty pleasure$",
			      "wishlist$", ]

	if album is not False: ignore_expressions.append(".*%s.*$" % album)

	return [tag["name"].lower() for tag in r["toptags"]["tag"] if tag["count"] >= thresh and not any([re.match( exp, tag["name"], re.I ) is not None for exp in ignore_expressions])]
		 
def image( artist, album=None, size="large" ):
	i = artist_info( artist ) if album is None else album_info( artist, album )
	if not i or not "image" in i or len(i["image"]) == 0: return
	i = i["image"]

	sizes = ["mega", "extralarge", "large", "medium", "small"]
	if not size in sizes: size = "large"

	avail = dict()
	for s in i:
		if len(s["#text"]) > 0: 
			avail[s["size"]] = s["#text"]
	print avail

	if len(avail) == 0: return

	if not size in avail:
		for s in sizes:
			if s in avail:
				size = s
				break

	url = avail[size]
	ext = ""
	for c in reversed(url):
		if c == ".": break
		ext = c + ext

	return {"type": ext, "content": request( url, ext, {}, request_type = requests.get )}

def request( url, ext, param, cache = True, request_type = requests.get ):
	cache_path = "/home/leonhard/Projects/streamer/stream/cache"

	# calculate a hash of the request to determine its cache file name
	request_hash = hashlib.md5(str(param) + url).hexdigest() + "." + ext

	# check to see if the cache file exists
	cache_file = os.path.join(cache_path, request_hash)
	logger.debug("Last.fm request: %s" % request_hash)
	if os.path.isfile(cache_file) and cache:
		# read it and return the data
		with open(cache_file, "r") as f:
			return f.read()

	now = time.time()
	diff = now - request.last
	if diff < .25 :
		time.sleep(.25 - diff)

	r = request_type(url, params=param)
	#pprint.PrettyPrinter(indent=4).pprint(r.content)
	# cache the file for future use
	if cache:
		with open(cache_file, "w") as f:
			f.write( r.content )

	request.last = time.time()
	return r.content

request.last = 0

REQUEST_URL = "https://ws.audioscrobbler.com/2.0/"
API_KEY = "[lol redacted]"
LOGIN_URL = "http://www.last.fm/api/auth/?api_key=" + API_KEY + "&cb="
SECRET_KEY = "[lol redacted]"


def json_request( method, param ):
	# compile the request info
	request_param = { 'method': method, "api_key": API_KEY, "format": "json" }
	request_param = dict(request_param.items() + param.items())

	return json.loads(request( REQUEST_URL, "json", request_param))

def json_request_signed( method, param, session_key = False ):
	# compile the request info
	request_param = { 'method': method, "api_key": API_KEY, "format": "json" }
	request_param = dict(request_param.items() + param.items())

	if session_key is not False:
		request_param["sk"] = session_key

	signature = ""

	for key in sorted(request_param):
		if key is not "format":
			signature = "%s%s%s" % (signature, key, request_param[key])

	signature = hashlib.md5(signature.encode("utf-8") + SECRET_KEY).hexdigest()
	request_param["api_sig"] = signature

	return json.loads(request(REQUEST_URL, "json", request_param, False, requests.post))
