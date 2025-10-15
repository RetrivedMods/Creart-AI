from fastapi import FastAPI, HTTPException, Query
from xhamster_api import Client

app = FastAPI(title="XHamster Video Info API")
client = Client()

@app.get("/api")
async def get_video_info(url: str = Query(..., description="XHamster video URL")):
    """
    Returns metadata + direct video URL (best quality) for XHamster videos.
    Does NOT download on server.
    """
    try:
        video = client.get_video(url)

        # Safe metadata
        title = getattr(video, "title", "Unknown")
        views = getattr(video, "views", "Unknown")
        duration = getattr(video, "duration", "Unknown")
        uploader = getattr(video, "uploader", "Unknown")

        # Get the best direct download URL
        download_url = None
        if hasattr(video, "videos") and video.videos:
            # Usually videos is a dict with quality keys
            # Pick the highest quality available
            qualities = sorted(video.videos.keys(), reverse=True)
            download_url = video.videos[qualities[0]]

        return {
            "title": title,
            "uploader": uploader,
            "views": views,
            "duration": duration,
            "original_url": url,
            "download_url": download_url
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
