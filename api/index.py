# main.py
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from xhamster_api import Client
import os

app = FastAPI(title="XHamster Video Info API")

# Initialize XHamster Client once
client = Client()

# Response model
class VideoInfo(BaseModel):
    title: str
    likes: int
    url: str
    download_path: str

@app.get("/api", response_model=VideoInfo)
async def get_video_info(url: str = Query(..., description="URL of the xHamster video")):
    try:
        # Fetch video
        video = client.get_video(url)
        
        # Optional: Download video (uncomment if needed)
        filename = f"{video.title.replace(' ', '_')}.mp4"
        download_path = os.path.join("downloads", filename)
        os.makedirs("downloads", exist_ok=True)
        
        video.download(downloader="threaded", quality="best", path=download_path)
        
        # Return video info
        return VideoInfo(
            title=video.title,
            likes=video.likes,
            url=url,
            download_path=download_path
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
