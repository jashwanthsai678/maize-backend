import asyncio
import json
import os
import httpx
import time
import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AgriSense-Proxy")

load_dotenv()

app = FastAPI(title="AgriSense Orchestrator Proxy")

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Cloud VM Endpoint (VM 1) ---
# Should be http://34.14.178.187:8000/process_all
YOLO_YIELD_VM_URL = os.getenv("YOLO_API_URL") 

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

@app.post("/orchestrate")
async def orchestrate_advisory(
    image: UploadFile = File(...),
    district: str = Form(...),
    season: str = Form(...),
    crop_year: str = Form(...),
    area_ha: str = Form(...),
    growth_stage: str = Form(...),
    language: str = Form(...),
    weather_json: str = Form("{}")
):
    start_time = time.time()
    logger.info(f"--- New Request Received ---")
    logger.info(f"Target VM URL: {YOLO_YIELD_VM_URL}")
    
    try:
        # 1. Read Image
        image_bytes = await image.read()
        logger.info(f"Image received: {image.filename} ({len(image_bytes)} bytes)")

        # 2. Forward to Cloud VM
        # 120 second timeout to handle heavy processing
        async with httpx.AsyncClient(timeout=120.0) as client:
            files = {"image": (image.filename, image_bytes, image.content_type)}
            data = {
                "district": district,
                "season": season,
                "crop_year": crop_year,
                "area_ha": area_ha,
                "growth_stage": growth_stage,
                "language": language,
                "weather_json": weather_json
            }
            
            logger.info(f"Attempting to connect to VM...")
            try:
                resp = await client.post(YOLO_YIELD_VM_URL, data=data, files=files)
            except httpx.ConnectError:
                logger.error("CONNECTION ERROR: Cannot reach the Cloud VM IP. Check Firewall/Port 8000.")
                raise HTTPException(status_code=503, detail="Cloud VM unreachable. Check Firewall/Port 8000.")
            except httpx.TimeoutException:
                logger.error("TIMEOUT ERROR: The VM took too long (>120s) to process the request.")
                raise HTTPException(status_code=504, detail="VM Timeout. The processing took too long.")
            
            # Log the result
            duration = time.time() - start_time
            logger.info(f"VM responded in {duration:.2f}s with status {resp.status_code}")
            
            if resp.status_code != 200:
                logger.error(f"VM RETURNED ERROR: {resp.text}")
                return {
                    "error": "Cloud VM returned an error",
                    "status_code": resp.status_code,
                    "vm_message": resp.text
                }
            
            # Return result directly
            return resp.json()

    except Exception as e:
        logger.error(f"PROXY EXCEPTION: {str(e)}")
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Proxy Internal Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
