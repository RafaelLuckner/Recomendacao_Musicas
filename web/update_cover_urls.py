import pandas as pd
import os
import time
from datetime import datetime
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sources

def authenticate_spotify():
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_album_cover_and_artist(song_name, artist_name, sp):
    query = f'track:{song_name} artist:{artist_name}'
    results = sp.search(q=query, limit=1, type='track')
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        album_cover_url = track['album']['images'][0]['url']
        artist_name = track['artists'][0]['name']  # Standardized artist name from Spotify
        return album_cover_url, artist_name
    return None, None

def update_cover_urls_file(file_path="data/cover_urls.csv"):
    # Load all user histories
    todos_documentos = sources.load_all_history()
    df = pd.DataFrame(todos_documentos)
    
    # Extract unique songs from histories
    unique_songs = set()
    for history in df['historico']:
        for song in history:
            unique_songs.add((song['song'].strip().lower(), song['artist'].strip().lower()))
    
    # Load existing cover_urls.csv if it exists
    if os.path.exists(file_path):
        cover_df = pd.read_csv(file_path)
    else:
        cover_df = pd.DataFrame(columns=['track_name', 'artists', 'cover_url'])
    
    # Normalize existing data for comparison
    cover_df['track_name'] = cover_df['track_name'].str.lower().str.strip()
    cover_df['artists'] = cover_df['artists'].str.lower().str.strip()
    
    # Authenticate Spotify
    sp = authenticate_spotify()
    
    # Check for missing cover URLs
    new_entries = []
    for song, artist in unique_songs:
        # Check if song exists in cover_df
        mask = (cover_df['track_name'] == song) & (cover_df['artists'] == artist)
        if not mask.any():
            # Fetch cover URL from Spotify
            cover_url, resolved_artist = get_album_cover_and_artist(song, artist, sp)
            if cover_url and resolved_artist:
                new_entries.append({
                    'track_name': song,
                    'artists': resolved_artist,
                    'cover_url': cover_url
                })
    
    # Append new entries and save
    if new_entries:
        new_df = pd.DataFrame(new_entries)
        cover_df = pd.concat([cover_df, new_df], ignore_index=True)
        cover_df.to_csv(file_path, index=False)
    
    # Update last modified timestamp
    with open('data/last_update.txt', 'w') as f:
        f.write(str(datetime.now().date()))

if __name__ == '__main__':
    # Check if update is needed (once per day)
    today = datetime.now().date()
    last_update = None
    if os.path.exists('data/last_update.txt'):
        with open('data/last_update.txt', 'r') as f:
            last_update = datetime.strptime(f.read().strip(), '%Y-%m-%d').date()
    
    if last_update != today:
        update_cover_urls_file()