from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models import Sum

from taggit.managers import TaggableManager
from taggit.models import TagBase, GenericTaggedItemBase

import lastfm
import logging

class MusicTag(TagBase):

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

class TaggedMusic(GenericTaggedItemBase):
    tag = models.ForeignKey(MusicTag,
                            related_name="%(app_label)s_%(class)s_items")
		
class Artist(models.Model):
	name = models.CharField(max_length = 200)
	ascii_name = models.CharField(max_length = 200)
	tags = TaggableManager(through=TaggedMusic)
	
	class Meta:
		ordering = ['name']

	def __str__(self):
		return self.name

	def __unicode__(self):
		return unicode(self.name)

	
	def info(self):
		return {
			"id": self.id, 
			"name": self.name,
			"tags": self.tags.names(),
		}

	def lastfm_info(self):
		return lastfm.artist_info(self.name)

	@property
	def parent(self):
		return None

	@property
	def length(self):
		 return self.children.aggregate(l=Sum("track__length"))["l"]

	@property
	def children(self):
		return Album.objects.filter(artist=self)

	def similar(self, count = 5):
		return [x for x in self.tags.similar_objects() if type(x) == type(self)][:count]

	@property
	def playcount(self):
		return self.children.aggregate(p=Sum("track__playcount"))["p"]

class Album(models.Model):
	name = models.CharField(max_length = 200)
	ascii_name = models.CharField(max_length = 200)
	artist = models.ForeignKey(Artist)
	tags = TaggableManager(through=TaggedMusic)

	def __str__(self):
		return self.name
	
	def info(self):
		return {
			"id": self.id,
			"name": self.name,
			"artist": self.artist.name,
			"artist_id": self.artist.id,
			"tracks": [t.id for t in self.children],
			"tags": self.tags.names(),
			"length": self.length,
		}
	
	class Meta:
		ordering = ['artist__name', 'name']

	def lastfm_info(self):
		return lastfm.album_info(self.artist.name, self.name)

	@property
	def parent(self):
		return self.artist

	@property
	def children(self):
		return Track.objects.filter(album=self).order_by("trackno", "relpath")

	def listify(self):
		return self.name

	def similar(self, count = 5):
		return [x for x in self.tags.similar_objects() if (type(x) == type(self) and x.artist.id is not self.artist.id)][:count]

	@property
	def length(self):
		return self.children.aggregate(l=Sum("length"))["l"]

	@property
	def playcount(self):
		return self.children.aggregate(p=Sum("playcount"))["p"]
	
class Track(models.Model):
	artist = models.ForeignKey(Artist)
	album  = models.ForeignKey(Album)
	trackno= models.IntegerField()
	title  = models.CharField(max_length = 200)
	relpath= models.CharField(max_length = 1000)
	length = models.IntegerField()
	tags = TaggableManager(through=TaggedMusic)
	playcount = models.IntegerField(default=0)
	ascii_title = models.CharField(max_length = 200)

	class Meta:
		ordering = ['album__name', 'relpath']

	def __str__(self):
		return self.title

	def __unicode__(self):
		return unicode(self.title)

	def register_play(self):
		self.playcount += 1
		self.save()
		logging.getLogger(__name__).debug("registered");		

	@property
	def parent(self):
		return self.album

	def info(self):
		return {
			"id": self.id,
			"title": self.title,
			"artist": self.artist.name,
			"artist_id": self.artist.id,
			"path": self.relpath,
			"length": self.length,
			"album" : self.album.name,
			"album_id": self.album.id,
			"trackno" : self.trackno,
			"playcount": self.playcount,
			"tags": self.tags.names(),
		}

	def lastfm_info(self):
		return lastfm.track_info(self.artist.name, self.title)

	def listify(self):
		return "%s - %s" % (self.artist.name, self.title)

	def similar(self, count = 5):
		ret = []
		same_artist = 0
		for s in self.tags.similar_objects():
			if s.__class__.__name__ == "Track": 
				if s.artist == self.artist:
					if same_artist < 2: ret.append(s) 
					same_artist += 1
				else: ret.append(s)

			if len(ret) == count: return ret

		return ret

	@property
	def children(self):
		return None
