from fastapi.testclient import TestClient

from agent_api.main import app

client = TestClient(app)


def test_healthz() -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "service" in payload


def test_runs_create_success() -> None:
    response = client.post("/runs", json={"task": "请拆解这个需求并给出两周计划"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "succeeded"
    assert payload["run_id"].startswith("run-")
    assert payload["trace_id"].startswith("tr-")
    assert payload["route"]["specialist"] == "planner"
    assert payload["output"]["summary"]


def test_runs_create_validation_error() -> None:
    response = client.post("/runs", json={"task": "bad"})
    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "BAD_REQUEST"
