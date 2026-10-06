# AI Smart Traffic Management System

An offline-first B.Tech minor project for intelligent traffic monitoring and adaptive signal control simulation.

## Current architecture

- **Frontend:** React + Vite
- **Backend:** FastAPI
- **AI:** Local Ultralytics YOLO vehicle detection + ByteTrack tracking
- **Traffic intelligence:** vehicle counting, lane density classification, adaptive signal timing with GREEN/YELLOW/ALL-RED safety phases
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

The dashboard uses `http://127.0.0.1:8000` by default. The backend accepts both `localhost:5173` and `127.0.0.1:5173`. Copy `backend/.env.example` to `backend/.env` if configuration needs to be changed.

## AI model

The detector expects a local Ultralytics YOLO weight file configured by `MODEL_PATH` or the default project model path. Model weights are intentionally not stored in Git because they are large binary artifacts.

The system should still start in demo mode when the model file is unavailable. Live AI processing is enabled only after the local model is supplied and validated.

## Development status

### Completed through Phase 3

Implemented in the repository:
- Local video validation for MP4/AVI/MOV/MKV/M4V
- Background video worker with MJPEG output
- Local YOLO model loading from `models/yolo/`
- ByteTrack persistence across consecutive frames
- Vehicle filtering for bicycle/car/motorcycle/bus/truck
- Unique tracked-vehicle counting and type counts
- Normalized four-way lane mapping
- Lane-wise density classification
- Adaptive signal demand decision
- Detection overlays, track IDs, lane regions, and signal information on the video stream
- Backend traffic snapshots sourced from the live AI pipeline
- Phase 3 unit tests and CI workflow

### Running real AI video

1. Install backend dependencies:
   `pip install -r backend/requirements.txt`
2. Place the local YOLO weight at:
   `models/yolo/yolo26n.pt`
3. Place a traffic video at:
   `data/videos/demo.mp4`
4. Start the FastAPI backend and React frontend.
5. Start **AI Video** from the dashboard.

Model weights are intentionally not committed to Git. The runtime uses Ultralytics YOLO tracking with ByteTrack persistence for consecutive video frames.

### Remaining phases

- Phase 5: signal state machine with yellow/all-red safety phases
- Phase 6: analytics, historical persistence, and prediction
- Phase 7: emergency vehicle priority
- Phase 8: reliability, validation, and end-to-end testing
- Phase 9: final presentation UI/demo hardening
- Phase 10: documentation, diagrams, PPT, viva preparation, and final verification


### Phase 5 status

Implemented in the repository:
- Local traffic video source discovery through `GET /api/video/sources`
- Dashboard source selection for any readable video under `data/videos/`
- Live backend connectivity indicator and manual refresh control
- 1.5-second polling for traffic, system, video session, and source state
- AI/demo mode shown explicitly in the dashboard
- Live MJPEG stream lifecycle with a fresh session query key
- Final AI traffic snapshot preserved after a short video reaches EOF
- Large-video inference resizing before YOLO processing
- Responsive live-monitor controls and video metadata display
- Phase 4 regression tests for inference resizing and completed AI session state

Phase 5 implements:
- Explicit GREEN → YELLOW → ALL-RED → GREEN transitions
- Minimum and maximum green-time enforcement
- Adaptive next-lane selection from current traffic demand
- Yellow clearance before all-red safety clearance
- All-red phase before the next direction becomes GREEN
- API exposure of signal state, remaining phase time, next direction, and transition reason
- Dashboard visualization of GREEN, YELLOW, and ALL-RED states
- Deterministic unit tests for transition timing and conflict prevention
- Dedicated Phase 5 CI workflow
