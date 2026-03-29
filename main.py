from fastapi import FastAPI
from api.routes import router

app = FastAPI(title="Spotify Recommender")

app.include_router(router)