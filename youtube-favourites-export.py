
import gdata.youtube.client


client = gdata.youtube.client.YouTubeClient()
client.client_login('email@gmail.com', 'password', 'exporter')

entries = []
uri = 'https://gdata.youtube.com/feeds/api/users/default/favorites'
while True:
    print 'Fetch', uri
    feed = client.get_videos(uri=uri, **{'max-results': 50})
    entries += feed.entry
    if not feed.get_next_link():
        break
    uri = feed.get_next_link().href

feed.entry = entries
print 'total', len(entries)
with open('youtube-favorites.xml', 'w') as fp:
    fp.write(feed.to_string())


# get subs
#

entries = []
uri = 'https://gdata.youtube.com/feeds/api/users/default/subscriptions'
while True:
    print 'Fetch', uri
    feed = client.get_feed(uri=uri, **{'max-results': 50})
    entries += feed.entry
    if not feed.get_next_link():
        break
    uri = feed.get_next_link().href

feed.entry = entries
print 'total', len(entries)
with open('youtube-subs.xml', 'w') as fp:
    fp.write(feed.to_string())
