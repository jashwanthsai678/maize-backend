import asyncio
import json
import os
import httpx
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv
from blended_predictor import predict_blended_yield

load_dotenv()

app = FastAPI(title="Advisory Orchestrator API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Configuration ---
# Path to your VM instance endpoint for the LLM
LLM_API_URL = os.getenv("LLM_API_URL", "http://34.69.210.248:8000/advisory")

# Microservice endpoints
YOLO_API_URL = os.getenv("YOLO_API_URL", "http://127.0.0.1:8002/predict")
YIELD_API_URL = os.getenv("YIELD_API_URL", "http://127.0.0.1:8003/predict")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

# Mount static files (css, js)
app.mount("/static", StaticFiles(directory="static"), name="static")


class YieldMetadata(BaseModel):
    district_std: str
    crop_year: int
    season: str
    area_ha: float
    T2M: list[float]
    T2M_MAX: list[float]
    T2M_MIN: list[float]
    PRECTOTCORR: list[float]
    RH2M: list[float]
    ALLSKY_SFC_SW_DWN: list[float]
    # Extra user context for LLM
    crop_type: str = "maize"
    growth_stage: str = "vegetative"
    language: str = "english"


async def run_yolo_diagnosis(image_bytes: bytes) -> dict:
    """Call the YOLO microservice."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            files = {"image": ("image.jpg", image_bytes, "image/jpeg")}
            response = await client.post(YOLO_API_URL, files=files)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"YOLO API Error: {e}")
        return {
            "diagnosis": "Error connecting to YOLO service",
            "confidence": 0.0,
            "severity": "unknown",
            "annotated_image_base64": ""
        }

async def run_yield_prediction(payload: dict) -> dict:
    """Call the Yield prediction logic directly (consolidated)."""
    try:
        # Instead of an external HTTP call, we run the logic in-process
        # Using to_thread if it's CPU intensive, or just calling it if it's fast enough.
        # Since it's joblib/pandas, it's blocking, so we use to_thread.
        preds = await asyncio.to_thread(predict_blended_yield, payload)
        return preds
    except Exception as e:
        print(f"Yield Prediction Error: {e}")
        return {
            "pred_best_rmse_blend": "Error computing yield"
        }

async def get_llm_advisory(payload: dict) -> dict:
    """Call the LLM API on the cloud VM."""
    print(f"\n--- LLM ADVISORY REQUEST ---")
    print(f"URL: {LLM_API_URL}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(LLM_API_URL, json=payload)
            print(f"Response Status: {response.status_code}")
            response.raise_for_status()
            res_json = response.json()
            print(f"Response JSON: {json.dumps(res_json, indent=2)}")
            return res_json
    except httpx.ConnectError:
        err_msg = f"Connection Error: Could not reach {LLM_API_URL}. Check if the VM is running and firewall port 8000 is open."
        print(f"!!! {err_msg}")
        return {"advisory": err_msg, "error": "connection_failed"}
    except httpx.HTTPStatusError as e:
        err_msg = f"HTTP Error {e.response.status_code}: {e.response.text}. Check if the endpoint path is correct."
        print(f"!!! {err_msg}")
        return {"advisory": err_msg, "error": "http_error"}
    except Exception as e:
        err_msg = str(e)
        print(f"!!! LLM Connectivity Error: {err_msg}")
        # Provide a realistic fallback for the demo if the VM is down
        return {
            "advisory": "### 💡 Expert Advisory (Fallback Mode)\n\n"
                        "We are currently experiencing a connection issue with the remote AI Advisor. "
                        "However, based on the **YOLO Diagnosis** and **Yield Data** processed locally:\n\n"
                        "- **Immediate Action**: Scrutinize the affected area and remove heavily infested leaves.\n"
                        "- **Preventive**: Maintain soil health and monitor neighboring plots.\n"
                        "- **Next Step**: Please check your VM firewall settings (Port 8000) to restore live AI advice.",
            "error": err_msg
        }


@app.post("/orchestrate")
async def orchestrate_advisory(
    image: UploadFile = File(...),
    metadata: str = Form(...)
):
    try:
        # 1. Parse Metadata
        try:
            meta_dict = json.loads(metadata)
            meta = YieldMetadata(**meta_dict)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=f"Invalid metadata format: {e.errors()}")
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Metadata must be valid JSON")

        # Read image bytes
        image_bytes = await image.read()

        # 2 & 3. Run YOLO and Yield Model in Parallel
        yolo_task = asyncio.create_task(run_yolo_diagnosis(image_bytes))
        yield_task = asyncio.create_task(run_yield_prediction(meta.model_dump()))
        
        # Await both to finish concurrently
        yolo_result, yield_result = await asyncio.gather(yolo_task, yield_task, return_exceptions=True)
        
        # Check for errors in parallel execution
        if isinstance(yolo_result, Exception):
            print(f"YOLO Error: {yolo_result}")
            yolo_result = {"diagnosis": "Error running YOLO", "confidence": 0, "severity": "unknown", "annotated_image_base64": ""}
            
        if isinstance(yield_result, Exception):
            print(f"Yield Model Error: {yield_result}")
            yield_result = {"pred_best_rmse_blend": "Error computing yield"}

        # Extract Yield Baseline
        expected_yield_val = yield_result.get("pred_best_rmse_blend", "Unknown")
        expected_yield_str = f"{expected_yield_val:.2f} t/ha" if isinstance(expected_yield_val, float) else expected_yield_val

        # 4. Prepare payload for LLM Interpretation
        llm_input = {
            "crop": meta.crop_type,
            "growth_stage": meta.growth_stage,
            "district": meta.district_std,
            "season": meta.season,
            "diagnosis": yolo_result.get("diagnosis", "unknown"),
            "confidence": yolo_result.get("confidence", 0),
            "severity": yolo_result.get("severity", "unknown"),
            "expected_yield": expected_yield_str,
            "language": meta.language
        }
        
        # Run LLM call
        llm_result = await get_llm_advisory(llm_input)
        
        # 5. Final Aggregation
        return {
            "status": "success",
            "visual_diagnosis": yolo_result,
            "environmental_context": {
                "district": meta.district_std,
                "season": meta.season,
                "expected_yield_baseline": expected_yield_str,
                "is_error": isinstance(yield_result, Exception) or "Error" in str(expected_yield_val)
            },
            "expert_advisory": llm_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
