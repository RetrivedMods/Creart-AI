from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from xhamster_api import Client
import os

app = FastAPI(title="XHamster Video API")

client = Client()

class VideoInfo(BaseModel):
    title: str
    likes: int
    url: str
    download_path: str

@app.get("/api", response_model=VideoInfo)
async def get_video_info(url: str = Query(..., description="XHamster video URL")):
    try:
        video = client.get_video(url)

        # Create downloads folder
        os.makedirs("downloads", exist_ok=True)

        # Generate filename
        filename = f"{video.title.replace(' ', '_')}.mp4"
        download_path = os.path.join("downloads", filename)

        # Download video
        video.download(downloader="threaded", quality="best", path=download_path)

        return VideoInfo(
            title=video.title,
            likes=video.likes,
            url=url,
            download_path=download_path
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
