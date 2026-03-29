import time
from sklearn.metrics.pairwise import cosine_similarity
from data.fetch import (
    get_lastfm_tags,
    get_lastfm_similar_tracks
)


def build_user_profile(tag_matrix):
    """
    Averages tag vectors of all user tracks
    into a single taste profile vector
    """
    return tag_matrix.mean(axis=0).reshape(1, -1)


def get_candidates(tracks):
    """
    Builds a candidate pool using Last.fm similar tracks.
    Uses top 3 tracks from the taste profile as seeds.
    """
    candidates = []
    for track in tracks[:3]:
        similar = get_lastfm_similar_tracks(track['artist'], track['name'])
        candidates.extend(similar)
        time.sleep(0.25)

    # deduplicate by name + artist
    seen = set()
    unique_candidates = []
    for c in candidates:
        key = f"{c['name']}_{c['artist']}"
        if key not in seen:
            seen.add(key)
            unique_candidates.append(c)

    return unique_candidates


def get_candidate_tag_matrix(candidates, mlb, max_tags=5):
    """
    Fetches Last.fm tags for candidate tracks and encodes
    them using the same fitted binarizer as the user profile.
    Uses transform not fit_transform to keep same vocabulary.
    """
    candidate_tags = []
    for c in candidates:
        tags = get_lastfm_tags(c['artist'], c['name'], max_tags)
        candidate_tags.append(tags)
        time.sleep(0.25)
    return mlb.transform(candidate_tags)


def build_recommendations(tracks, tag_matrix, mlb, n=10):
    """
    Full recommendation pipeline:
    1. Build user taste profile from Last.fm tag vectors
    2. Generate candidates via Last.fm similar tracks
    3. Fetch and encode candidate tags with same vocabulary
    4. Score by cosine similarity
    5. Return top N
    """
    user_profile = build_user_profile(tag_matrix)
    candidates = get_candidates(tracks)

    print(f"Total candidates: {len(candidates)}")

    if not candidates:
        print("No candidates found.")
        return []

    candidate_matrix = get_candidate_tag_matrix(candidates, mlb)

    if candidate_matrix.sum() == 0:
        print("Warning: no candidate tags matched vocabulary.")
        return candidates[:n]

    similarities = cosine_similarity(user_profile, candidate_matrix)[0]
    top_indices = similarities.argsort()[::-1][:n]

    recommendations = []
    for i in top_indices:
        recommendations.append({
            'name': candidates[i]['name'],
            'artist': candidates[i]['artist'],
            'similarity_score': round(float(similarities[i]), 4)
        })
    return recommendations