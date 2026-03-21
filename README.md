# AgriSense AI | Intelligent Maize Advisory System

This project is an ultra-lightweight web interface and orchestrator for the Maize Advisory System. It coordinates between three cloud-hosted microservices to provide real-time pest diagnosis and yield prediction.

## 🚀 Key Features
- **Visual Diagnosis**: Integrates with a Cloud YOLO model for real-time pest identification.
- **Yield Projection**: Uses cloud-hosted scikit-learn models for yield estimation based on environmental context.
- **Expert Advisory**: Provides AI-powered agronomist advice via a remote LLM.
- **Optimized for Render**: Extremely small footprint, offloading all heavy processing to the cloud.

## 🛠️ Architecture
The `orchestrator_api.py` coordinates requests from the web UI to:
1. **Cloud YOLO Service**: For image analysis.
2. **Cloud Yield Service**: For tabular data prediction.
3. **Cloud LLM (Advisory)**: For final expert interpretation.

## 📦 Deployment on Render

### 1. Configure Environment Variables
In the Render dashboard, project environment settings, add:
- `YOLO_API_URL`: Your cloud YOLO endpoint.
- `YIELD_API_URL`: Your cloud Yield endpoint.
- `LLM_API_URL`: Your cloud LLM endpoint.

### 2. Verify Config
- Render will automatically use the `Procfile` and `requirements.txt`.
- Pinning `scikit-learn==1.6.1` and `Python 3.11` ensures compatibility with the model-hosting cloud.

## 📂 Project Structure
```
.
├── static/
│   ├── index.html (Main UI)
│   ├── app.js
│   └── styles.css
├── orchestrator_api.py (Coordinator API)
├── Procfile (Render config)
├── runtime.txt
└── requirements.txt
```