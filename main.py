from fastapi import FastAPI, HTTPException, Query
from xhamster_api import Client
import os

app = FastAPI()
client = Client()

@app.get("/api")
async def get_video(url: str = Query(...)):
    try:
        video = client.get_video(url)

        # Safe attributes
        title = getattr(video, "title", "Unknown")
        views = getattr(video, "views", "Unknown")
        duration = getattr(video, "duration", "Unknown")

        # Optional: Download
        os.makedirs("downloads", exist_ok=True)
        filename = f"{title.replace(' ', '_')}.mp4"
        download_path = os.path.join("downloads", filename)
        video.download(downloader="threaded", quality="best", path=download_path)

        return {
            "title": title,
            "views": views,
            "duration": duration,
            "url": url,
            "download_path": download_path
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
