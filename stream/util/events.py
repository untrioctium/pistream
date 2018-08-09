from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage
import json

event_publisher = RedisPublisher(facility="events", broadcast=True)

def publish_event( name, payload, pub = event_publisher ):
	pub.publish_message(RedisMessage(json.dumps({"name": name, "payload": payload})))

def get_allowed_channels(request, channels):
	return set(channels).intersection(['subscribe-broadcast', 'subscribe-session'])

def track_played( track ):
	event_payload = {}
	event_payload["track_id"] = track.id
	event_payload["track_playcount"] = track.playcount
	event_payload["album_id"] = track.album.id
	event_payload["album_playcount"] = track.album.playcount
	event_payload["artist_id"] = track.artist.id
	event_payload["artist_playcount"] = track.artist.playcount

	publish_event( "track_played", event_payload )

def authenticated( session_key, username ):
	session_publisher = RedisPublisher(facility="events", sessions=[session_key])
	publish_event( "authenticated", {"username": username}, session_publisher )
	
def pinged( session_key ):
	session_publisher = RedisPublisher(facility="events", sessions=[session_key])
	publish_event( "pinged", {}, session_publisher )	
