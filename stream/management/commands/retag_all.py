from django.core.management.base import BaseCommand, CommandError
from stream.models import Artist, Track, Album
import lastfm
import logging

class Command(BaseCommand):
	def add_arguments(self, parser):
		parser.add_argument("models", type=str, default="alt")
		

	def handle(self, *args, **options):
		logging.disable(logging.CRITICAL)

		models = {}
		models["artist"] = {"flag": 'a', 
				    "base": Artist.objects.all(), 
				    "name": lambda x: x.name, 
				    "args": lambda x: {"artist": x.name} }
		models["album"]  = {"flag": 'l', 
				    "base": Album.objects.all(),  
				    "name": lambda x: "%s - %s" % (x.artist.name, x.name), 
				    "args": lambda x: {"artist": x.artist.name, "album": x.name}}
		models["track"]  = {"flag": 't', 
				    "base": Track.objects.all(),  
				    "name": lambda x: "%s - %s" % (x.artist.name, x.title), 
				    "args": lambda x: {"artist": x.artist.name, "track": x.title}}

		for name, opts in models.iteritems():
			if not opts["flag"] in options["models"]:
				continue

			print "Retagging " + name + "s:"
			total = opts["base"].count()
			cur = 1

			for o in opts["base"]:
				t = lastfm.tags(**(opts["args"](o)))[:7]
				out = "%s (%d/%d)" % (opts["name"](o), cur, total)
				if len(t) == 0:
					out += " (skipped)"
				else:
					o.tags.clear()
					o.tags.add(*t)
					out += " (" + ", ".join(t) + ")"
				print out
				cur += 1
