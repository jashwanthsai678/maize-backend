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
logger = logging.getLogger("AgriSense-Orchestrator")

load_dotenv()

app = FastAPI(title="AgriSense Multi-VM Orchestrator")

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Cloud VM Endpoints ---
# VM 1: YOLO + Yield
YOLO_YIELD_VM_URL = (os.getenv("YOLO_API_URL") or "http://34.14.178.187:8000/process_all").strip()
# VM 2: Qwen LLM Advisory (NEW IP PROVIDED BY USER)
LLM_VM_URL = (os.getenv("LLM_API_URL") or "http://34.10.208.65:8000/advisory").strip()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

@app.get("/test-vm")
async def test_vm_connection():
    """Diagnostic endpoint to see if Render can 'talk' to both VMs"""
    results = {}
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test VM 1
        try:
            resp1 = await client.get(YOLO_YIELD_VM_URL.replace("/process_all", ""))
            results["VM1 (YOLO/Yield)"] = {"status": "success", "code": resp1.status_code}
        except Exception as e:
            results["VM1 (YOLO/Yield)"] = {"status": "error", "detail": str(e)}
        
        # Test VM 2
        try:
            resp2 = await client.get(LLM_VM_URL.replace("/advisory", ""))
            results["VM2 (LLM Advisory)"] = {"status": "success", "code": resp2.status_code}
        except Exception as e:
            results["VM2 (LLM Advisory)"] = {"status": "error", "detail": str(e)}
            
    return results

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
    logger.info(f"--- Multi-VM Orchestration Start ---")
    
    try:
        image_bytes = await image.read()
        
        # STEP 1: Call VM 1 for Diagnosis and Yield
        logger.info(f"Step 1: Calling VM 1 at {YOLO_YIELD_VM_URL}")
        async with httpx.AsyncClient(timeout=60.0) as client:
            vm1_data = {
                "district": district,
                "season": season,
                "crop_year": crop_year,
                "area_ha": area_ha,
                "growth_stage": growth_stage,
                "language": language,
                "weather_json": weather_json
            }
            files = {"image": (image.filename, image_bytes, image.content_type)}
            
            vm1_resp = await client.post(YOLO_YIELD_VM_URL, data=vm1_data, files=files)
            if vm1_resp.status_code != 200:
                logger.error(f"VM 1 Error: {vm1_resp.text}")
                raise HTTPException(status_code=vm1_resp.status_code, detail=f"VM 1 (Diagnosis) Error: {vm1_resp.text}")
            
            vm1_result = vm1_resp.json()
            logger.info("Step 1 Complete: Diagnosis received.")

        # STEP 2: Call VM 2 for Qwen Advisory
        logger.info(f"Step 2: Calling VM 2 at {LLM_VM_URL}")
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
                 logger.warning(f"VM 2 failed, using fallback advisory.")
                 advisory_text = "Qwen Advisory is currently unavailable. Please refer to the diagnosis and yield results."
            else:
                 llm_result = llm_resp.json()
                 advisory_text = llm_result.get("advisory", "No advisory available.")
            logger.info("Step 2 Complete: Advisory received.")

        # Final Aggregation
        duration = time.time() - start_time
        logger.info(f"Orchestration completed in {duration:.2f}s")
        
        return {
            "detected_pest": vm1_result.get("detected_pest", "Unknown"),
            "detection_confidence": vm1_result.get("detection_confidence", 0.0),
            "yield_prediction": vm1_result.get("yield_prediction", 0.0),
            "severity": vm1_result.get("severity", "Moderate"),
            "advisory": advisory_text,
            "visual_diagnosis": {
                "annotated_image_base64": vm1_result.get("annotated_image_base64", ""),
            }
        }

    except Exception as e:
        logger.error(f"ORCHESTRATION EXCEPTION: {str(e)}")
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Orchestration Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
