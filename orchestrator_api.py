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
    crop_year: int = Form(...),
    area_ha: float = Form(...),
    growth_stage: str = Form(...),
    language: str = Form(...),
    weather_json: str = Form("{}") # Received from app.js
):
    try:
        # 1. Read Image
        image_bytes = await image.read()
        
        # Parse weather data (though not used directly in this specific VM1 call, we have it)
        try:
            weather_data = json.loads(weather_json)
        except:
            weather_data = {}

        # 2. Call VM 1 (YOLO + Yield)
        # We send the form data and image to the processing VM
        async with httpx.AsyncClient(timeout=40.0) as client:
            vm1_files = {"image": (image.filename, image_bytes, image.content_type)}
            vm1_data = {
                "district": district,
                "season": season,
                "crop_year": str(crop_year),
                "area_ha": str(area_ha),
                "growth_stage": growth_stage,
                "language": language,
                "weather_json": weather_json
            }
            
            # Requesting both Pest Detection and Yield from VM 1
            vm1_resp = await client.post(YOLO_YIELD_VM_URL, data=vm1_data, files=vm1_files)
            if vm1_resp.status_code != 200:
                raise HTTPException(status_code=vm1_resp.status_code, detail=f"VM 1 Error: {vm1_resp.text}")
            
            vm1_result = vm1_resp.json()

        # 3. Call VM 2 (Qwen LLM)
        # Now we take the results from VM 1 and ask Qwen for an advisory
        async with httpx.AsyncClient(timeout=60.0) as client:
            llm_payload = {
                "crop": "Maize",
                "growth_stage": growth_stage,
                "district": district,
                "season": season,
                "diagnosis": vm1_result.get("detected_pest", "Healthy"),
                "confidence": vm1_result.get("detection_confidence", 0.0),
                "severity": vm1_result.get("severity", "Moderate"),
                "expected_yield": f"{vm1_result.get('yield_prediction', 0):.2f} t/ha",
                "language": language
            }
            
            llm_resp = await client.post(LLM_VM_URL, json=llm_payload)
            if llm_resp.status_code != 200:
                 # Fallback advisory if LLM is down
                 advisory_text = "Expert advisory is currently unavailable. Please check the diagnosis and yield results above."
            else:
                 llm_result = llm_resp.json()
                 advisory_text = llm_result.get("advisory", "No advisory available.")

        # 4. Final Aggregated Response to Website
        return {
            "detected_pest": vm1_result.get("detected_pest", "Unknown"),
            "detection_confidence": vm1_result.get("detection_confidence", 0.0),
            "yield_prediction": vm1_result.get("yield_prediction", 0.0),
            "severity": vm1_result.get("severity", "Moderate"),
            "advisory": advisory_text,
            "visual_diagnosis": {
                "annotated_image_base64": vm1_result.get("annotated_image_base64", ""),
                "diagnosis": vm1_result.get("detected_pest", "Unknown"),
                "confidence": vm1_result.get("detection_confidence", 0.0)
            }
        }

    except Exception as e:
        print(f"Orchestration Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Use 8000 internally, Render will proxy via $PORT
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
