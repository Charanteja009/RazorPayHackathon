import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import get_db

mock_db = MagicMock()

def override_get_db():
    try:
        yield mock_db
    finally:
        pass

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_health_check_endpoint():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"

def test_predict_recovery_endpoint():
    payload = {
        "amount": 2500.0,
        "failure_reason": "INSUFFICIENT_FUNDS",
        "payment_method": "UPI",
        "retry_count": 0,
        "hours_since_failure": 1.0
    }
    resp = client.post("/api/recovery/predict", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "recovery_probability" in data
    assert data["recovery_eligible"] is True

def test_missing_idempotency_key_error_422():
    # Priority 5: Missing Idempotency-Key returns 422 Unprocessable Entity
    resp = client.post("/api/recovery/SCENARIO_1_TEMPORARY_SUCCESS/start")
    assert resp.status_code == 422
    assert "mandatory" in resp.json()["detail"].lower()

def test_get_transaction_404_error():
    mock_db.query.return_value.filter.return_value.first.return_value = None
    resp = client.get("/api/recovery/NON_EXISTENT_TX_ID_999")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()

def test_idempotency_conflict_error():
    mock_record = MagicMock()
    mock_record.idempotency_key = "ik_dup_123"
    mock_record.request_hash = "different_hash"
    mock_record.response_json = {"status": "SUCCESS"}
    
    mock_db.query.return_value.filter.return_value.first.return_value = mock_record

    resp = client.post(
        "/api/recovery/SCENARIO_1_TEMPORARY_SUCCESS/start",
        json={"different": "body"},
        headers={"Idempotency-Key": "ik_dup_123"}
    )
    assert resp.status_code == 409
    assert "previously used" in resp.json()["detail"].lower()

def test_provider_health_endpoint():
    resp = client.get("/api/llm/providers")
    assert resp.status_code == 200
    data = resp.json()
    assert "providers" in data
    assert len(data["providers"]) == 4
