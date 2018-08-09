#!/usr/bin/python
import os
import sys
import fnmatch
import mutagen.id3
import mutagen.easyid3
import mad
import lastfm
import pprint
import time
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import ProgrammingError
from stream.models import Artist, Track, Album
from unidecode import unidecode
from termcolor import colored;
import logging

#def colored(a, b):
#	return a

rootdir = "./stream/static/music/"

class Command(BaseCommand):
	def handle(self, *args, **options):
		logging.disable(logging.CRITICAL)
		total_time = time.time()
		results = {"skipped_exists": 0, "skipped_badtags": 0, "skipped_nolastfm": 0, "success": 0, "skipped_invalid": 0}
		for folder, subs, files in os.walk(rootdir):
			for filename in files:
				if filename.endswith((".mp3", ".MP3")):
					result = process( os.path.join( folder, filename ) ) 
					#if result != "skipped_exists": print "(%s) (%s) (%s)" % (folder, filename, result)
					results[result] += 1
		
		total_time = time.time() - total_time
		processed = 0
		for k in results:
			processed += results[k]

		print "Processed %d files in %d seconds." % (processed, total_time)
		print "\t%d files successfully added." % (results["success"])
		print "\t%d files skipped for already existing in database." % (results["skipped_exists"])
		print "\t%d files skipped for having missing or invalid tags." % (results["skipped_badtags"])
		print "\t%d files skipped for being an unknown track." % (results["skipped_nolastfm"])
		print "\t%d files skipped for invalid filenames." % (results["skipped_invalid"])

def add_tags(object, tags):
	if "tag" in tags:
		if type(tags["tag"]) is dict:
			tags["tag"] = [tags["tag"]]
			
		for t in tags["tag"]:
			if "name" in t:
				object.tags.add(t["name"])
					
def process(path):
	relpath = path[len(rootdir):]

	def print_error(reason): print "Skipping " + os.path.basename(relpath) + ": " + colored(reason, "red")

	try:
		if Track.objects.filter(relpath=relpath).exists():
			#print_error("already in database")
			return "skipped_exists"
	except ProgrammingError:
		print_error("invalid filename")
		return "skipped_invalid"

	try:
		tags = mutagen.easyid3.EasyID3(path)

		artist = tags["artist"][0].strip()
		title = tags["title"][0].strip()
		album = tags["album"][0].strip()
	except mutagen.id3.error:
		print_error("invalid tags (mutagen)")
		return "skipped_badtags"

	info = lastfm.track_info(artist, title)

	if not info:
		print_error("unknown track (last.fm error)")
		return "skipped_nolastfm"
					

	artist = info["artist"]["name"]
	title = info["name"]
					
	art_obj = Artist.objects.filter(name__exact=artist)
	if not art_obj.exists():
		art_obj = Artist(name=artist, ascii_name=unicode(unidecode(artist), "utf-8"))
		tags = lastfm.artist_info( artist )["tags"]
		art_obj.save()
		#add_tags(art_obj, tags)
		art_obj.tags.add( *lastfm.tags(artist) )
		print "Added artist: " + colored(artist, "yellow")
	else: 
		art_obj = art_obj[0]

	album = lastfm.album_info( artist, album )
	if not album:
		print_error("invalid tags")
		return "skipped_badtags"
	
	album_obj = Album.objects.filter(name__exact=album["name"], artist=art_obj)
	if not album_obj.exists():
		album_obj = Album(name=album["name"], artist=art_obj, ascii_name=unicode(unidecode(album["name"]), "utf-8"))
		album_obj.save()
		#add_tags(album_obj, album["tags"])
		album_obj.tags.add( *lastfm.tags(artist, album = album["name"] ) )
		print "Added album: " + colored(artist, "yellow") + " -- " + colored(album["name"], "green")
	else:
		album_obj = album_obj[0]
		
	trackno = 0
	
	tracklen = int(mad.MadFile(path).total_time() / 1000.0)
		
	track_obj = Track.objects.filter(title__exact=title, artist = art_obj, album = album_obj)
	if not track_obj.exists():

		#try to extract a track number
		ex = ""
		for c in os.path.basename(path):
			if c.isdigit():
				ex += c
			else:
				break

		if ex is not "":
			trackno = int(ex)
			ex = str(trackno)
			ex = " " + ex
			ex += ". "

		track_obj = Track(title=title, ascii_title = unicode(unidecode(title), "utf-8"), artist = art_obj, album = album_obj, relpath=relpath, length=tracklen, trackno = trackno )
		track_obj.save()
		#add_tags(track_obj, info["toptags"])
		track_obj.tags.add( *lastfm.tags(artist, title) )
		sec = str(tracklen%60)
		
		if len(sec) == 1:
			sec = "0" + sec
		print "Added track: " + colored(artist, "yellow") + " - \"" + ex + colored(title, "cyan") + "\" (" + str(tracklen//60) + ":" + sec + ")"
		return "success"
	else:
		#print_error("already in database")
		return "skipped_exists"
