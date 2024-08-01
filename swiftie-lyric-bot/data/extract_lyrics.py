from lyricsgenius import Genius
import os
import re
import csv
from time import sleep
from shutil import copyfile

from dotenv import load_dotenv
load_dotenv()

ARTIST = "Taylor Swift"

GENIUS_TOKEN = os.getenv("GENIUS_CLIENT_ACCESS_TOKEN")

OUTPUT_PATH = 'swiftie-lyric-bot/data'
OUTPUT_FILENAME = os.path.join(OUTPUT_PATH, 'taylor_swift_tracks.csv')
OUTPUT_LYRICS_FILENAME = os.path.join(OUTPUT_PATH, 'lyrics.csv')
OUTPUT_LYRICS_PATH = os.path.join(OUTPUT_PATH, 'lyrics')

def run_and_retry(func, max_retries=3):
    for i in range(max_retries):
        try:
            return func()
        except Exception as e:
            print(f'Error: {e}')
            print(f'Waiting for 5 seconds')
            sleep(5)
            print(f'Retrying {i+1}/{max_retries}')
    raise Exception(f'Failed after {max_retries} retries')

def get_all_albums(genius, artist):
    page = 1
    albums = []
    while page:
        albums_page = genius.artist_albums(
            artist.id,
            page=page,
            per_page=50,
            )
        albums.extend(albums_page['albums'])
        page = albums_page['next_page']
    return albums

def get_lyrics(genius, lyrics_path, track_name, artist_name):

    # cached lyrics exist?
    if os.path.isfile(lyrics_path):
    
        print(f'Track: {track_name} lyrics exist')
        # read file and return lyrics
        with open(lyrics_path, "r") as f:
            lyrics_txt = f.read()
    
    else:

        # retrieve lyrics from genius
        song_dict = run_and_retry(lambda: genius.search_song(track_name, artist_name))
        
        try:
            lyrics_txt = song_dict.lyrics

        except AttributeError:
            # lyrics not available - return None
            print(f'Track: {track_name} lyrics not found')
            lyrics_txt = None
        
        else: 
            lyrics_txt = lyrics_txt[lyrics_txt.find(track_name):-5].rstrip("0123456789")

            # save the lyrics
            with open(lyrics_path,'w',encoding="utf-8") as f:
                f.write(lyrics_txt)

    return lyrics_txt
    
def format_release_date(entity):
    try:
        # date data is really messy
        date = f"{entity['release_date_components']['year']:02}-{entity['release_date_components']['month']:02}-{entity['release_date_components']['day']:02}"
    except Exception as e:
        print(f'Date formatting error: {e}')
        date = ''
    return date

def extract_lyrics():

    os.makedirs(OUTPUT_PATH, exist_ok=True)
    os.makedirs(OUTPUT_LYRICS_PATH, exist_ok=True)

    tracks_csv_file = open(OUTPUT_FILENAME, "w", encoding="utf8", newline='')
    fieldnames = [
        'album_id',
        'album_name',
        'album_cover_image',
        'album_release_date',
        'track_id',
        'track_number',
        'track_name',
        'track_artist_names',
        'track_release_date',
        'lyrics_filename'
        ]
    tracks_csv = csv.DictWriter(tracks_csv_file, fieldnames=fieldnames)
    tracks_csv.writeheader()

    lyrics_csv_file = open(OUTPUT_LYRICS_FILENAME, "w", encoding="utf8", newline='')
    fieldnames = ['track_id', 'lyrics']
    lyrics_csv = csv.DictWriter(lyrics_csv_file, fieldnames=fieldnames)
    lyrics_csv.writeheader()

    genius = Genius(GENIUS_TOKEN, verbose=False) 
    artist = genius.search_artist(ARTIST, max_songs=1, sort="popularity")
    albums = get_all_albums(genius, artist) 

    print(f'{len(albums)} albums found')

    lyrics_found = []
    for album in albums:
        album_id = album['id']
        album_name = album['name']
        try:
            album_cover_image = genius.album_cover_arts(album_id)['cover_arts'][0]['image_url'] 
        except Exception as e:
            album_cover_image = ''
            print(f'Album: {album_name} cover image not found')

        print(f'Album: {album_name}')

        tracks = run_and_retry(lambda: genius.album_tracks(album_id, per_page=50))

        for track in tracks['tracks']:
            track_id = track['song']['id']
            track_number = track['number']
            track_name = track['song']['title']

            lyrics_path = os.path.join(
                OUTPUT_LYRICS_PATH,
                f"{track_id}.txt"
            )

            lyrics_txt = get_lyrics(genius, lyrics_path, track_name, artist.name)

            if lyrics_txt is not None:

                # de-dupe lyrics csv
                if track_id not in lyrics_found:
                    lyrics_csv.writerow(
                        {
                            "track_id": track_id, 
                            "lyrics": lyrics_txt
                        }
                    )
                    lyrics_found.append(track_id)

            tracks_csv.writerow({
                'album_id': album_id,
                'album_name': album_name,
                'album_cover_image': album_cover_image,
                'album_release_date' : format_release_date(album),
                'track_id': track_id,
                'track_number': track_number,
                'track_name': track_name,
                'track_artist_names': track['song']['artist_names'] if track['song']['artist_names'] else '',
                'track_release_date' : format_release_date(track['song']),
                'lyrics_filename': lyrics_path if lyrics_txt is not None else ''
            })

    tracks_csv_file.close()
    lyrics_csv_file.close()

if __name__ == "__main__":
    extract_lyrics()