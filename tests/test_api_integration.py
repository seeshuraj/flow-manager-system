import pytest
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_create_execute_and_status_flow():
    flow_config = {
        "id": "api_flow_1",
        "name": "API Flow Test",
        "start_task": "start",
        "tasks": [
            {"name": "start", "task_type": "print", "parameters": {"message": "Starting flow", "failure_rate": 0}},
            {"name": "end", "task_type": "wait", "parameters": {"seconds": 0, "failure_rate": 0}},
        ],
        "conditions": []
    }

    create_resp = client.post("/flow/create", json=flow_config)
    assert create_resp.status_code == 200
    exec_id = create_resp.json().get("execution_id")
    assert exec_id

    execute_resp = client.post("/flow/execute", json={"execution_id": exec_id})
    assert execute_resp.status_code == 200

    import time
    final_state = None
    for _ in range(10):
        status_resp = client.get(f"/flow/{exec_id}/status")
        assert status_resp.status_code == 200
        state = status_resp.json()
        if state["status"] == "COMPLETED":
            final_state = state
            break
        time.sleep(0.5)

    assert final_state is not None
    assert final_state["status"] == "COMPLETED"
    assert "start" in final_state["completed_tasks"]
    assert "end" in final_state["completed_tasks"]

    delete_resp = client.delete(f"/flow/{exec_id}")
    assert delete_resp.status_code == 200
    assert "deleted successfully" in delete_resp.json().get("message", "")

