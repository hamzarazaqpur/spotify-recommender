# 🎵 Spotify Music Recommender

A personalized music recommendation system that combines the **Spotify Web API** and **Last.fm API** to analyze your listening history and recommend new songs tailored to your taste.

> Built as a portfolio project demonstrating end-to-end ML pipeline design, REST API development, and multi-API integration. Adapted mid-build to work around Spotify's November 2024 deprecation of their audio features and recommendations endpoints — replacing them with Last.fm's tag and similar tracks APIs.

---

## How It Works

1. **Pulls your listening data from Spotify** — liked songs, top tracks (short + medium term), and recently played
2. **Fetches Last.fm tags for each track** — genre, mood, and style descriptors like `indie`, `chill`, `melancholic`, `acoustic`
3. **Builds a taste profile vector** — averages your tag vectors into a single representation of your musical preferences
4. **Generates candidates via Last.fm** — uses `track.getSimilar` to find fresh songs you haven't heard
5. **Scores candidates by cosine similarity** — ranks them against your taste profile and returns the top N

---

## Project Structure

```
spotify-recommender/
├── auth/
│   ├── __init__.py
│   └── auth.py              # Spotify OAuth client
├── data/
│   ├── __init__.py
│   └── fetch.py             # Spotify + Last.fm data fetching
├── model/
│   ├── __init__.py
│   └── recommender.py       # Recommendation logic (cosine similarity)
├── api/
│   ├── __init__.py
│   └── routes.py            # FastAPI endpoints
├── notebooks/
│   └── recommender.ipynb    # Exploration, EDA, and visualizations
├── main.py                  # FastAPI app entry point
├── .env.example             # Environment variable template
├── .gitignore
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Music Data | Spotify Web API (via Spotipy) |
| Tag & Similarity Data | Last.fm API |
| ML / Similarity | scikit-learn (cosine similarity, MultiLabelBinarizer) |
| API Framework | FastAPI + Uvicorn |
| Data Processing | Pandas, NumPy |
| Visualization | Matplotlib, Seaborn |
| Environment | python-dotenv |

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/spotify-recommender.git
cd spotify-recommender
```

### 2. Install Dependencies

```bash
pip install spotipy fastapi uvicorn scikit-learn pandas numpy matplotlib seaborn requests python-dotenv
```

### 3. Set Up API Credentials

**Spotify:**
1. Go to [developer.spotify.com](https://developer.spotify.com) and create an app
2. Add `http://127.0.0.1:8080/callback` as a Redirect URI in your app settings
3. Copy your Client ID and Client Secret

**Last.fm:**
1. Go to [last.fm/api/account/create](https://www.last.fm/api/account/create) and create an app
2. Copy your API Key (available instantly, no approval needed)

### 4. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

```
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8080/callback
LASTFM_API_KEY=your_lastfm_api_key_here
```

### 5. Run the API

```bash
uvicorn main:app --reload
```

The API will be live at `http://127.0.0.1:8000`. Visit `http://127.0.0.1:8000/docs` for the interactive Swagger UI.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/recommend` | Recommend songs based on your full taste profile |
| `GET` | `/recommend/playlist/{playlist_id}` | Recommend songs based on a specific playlist |
| `GET` | `/top-artists` | Return your top artists for a given time range |
| `GET` | `/taste-profile` | Return your full combined track list |

### Example Requests

```bash
# get 10 recommendations based on your listening history
curl http://127.0.0.1:8000/recommend?n=10

# get recommendations based on a playlist
curl http://127.0.0.1:8000/recommend/playlist/37i9dQZF1DXcBWIGoYBM5M

# get your top artists from the last 4 weeks
curl http://127.0.0.1:8000/top-artists?time_range=short_term
```

### Example Response

```json
{
  "recommendations": [
    {
      "name": "Motion Sickness",
      "artist": "Phoebe Bridgers",
      "similarity_score": 0.8741
    },
    {
      "name": "Vanilla Twilight",
      "artist": "Owl City",
      "similarity_score": 0.8312
    }
  ]
}
```

---

## First-Time Authentication

The first time you run the app, Spotipy will prompt you to authenticate with Spotify:

1. A URL will be printed in your terminal
2. Paste it into your browser and log in to Spotify
3. After authorizing, copy the full redirected URL from your browser address bar
4. Paste it back into the terminal prompt

A `.cache` file will be created to store your token for future runs — this is already included in `.gitignore`.

---

## Notebook

The `notebooks/recommender.ipynb` file walks through the full pipeline interactively with visualizations including:

- Audio tag distribution across your taste profile
- Top 20 tags by track count
- Recommended songs ranked by similarity score

---

## Architecture Note

This project was originally designed to use Spotify's `audio-features` and `recommendations` endpoints. In November 2024, Spotify deprecated both endpoints for new development mode apps. The architecture was redesigned to use Last.fm as a replacement for both feature extraction (`track.getTopTags`) and candidate generation (`track.getSimilar`), while continuing to use Spotify exclusively for personalized listening history data.