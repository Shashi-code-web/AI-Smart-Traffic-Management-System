# Viva Preparation — AI Smart Traffic Management System

## Core questions

### 1. What problem does the project solve?
It automates traffic monitoring and signal control using local computer vision, reducing dependence on manual observation and fixed signal timing.

### 2. Why YOLO?
YOLO provides real-time object detection suitable for identifying road vehicles frame by frame on a local machine.

### 3. Why ByteTrack?
Detection alone can count the same vehicle repeatedly. Persistent tracking IDs allow unique vehicle counting across frames.

### 4. How is lane density calculated?
Detected vehicles are assigned to normalized NORTH, EAST, SOUTH, and WEST regions. Counts are converted into LOW, MEDIUM, HIGH, or CRITICAL density levels.

### 5. How is signal timing adaptive?
The controller selects the highest-demand alternative lane and calculates green time between configured minimum and maximum values.

### 6. Why are YELLOW and ALL-RED required?
They provide a safe clearance interval so one direction never changes directly from GREEN to another direction's GREEN.

### 7. How does emergency priority work?
Supported emergency classes are confidence-gated. A valid emergency direction requests priority, but the controller still performs the required YELLOW and ALL-RED clearance before granting priority GREEN.

### 8. Does the standard YOLO model detect ambulances?
Not necessarily. Actual emergency recognition requires a local model trained with ambulance/fire/police/emergency classes. The application is designed to accept those local model labels.

### 9. Why SQLite?
It is local, lightweight, requires no external server, and is suitable for an offline-first academic demonstration.

### 10. How is historical analytics implemented?
Traffic snapshots are sampled at a configurable interval into SQLite, then summarized into averages, peaks, lane statistics, and signal-state counts.

### 11. How is prediction implemented?
Phase 6 uses an offline linear-trend forecasting baseline. It is intentionally simple, explainable, and reproducible for a B.Tech project.

### 12. What happens if the database or YOLO model is unavailable?
The system reports diagnostics truthfully. Traffic simulation can still run without the YOLO model, while analytics persistence is best-effort so a database write problem does not crash the traffic endpoint.

### 13. What makes the project offline-first?
Traffic videos, YOLO weights, inference, FastAPI, React, SQLite, analytics, and prediction all run locally. No cloud inference is required.

### 14. What are the major technologies?
Python, FastAPI, OpenCV, Ultralytics YOLO, ByteTrack, SQLAlchemy, SQLite, React, Vite, and JavaScript/CSS.

### 15. What are the project's main limitations?
Emergency detection quality depends on the local training classes/model, lane zones are normalized demo regions rather than calibrated road geometry, and prediction is a baseline model rather than a production forecasting service.
