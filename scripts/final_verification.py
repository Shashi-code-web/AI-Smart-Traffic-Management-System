from __future__ import annotations

import sys

from fastapi.testclient import TestClient

from backend.app.main import app


def main() -> int:
    client = TestClient(app)

    checks = [
        ("root", lambda: client.get("/")),
        ("health", lambda: client.get("/health")),
        ("system status", lambda: client.get("/api/system/status")),
        ("diagnostics", lambda: client.get("/api/system/diagnostics")),
        ("traffic snapshot", lambda: client.get("/api/traffic/snapshot")),
        ("analytics summary", lambda: client.get("/api/analytics/summary")),
        ("analytics history", lambda: client.get("/api/analytics/history?limit=5")),
        ("analytics prediction", lambda: client.get("/api/analytics/predict?horizon=3")),
        ("video sources", lambda: client.get("/api/video/sources")),
        ("video session", lambda: client.get("/api/video/session")),
    ]

    failures = []
    for name, request in checks:
        response = request()
        if response.status_code != 200:
            failures.append(f"{name}: HTTP {response.status_code} {response.text}")

    if failures:
        print("FINAL VERIFICATION FAILED")
        for failure in failures:
            print(" -", failure)
        return 1

    root = client.get("/").json()
    if root.get("phase") != 10:
        print(f"FINAL VERIFICATION FAILED: expected phase 10, got {root.get('phase')}")
        return 1

    health = client.get("/health").json()
    if health.get("version") != "1.0.0":
        print(f"FINAL VERIFICATION FAILED: expected version 1.0.0, got {health.get('version')}")
        return 1

    diagnostics = client.get("/api/system/diagnostics").json()
    unexpected = [
        check for check in diagnostics["checks"]
        if not check["ok"] and check["name"] != "local_model"
    ]
    if unexpected:
        print("FINAL VERIFICATION FAILED: unexpected diagnostics failure")
        for check in unexpected:
            print(" -", check)
        return 1

    print("FINAL VERIFICATION PASSED")
    print("Application:", root["name"])
    print("Version:", health["version"])
    print("Phase:", root["phase"])
    print("Diagnostics:", diagnostics)
    return 0


if __name__ == "__main__":
    sys.exit(main())
