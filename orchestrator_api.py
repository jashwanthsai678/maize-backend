import asyncio
import json
import os
import httpx
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AgriSense Orchestrator")

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- VM Endpoints from Render Environment ---
YOLO_YIELD_VM_URL = os.getenv("YOLO_API_URL") 
LLM_VM_URL = os.getenv("LLM_API_URL")        

# Mount static files to serve the website
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
    try:
        # 1. Prepare data for the GCE VM
        # We forward EXACTLY what the VM's /process_all expects
        image_bytes = await image.read()
        
        async with httpx.AsyncClient(timeout=60.0) as client:
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
            
            # Proxy the request to the Cloud VM1
            # Using the URL from environment (e.g. http://34.14.178.187:8000/process_all)
            print(f"Proxying request to: {YOLO_YIELD_VM_URL}")
            resp = await client.post(YOLO_YIELD_VM_URL, data=data, files=files)
            
            if resp.status_code != 200:
                print(f"VM Error ({resp.status_code}): {resp.text}")
                raise HTTPException(status_code=resp.status_code, detail=f"Cloud VM Error: {resp.text}")
            
            # Return the VM's response directly to the frontend
            return resp.json()

    except Exception as e:
        print(f"Proxy Orchestration Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Use 8000 internally, Render will proxy via $PORT
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
