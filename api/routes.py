from fastapi import APIRouter
from auth.auth import get_spotify_client
from data.fetch import (
    get_full_taste_profile,
    get_lastfm_features,
    get_top_artists
)
from model.recommender import build_recommendations

router = APIRouter()


@router.get("/recommend")
def recommend(n: int = 10):
    """
    Recommends songs based on the user's full taste profile
    (liked songs + top tracks + recently played)
    scored against Last.fm similar tracks
    """
    sp = get_spotify_client()
    tracks = get_full_taste_profile(sp)
    tag_matrix, mlb, _ = get_lastfm_features(tracks)
    recommendations = build_recommendations(tracks, tag_matrix, mlb, n)
    return {"recommendations": recommendations}


"""
@router.get("/recommend/playlist/{playlist_id}")
def recommend_from_playlist(playlist_id: str, n: int = 10):
    """
    # Recommends songs based on the audio profile of a given playlist
    # May implement later; for now, not using playlist recommendations
    """
    sp = get_spotify_client()
    results = sp.playlist_tracks(playlist_id)
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
            'source': 'playlist'
        })
    tag_matrix, mlb, _ = get_lastfm_features(tracks)
    recommendations = build_recommendations(tracks, tag_matrix, mlb, n)
    return {"recommendations": recommendations}
"""

@router.get("/top-artists")
def top_artists(time_range: str = 'medium_term'):
    """
    Returns the user's top artists for a given time range.
    time_range options: short_term, medium_term, long_term
    """
    sp = get_spotify_client()
    artists = get_top_artists(sp, time_range=time_range)
    return {"top_artists": artists}


@router.get("/taste-profile")
def taste_profile():
    """
    Returns the full combined track list used to build
    the user's taste profile
    """
    sp = get_spotify_client()
    tracks = get_full_taste_profile(sp)
    return {"total_tracks": len(tracks), "tracks": tracks}