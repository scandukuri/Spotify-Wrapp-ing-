import os
import sys
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import pandas as pd

# Read the access token from standard input
access_token = input()

if access_token:
    sp = spotipy.Spotify(auth=access_token)
    results = sp.current_user_top_tracks(limit=50, offset=0, time_range='short_term')
    results = results['items']
else:
    print("Can't get token for user.")

token = access_token

if token:
    sp = spotipy.Spotify(auth=token)
    results = sp.current_user_top_tracks(limit=5,offset=0,time_range='short_term')
    results = results['items']
else:
    print("Can't get token for user.")

track_names = []
track_artists = []
track_album_names = []
track_cover_art_urls = []
largest_images = []
track_ids = []
for track_dict in results:
    track_names.append(track_dict['name'])
    track_artists.append(track_dict['artists'][0]['name'])
    track_album_names.append(track_dict['album']['name'])
    track_cover_art_urls.append(track_dict['album']['images'])
    largest_images.append(track_dict['album']['images'][0]['url'])
    track_ids.append(track_dict['id'])


# Each song's cover art urls entry is a list of 3 dictionaries
# Access this list of 3 dictionaries for song i with track_cover_art_urls[i]
# track_cover_art_urls[i][0] is 640 x 640
# track_cover_art_urls[i][1] is 300 x 300
# track_cover_art_urls[i][2] is 64 x 64

genres = []
for artist in track_artists:
    result = sp.search(artist, limit=1, type="artist")
    artist_genres = result["artists"]["items"][0]["genres"]
    # Note that for each artist, we get a LIST of genres associated
    # Eventually we'll calculate genre by getting the UNION of all of the artist's genres
    # For now, this works. We might make it more complex in the future
    # genres should be a list of 50 lists if we have 50 artists.
    genres.append(artist_genres)

df = pd.DataFrame(list(zip(track_names, track_artists, track_album_names, track_ids, track_cover_art_urls, largest_images, genres)),
               columns =['Name', 'Artist', 'Album', 'ID', 'Cover Art Information', 'Cover Art Largest Image Link', 'Genres'])
df['index'] = pd.Series(list(range(1, len(track_names) + 1)))
df.set_index(df['index'], inplace = True)

### Top 5 songs sub-dataframe
top5 = df.head(5)[['Name', 'Artist', 'Cover Art Largest Image Link']]

### Top artist calculation here
top_artist = df['Artist'].mode()

### Top genre calculation
genres_union = []
# Find the union of genres - rap may occur 100 times, hip hop 40, etc.
for genre_list in list(df['Genres']):
    genres_union.extend(genre_list)

# This calculation finds the genre that occurs the most number of times
top_genre = max(set(genres_union), key=genres_union.count)
top_genre_formatted = top_genre.title()


def json_data():
    return top5.to_dict()


def main():
    print(json.dumps(json_data()))


if __name__ == '__main__':
    main()