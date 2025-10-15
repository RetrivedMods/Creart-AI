from fastapi import FastAPI, HTTPException, Query
import requests
from bs4 import BeautifulSoup

app = FastAPI(title="XHamster Video Info API (Scraper)")

@app.get("/api")
async def get_video_info(url: str = Query(..., description="XHamster video URL")):
    """
    Returns metadata + direct download URL for XHamster videos
    without saving to server.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch video page")

        html = resp.text
        soup = BeautifulSoup(html, "html.parser")

        # Get the video title
        title_tag = soup.find("meta", {"name": "title"})
        title = title_tag["content"] if title_tag else "Unknown"

        # Get the video duration
        duration_tag = soup.find("meta", {"itemprop": "duration"})
        duration = duration_tag["content"] if duration_tag else "Unknown"

        # Get the uploader
        uploader_tag = soup.find("a", {"class": "username"})
        uploader = uploader_tag.text.strip() if uploader_tag else "Unknown"

        # Get the direct video URL from the player configuration
        download_url = None
        scripts = soup.find_all("script")
        for s in scripts:
            if "flashvars" in s.text:
                text = s.text
                # Search for video URL in the JavaScript config
                import re
                match = re.search(r'video_url:\s*"([^"]+)"', text)
                if match:
                    download_url = match.group(1)
                    break

        if not download_url:
            raise HTTPException(status_code=404, detail="Download URL not found")

        return {
            "title": title,
            "uploader": uploader,
            "duration": duration,
            "original_url": url,
            "download_url": download_url
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
