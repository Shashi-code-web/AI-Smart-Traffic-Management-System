# AI Smart Traffic Management System

An offline-first B.Tech minor project for intelligent traffic monitoring and adaptive signal simulation.

## Current architecture

- **Frontend:** React + Vite
- **Backend:** FastAPI
- **AI:** Local YOLO vehicle detection + ByteTrack-compatible tracking
- **Traffic intelligence:** vehicle counting, lane density classification, adaptive signal decision
- **Database:** SQLite for local development; designed to remain usable without a database for demo mode
- **Presentation mode:** local/offline demo is the primary reliability path

## Pipeline

Traffic video → YOLO detection → tracking → vehicle counting → lane density → adaptive signal timing → FastAPI → dashboard

## Repository structure

```
frontend/                 React dashboard
backend/                  FastAPI application
ai/detection/             YOLO vehicle detection
ai/tracking/              ByteTrack adapter
ai/counting/              unique vehicle counting
ai/density/               LOW/MEDIUM/HIGH/CRITICAL classification
ai/signals/               adaptive signal decision logic
models/yolo/              local model weights (not committed)
data/videos/              presentation/demo videos
tests/                    project tests
docs/                     report and architecture material
scripts/                  Windows/Linux startup helpers
```

## Local setup

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The dashboard uses `http://127.0.0.1:8000` by default. Copy `backend/.env.example` to `.env` if configuration needs to be changed.

## AI model

The detector expects a local Ultralytics YOLO weight file configured by `MODEL_PATH` or the default project model path. Model weights are intentionally not stored in Git because they are large binary artifacts.

The system should still start in demo mode when the model file is unavailable. Live AI processing is enabled only after the local model is supplied and validated.

## Development status

### Completed
- Project foundation
- Offline-first configuration
- FastAPI health/system endpoints
- React dashboard shell
- YOLO vehicle detector adapter
- ByteTrack adapter
- Unique vehicle counting
- Density classifier
- Adaptive signal decision logic
- Traffic snapshot API

### Next
- Video ingestion and frame-processing service
- Lane/ROI configuration and line-crossing counts
- Live dashboard integration
- signal state machine with yellow/all-red safety phases
- analytics and persistence
- emergency vehicle priority
- automated tests and end-to-end demo verification
