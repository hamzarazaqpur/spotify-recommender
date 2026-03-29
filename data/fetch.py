import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()

LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
LASTFM_BASE_URL = "http://ws.audioscrobbler.com/2.0/"

# Spotify data fetching
def get_liked_songs(sp):
    results = sp.current_user_saved_tracks(limit=50)
    tracks = []
    while results:
        for item in results['items']:
            track = item['track']
            if track is None:
                continue
            tracks.append({
                'id': track['id'],
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'artist_id': track['artists'][0]['id'],
                'popularity': track.get('popularity', 0),
                'source': 'liked'
            })
        results = sp.next(results)
    return tracks


def get_top_tracks(sp, time_range='medium_term', limit=50):
    results = sp.current_user_top_tracks(
        time_range=time_range,
        limit=limit
    )
    tracks = []
    for item in results['items']:
        if item is None:
            continue
        tracks.append({
            'id': item['id'],
            'name': item['name'],
            'artist': item['artists'][0]['name'],
            'artist_id': item['artists'][0]['id'],
            'popularity': item.get('popularity', 0),
            'source': f'top_tracks_{time_range}'
        })
    return tracks


def get_top_artists(sp, time_range='medium_term', limit=50):
    results = sp.current_user_top_artists(
        time_range=time_range,
        limit=limit
    )
    artists = []
    for item in results['items']:
        if item is None:
            continue
        artists.append({
            'id': item['id'],
            'name': item['name'],
            'genres': item.get('genres', []),
            'popularity': item.get('popularity', 0),
            'source': f'top_artists_{time_range}'
        })
    return artists


def get_recently_played(sp, limit=50):
    results = sp.current_user_recently_played(limit=limit)
    tracks = []
    for item in results['items']:
        track = item['track']
        if track is None:
            continue
        tracks.append({
            'id': track['id'],
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'artist_id': track['artists'][0]['id'],
            'popularity': track.get('popularity', 0),
            'played_at': item['played_at'],
            'source': 'recently_played'
        })
    return tracks


def get_full_taste_profile(sp):
    all_tracks = (
        get_liked_songs(sp) +
        get_top_tracks(sp, 'short_term') +
        get_top_tracks(sp, 'medium_term') +
        get_recently_played(sp)
    )
    seen = set()
    unique = []
    for t in all_tracks:
        if t['id'] not in seen:
            seen.add(t['id'])
            unique.append(t)
    return unique

# Last.fm data fetching
def get_lastfm_tags(artist, track, max_tags=5):
    """
    Fetches top tags for a track from Last.fm.
    Falls back to artist-level tags if track not found.
    """
    try:
        response = requests.get(LASTFM_BASE_URL, params={
            "method": "track.getTopTags",
            "artist": artist,
            "track": track,
            "api_key": LASTFM_API_KEY,
            "format": "json"
        }, timeout=5)
        data = response.json()
        if 'error' in data or 'toptags' not in data:
            return get_lastfm_artist_tags(artist, max_tags)
        tags = [
            t['name'].lower().strip()
            for t in data['toptags']['tag']
            if int(t.get('count', 0)) > 10
        ]
        return tags[:max_tags]
    except Exception as e:
        print(f"Last.fm failed for {artist} - {track}: {e}")
        return []


def get_lastfm_artist_tags(artist, max_tags=5):
    """
    Fallback: fetches tags at the artist level
    """
    try:
        response = requests.get(LASTFM_BASE_URL, params={
            "method": "artist.getTopTags",
            "artist": artist,
            "api_key": LASTFM_API_KEY,
            "format": "json"
        }, timeout=5)
        data = response.json()
        if 'error' in data or 'toptags' not in data:
            return []
        tags = [
            t['name'].lower().strip()
            for t in data['toptags']['tag']
            if int(t.get('count', 0)) > 10
        ]
        return tags[:max_tags]
    except Exception as e:
        print(f"Last.fm artist fallback failed for {artist}: {e}")
        return []


def get_lastfm_features(tracks, max_tags=5):
    """
    Fetches Last.fm tags for all tracks and encodes
    them as binary feature vectors.
    Returns the feature matrix, fitted binarizer, and raw tag lists.
    """
    from sklearn.preprocessing import MultiLabelBinarizer

    track_tags = []
    total = len(tracks)

    for i, track in enumerate(tracks):
        tags = get_lastfm_tags(track['artist'], track['name'], max_tags)
        track_tags.append(tags)
        if (i + 1) % 10 == 0:
            print(f"Processed {i + 1}/{total} tracks...")
        time.sleep(0.25)

    filled = sum(1 for t in track_tags if len(t) > 0)
    print(f"Tracks with tags: {filled}/{total}")

    mlb = MultiLabelBinarizer()
    tag_matrix = mlb.fit_transform(track_tags)

    return tag_matrix, mlb, track_tags


def get_lastfm_similar_tracks(artist, track, limit=30):
    """
    Gets similar tracks from Last.fm to use as recommendation candidates.
    Replaces Spotify's deprecated recommendations endpoint.
    """
    try:
        response = requests.get(LASTFM_BASE_URL, params={
            "method": "track.getSimilar",
            "artist": artist,
            "track": track,
            "api_key": LASTFM_API_KEY,
            "limit": limit,
            "format": "json"
        }, timeout=5)
        data = response.json()
        if 'error' in data or 'similartracks' not in data:
            return []
        return [
            {'name': t['name'], 'artist': t['artist']['name']}
            for t in data['similartracks']['track']
        ]
    except Exception as e:
        print(f"Similar tracks failed for {artist} - {track}: {e}")
        return []