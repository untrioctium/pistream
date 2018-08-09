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
from stream.models import Artist, Track, Album
from shutil import copyfile
from termcolor import colored;
from unidecode import unidecode
#def colored(a, b):
#	return a

rootdir = "/media/flash/music/"

class Command(BaseCommand):
	def handle(self, *args, **options):
		for t in Track.objects.all():
			fullpath = os.path.join( rootdir, t.relpath )
			if "?" in fullpath:
				print "rename %s to %s" % (fullpath, fullpath.replace("?", "_"))
				newpath = fullpath.replace("?", "_")
				copyfile( fullpath, newpath )
				t.relpath = t.relpath.replace("?", "_")
				t.save()
