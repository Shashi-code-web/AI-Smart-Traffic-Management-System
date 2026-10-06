from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_phase9_offline_launchers_exist_and_reference_local_services():
    shell = (ROOT / "scripts" / "run_offline_demo.sh").read_text()
    windows = (ROOT / "scripts" / "run_offline_demo.bat").read_text()

    assert "127.0.0.1:8000" in shell
    assert "127.0.0.1:5173" in shell
    assert "uvicorn backend.app.main:app" in shell

    assert "127.0.0.1:8000" in windows
    assert "127.0.0.1:5173" in windows
    assert "uvicorn backend.app.main:app" in windows


def test_phase10_documentation_package_exists():
    required = [
        "docs/demo-runbook.md",
        "docs/system-architecture.mmd",
        "docs/viva-prep.md",
        "docs/final-verification.md",
        "scripts/final_verification.py",
    ]
    for relative in required:
        assert (ROOT / relative).exists(), relative


def test_phase9_frontend_contains_final_user_flows():
    app = (ROOT / "frontend" / "src" / "App.jsx").read_text()
    assert "Traffic History" in app
    assert "Emergency Priority" in app
    assert "System Diagnostics" in app
    assert "Offline Demo Workflow" in app
