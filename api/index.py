# main.py

import httpx
from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional
import base64, io

CREART_AI_BASE_URL = "https://api.creartai.com/api/v1"

app = FastAPI(
    title="My Custom Image Generation API",
    description="A Python wrapper for the Creart AI text-to-image and image-to-image APIs.",
    version="1.0.0"
)

# ----------------------------
# Request Models
# ----------------------------

class Text2ImageRequest(BaseModel):
    prompt: str = Field(..., example="a beautiful landscape, cinematic lighting, 8k")
    negative_prompt: str = ""
    aspect_ratio: str = Field(default="1x1", example="4x5")
    guidance_scale: float = Field(default=9.5, example=8.0)
    seed: Optional[int] = None

class Image2ImageRequest(Text2ImageRequest):
    input_image_base64: str = Field(..., description="The source image encoded in Base64 format.")

# ----------------------------
# HTML Form for Browser
# ----------------------------

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head><title>Creart AI Image Generator</title></head>
        <body style="font-family:sans-serif; text-align:center;">
            <h1>🖼️ Creart AI Image Generator</h1>
            <form action="/generate-browser" method="get">
                <input type="text" name="prompt" placeholder="Enter your prompt" size="50" required />
                <button type="submit">Generate</button>
            </form>
        </body>
    </html>
    """

# ----------------------------
# POST Endpoints (Original)
# ----------------------------

@app.post("/api/text-to-image")
async def generate_text_to_image(request_data: Text2ImageRequest):
    api_url = f"{CREART_AI_BASE_URL}/text2image"
    payload = { 
        "prompt": request_data.prompt,
        "input_image_type": "text2image",
        "input_image_base64": "",
        "negative_prompt": request_data.negative_prompt,
        "aspect_ratio": request_data.aspect_ratio,
        "guidance_scale": request_data.guidance_scale,
        "seed": request_data.seed,
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(api_url, data=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Error from external API: {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.post("/api/image-to-image")
async def generate_image_to_image(request_data: Image2ImageRequest):
    api_url = f"{CREART_AI_BASE_URL}/image2image"
    payload = {
        "prompt": request_data.prompt,
        "input_image_type": "image2image",
        "input_image_base64": request_data.input_image_base64,
        "negative_prompt": request_data.negative_prompt,
        "aspect_ratio": request_data.aspect_ratio,
        "guidance_scale": request_data.guidance_scale,
        "seed": request_data.seed,
    }
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(api_url, data=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Error from external API: {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

# ----------------------------
# GET Endpoints for Browser
# ----------------------------

@app.get("/generate-browser")
async def generate_text_to_image_browser(prompt: str = Form(...)):
    api_url = f"{CREART_AI_BASE_URL}/text2image"
    payload = {
        "prompt": prompt,
        "input_image_type": "text2image",
        "input_image_base64": "",
        "negative_prompt": "",
        "aspect_ratio": "1x1",
        "guidance_scale": 7.5,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(api_url, data=payload)
            response.raise_for_status()
            data = response.json()

            if "data" in data and "image_base64" in data["data"]:
                image_bytes = base64.b64decode(data["data"]["image_base64"])
                return StreamingResponse(io.BytesIO(image_bytes), media_type="image/png")
            else:
                return data

        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Error from external API: {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

# Optional: direct GET with query string
@app.get("/api/text-to-image-browser")
async def text_to_image_direct(prompt: str):
    """Direct GET access via URL for Chrome."""
    api_url = f"{CREART_AI_BASE_URL}/text2image"
    payload = {
        "prompt": prompt,
        "input_image_type": "text2image",
        "input_image_base64": "",
        "negative_prompt": "",
        "aspect_ratio": "1x1",
        "guidance_scale": 7.5,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(api_url, data=payload)
        response.raise_for_status()
        data = response.json()
        image_bytes = base64.b64decode(data["data"]["image_base64"])
        return StreamingResponse(io.BytesIO(image_bytes), media_type="image/png")
