# Water Quality Fingerprinting using IoT & Explainable AI

Pollution source attribution system — Phase 1 (ML + XAI + Dashboard, software-only using
CPCB / Tamil Nadu PCB public datasets) and Phase 2 (ESP32/LoRa live sensor integration).

## Structure
- `ml-pipeline/` — data ingestion, preprocessing, fingerprint feature engineering, RF/XGBoost training, SHAP explainability
- `backend/` — FastAPI service exposing prediction + explanation endpoints
- `frontend/` — React.js dashboard
- `iot-firmware/` — Phase 2 ESP32 sensor node code (placeholder for now)
- `docs/` — paper drafts, architecture notes

## Quick Start

### 1. ML Pipeline
```bash
cd ml-pipeline
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run_pipeline.py
```

### 2. Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm start
```

Backend runs at `http://localhost:8000`, frontend at `http://localhost:3000`.

## Phase 1 Roadmap
1. Download CPCB / TN PCB dataset → `ml-pipeline/data/raw/`
2. Run preprocessing + fingerprint feature engineering
3. Train RF + XGBoost, evaluate
4. Run SHAP explainability
5. Serve via FastAPI, visualize via React dashboard
6. Write and submit paper (`docs/paper/`)

## Phase 2 Roadmap
1. Flash `iot-firmware/esp32_sensor_node/main.ino` to ESP32
2. Implement a new ingestion source in `ml-pipeline/src/ingestion/` implementing `base_source.py`
3. Enable `backend/app/api/routes_stream.py` for live data
4. Validate end-to-end with field data
