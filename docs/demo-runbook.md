# AI Smart Traffic Management System — 3–5 Minute Demo Runbook

## Prerequisites
1. Python 3.11+
2. Node.js 22+
3. Optional local YOLO weight at `models/yolo/yolo26n.pt`
4. At least one readable traffic video in `data/videos/`

## One-command launch
Windows:
`scripts\\run_offline_demo.bat`

Linux/macOS:
`bash scripts/run_offline_demo.sh`

Dashboard:
`http://127.0.0.1:5173`

Backend:
`http://127.0.0.1:8000`

## Presentation sequence
### 0:00–0:30 — Overview
Show backend connection, database status, video source availability, and current traffic metrics.

### 0:30–1:45 — Live traffic
Select a local traffic video and start AI mode when the local YOLO model is available. Otherwise demonstrate the offline simulation mode. Show vehicle detection, counts, lane density, and signal state.

### 1:45–2:30 — Adaptive signal
Show the GREEN → YELLOW → ALL-RED → next GREEN safety sequence and the countdown. Explain that emergency priority never skips clearance phases.

### 2:30–3:15 — Analytics
Open Analytics. Show historical samples, average/peak traffic, busiest lane, lane averages, and five-minute offline forecast.

### 3:15–4:00 — Emergency
Open Emergency. Explain emergency-class support, confidence gating, direction mapping, and safe signal preemption. State clearly that a model trained with emergency classes is required for real ambulance/fire/police recognition.

### 4:00–4:30 — Diagnostics
Open Settings and show System Diagnostics. Finish on a healthy database/video check and the offline-ready architecture.

## Viva closing line
“The system is an offline-first intelligent traffic controller that combines local computer vision, lane-level traffic analytics, adaptive signal safety, emergency priority, historical analytics, and short-term forecasting in one reproducible B.Tech project.”
