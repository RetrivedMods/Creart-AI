from fastapi import FastAPI, HTTPException, Query
from xhamster_api import Client

app = FastAPI(title="XHamster Video Info API")
client = Client()

@app.get("/api")
async def get_video_info(url: str = Query(..., description="XHamster video URL")):
    """
    Fetches metadata of a XHamster video and returns info + direct download link.
    Does NOT download video to the server.
    """
    try:
        video = client.get_video(url)

        # Safe attributes
        title = getattr(video, "title", "Unknown")
        views = getattr(video, "views", "Unknown")
        duration = getattr(video, "duration", "Unknown")
        uploader = getattr(video, "uploader", "Unknown")

        # Get direct video URLs (usually multiple qualities)
        video_urls = {}
        if hasattr(video, "videos") and isinstance(video.videos, dict):
            for quality, v_url in video.videos.items():
                video_urls[quality] = v_url

        return {
            "title": title,
            "uploader": uploader,
            "views": views,
            "duration": duration,
            "original_url": url,
            "video_urls": video_urls  # direct URLs, no server storage
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
