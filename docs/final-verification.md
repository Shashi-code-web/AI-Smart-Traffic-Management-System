# Final Verification Plan

## Automated checks
- Phase 3 regression suite
- Phase 4 dashboard build and backend regression
- Phase 5 signal safety tests
- Phase 6 analytics/prediction tests
- Phase 7 emergency priority tests
- Phase 8 diagnostics/reliability tests
- Phase 9 frontend build and offline launcher checks
- Phase 10 final API smoke verification

## Final smoke endpoints
- `GET /`
- `GET /health`
- `GET /api/system/status`
- `GET /api/system/diagnostics`
- `GET /api/traffic/snapshot`
- `GET /api/analytics/summary`
- `GET /api/analytics/history`
- `GET /api/analytics/predict`
- `GET /api/video/sources`
- `GET /api/video/session`

## Acceptance criteria
1. No failing backend regression tests.
2. Frontend build succeeds.
3. No phase regression from the latest approved phase.
4. Database readiness is truthful.
5. Local video paths cannot escape `data/videos/`.
6. Signal controller never skips YELLOW/ALL-RED.
7. Emergency priority remains confidence-gated and safety-cleared.
8. Dashboard remains usable with and without a local YOLO weight.
9. Offline demo launcher starts the local backend and dashboard.
10. Final smoke script reports PASS.
