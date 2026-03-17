#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Initial commit


# In[4]:


# Import essential libraries for authentication
# Spotipy is the go-to Python wrapper for the Spotify API
# Spotify uses OAuth 2.0, so we will import that
import spotipy
from spotipy.oauth2 import SpotifyOAuth


# In[6]:


# Authentication via spotipy.Spotify()
def get_spotify_client():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id="8d3cadb1129444249efdea66bb7be04d",
        client_secret="a1514cc6db2e408bac9f09ddec882854",
        redirect_uri="http://127.0.0.1:8888/callback",
        scope="user-library-read user-top-read user-read-recently-played"
    ))
    return sp


# In[ ]:




