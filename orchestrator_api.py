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
    logger.info(f"--- Direct Request to LLM VM at {LLM_VM_URL} ---")
    
    try:
        image_bytes = await image.read()
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            # We send JSON to the /advisory endpoint as expected
            llm_payload = {
                "crop": "Maize",
                "growth_stage": growth_stage,
                "district": district,
                "season": season,
                "diagnosis": "Direct Advisory Request",
                "confidence": 1.0,
                "severity": "Info",
                "expected_yield": "N/A",
                "language": language
            }
            
            try:
                resp = await client.post(LLM_VM_URL, json=llm_payload)
            except httpx.ConnectError:
                raise HTTPException(status_code=503, detail="Cloud VM unreachable. Check Firewall/Port 8000 on 34.10.208.65.")
            except httpx.TimeoutException:
                raise HTTPException(status_code=504, detail="VM Timeout. The processing took too long.")
            
            if resp.status_code == 422:
                # If JSON fails, the user might have updated the endpoint to accept form data (image+metadata). Let's try it as fallback.
                logger.warning("VM returned 422 for JSON. Falling back to Multipart Form Data.")
                vm_data = {
                    "district": district,
                    "season": season,
                    "crop_year": str(crop_year),
                    "area_ha": str(area_ha),
                    "growth_stage": growth_stage,
                    "language": language,
                    "weather_json": weather_json
                }
                files = {"image": (image.filename, image_bytes, image.content_type)}
                resp = await client.post(LLM_VM_URL, data=vm_data, files=files)
                
            if resp.status_code != 200:
                logger.error(f"VM Error ({resp.status_code}): {resp.text}")
                raise HTTPException(status_code=resp.status_code, detail=f"VM Error: {resp.text}")
            
            llm_result = resp.json()
            
            # If the VM returns the full struct (detected_pest, yield_prediction), use it. Else fallback to defaults.
            return {
                "detected_pest": llm_result.get("detected_pest", "Direct Request"),
                "detection_confidence": llm_result.get("detection_confidence", 100.0),
                "yield_prediction": llm_result.get("yield_prediction", 0.0),
                "severity": llm_result.get("severity", "Moderate"),
                "advisory": llm_result.get("advisory", str(llm_result)),
                "visual_diagnosis": {
                    "annotated_image_base64": llm_result.get("annotated_image_base64", ""),
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
