import asyncio
import os
import httpx
import time
import logging
import json
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
    logger.info("--- Starting VM1 -> VM2 Pipeline ---")
    
    try:
        image_bytes = await image.read()
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            
            # -------------------------------------------------------------------
            # STEP 1: BYPASS VM 1 (Because it is currently offline)
            # -------------------------------------------------------------------
            logger.info("Bypassing VM 1 as requested by user. Proceeding directly to VM 2.")
            
            # Since VM 1 is bypassed, we provide default/placeholder values that VM 2 expects
            detected_pest = "Pending Visual Diagnosis"
            detection_confidence = 100.0
            yield_prediction = 0.0
            severity = "Analysis Bypassed"
            annotated_image_base64 = ""

            # -------------------------------------------------------------------
            # STEP 2: VM 2 (LLM Advisory)
            # -------------------------------------------------------------------
            logger.info(f"Sending request to VM 2: {LLM_VM_URL}")
            llm_payload = {
                "crop": "Maize",
                "growth_stage": growth_stage,
                "district": district,
                "season": season,
                "diagnosis": str(detected_pest),
                "confidence": float(detection_confidence),
                "severity": str(severity),
                "expected_yield": str(yield_prediction),
                "language": str(language)
            }
            
            try:
                resp2 = await client.post(LLM_VM_URL, json=llm_payload)
            except Exception as e:
                logger.error(f"Error connecting to VM 2: {e}")
                raise HTTPException(status_code=503, detail="VM 2 unreachable or timed out.")
            
            if resp2.status_code != 200:
                logger.error(f"VM 2 Error ({resp2.status_code}): {resp2.text}")
                raise HTTPException(status_code=resp2.status_code, detail=f"VM 2 Error: {resp2.text}")
                
            vm2_result = resp2.json()
            logger.info("Successfully received response from VM 2.")
            
            # Combine the results for the frontend presentation
            return {
                "detected_pest": detected_pest,
                "detection_confidence": detection_confidence,
                "yield_prediction": yield_prediction,
                "severity": severity,
                "advisory": vm2_result.get("advisory", str(vm2_result)),
                "visual_diagnosis": {
                    "annotated_image_base64": annotated_image_base64
                }
            }

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"ORCHESTRATION EXCEPTION: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Orchestration Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
