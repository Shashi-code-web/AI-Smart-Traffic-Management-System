# AI Smart Traffic Management System — Final Project Report

## 1. Abstract
The AI Smart Traffic Management System is an offline-first intelligent traffic monitoring and adaptive signal-control platform developed as a B.Tech minor project. It combines local YOLO object detection, ByteTrack tracking, lane-wise density estimation, adaptive signal safety, emergency-vehicle priority, historical traffic analytics, short-term forecasting, a FastAPI backend, a React dashboard, and SQLite persistence.

The project is designed for reproducible academic demonstration on a normal laptop without cloud inference.

## 2. Objectives
- Detect and track road vehicles from local traffic videos.
- Count unique vehicles and classify traffic density by lane.
- Select adaptive signal timing using current traffic demand.
- Enforce GREEN → YELLOW → ALL-RED safety transitions.
- Provide emergency-vehicle priority without bypassing safety clearance.
- Persist traffic history and provide analytics and short-term forecasting.
- Provide a responsive dashboard and a 3–5 minute offline demo workflow.
- Provide automated regression, diagnostics, and final verification.

## 3. Technology Stack
### Frontend
React, Vite, JavaScript, CSS, lucide-react.

### Backend
Python, FastAPI, Pydantic, SQLAlchemy, SQLite, OpenCV.

### AI
Ultralytics YOLO, ByteTrack persistence, local model inference.

### Verification
Pytest, GitHub Actions, final API smoke verification.

## 4. System Pipeline
Traffic Video → YOLO → ByteTrack → Vehicle Counting → Lane Mapping → Density Estimation → Adaptive Signal Controller → FastAPI → React Dashboard.

Emergency detection runs beside vehicle detection and requests safe priority through the same signal state machine.

## 5. Functional Modules
### Vehicle detection
Supported base vehicle classes include bicycle, car, motorcycle, bus, and truck.

### Tracking and counting
Persistent track IDs are used to prevent repeated counting of the same vehicle.

### Lane and density analysis
Four normalized regions represent NORTH, EAST, SOUTH, and WEST. Counts are classified into LOW, MEDIUM, HIGH, or CRITICAL.

### Adaptive signals
Green time is bounded by configurable minimum and maximum values. Phase transitions explicitly use YELLOW and ALL-RED safety intervals.

### Emergency priority
Emergency-class labels can be supplied by a local YOLO model. Priority is confidence-gated, direction-aware, and safety-cleared.

### Analytics
Traffic samples are throttled before local SQLite persistence. Summary APIs provide averages, peaks, lane statistics, and signal-state distribution. Forecasting uses an explainable offline linear-trend baseline.

### Dashboard
The dashboard exposes Overview, Live Monitor, Analytics, Emergency, and Settings/Diagnostics views.

## 6. Offline Design
The project does not require cloud inference or an external database server. Traffic videos, model weights, inference, analytics, and the dashboard operate locally. When a local YOLO model is absent, simulation mode remains available for presentation.

## 7. Safety and Reliability
- Unsafe video paths are rejected.
- Unsupported video extensions are rejected.
- Signal configuration validation fails fast.
- Database connections use pre-ping.
- SQLite uses WAL mode.
- Analytics writes are best-effort.
- Final diagnostics expose database, video-directory, and local-model readiness.
- Emergency priority does not skip the YELLOW or ALL-RED phases.

## 8. Phase Completion
- Phase 1 — foundation
- Phase 2 — AI traffic intelligence
- Phase 3 — real video + YOLO/ByteTrack
- Phase 4 — live dashboard
- Phase 5 — adaptive signal safety
- Phase 6 — analytics + prediction
- Phase 7 — emergency priority
- Phase 8 — reliability + validation
- Phase 9 — UI/UX + offline demo
- Phase 10 — documentation + final verification

## 9. Limitations
1. Emergency recognition quality depends on a local YOLO model trained with emergency classes.
2. Lane boundaries are normalized demonstration regions and should be calibrated for deployment at a real intersection.
3. Forecasting is a baseline linear-trend model, not a production traffic forecasting model.
4. The project is intended as an academic prototype rather than a certified traffic-control product.

## 10. Future Work
- Camera calibration and perspective-aware lanes.
- Multi-camera fusion.
- More advanced forecasting models.
- Weather and road-condition context.
- Vehicle speed estimation.
- Real traffic-controller hardware integration.
- Certified safety validation before any real-world deployment.

## 11. Final Demo
Follow `docs/demo-runbook.md` for the 3–5 minute presentation sequence.
