"""Automated tests for student-ml-api.

TestClient starts the FastAPI application in-process, so no server and no
Docker container are required to run these tests.
"""

from fastapi.testclient import TestClient

from app import APPLICATION_NAME, APPLICATION_VERSION, application

test_client = TestClient(application)


def test_health_endpoint_returns_healthy_status():
    response = test_client.get("/health")

    assert response.status_code == 200

    response_body = response.json()
    assert response_body["status"] == "healthy"
    assert response_body["application"] == APPLICATION_NAME
    assert response_body["version"] == APPLICATION_VERSION


def test_predict_endpoint_returns_expected_prediction():
    response = test_client.post("/predict", json={"value": 10})

    assert response.status_code == 200
    assert response.json() == {"input": 10, "prediction": 20}


def test_predict_endpoint_rejects_missing_input():
    response = test_client.post("/predict", json={})

    assert response.status_code == 400
    assert response.json()["error"] == "invalid_request"


def test_predict_endpoint_rejects_invalid_input():
    response = test_client.post("/predict", json={"value": "not_a_number"})

    assert response.status_code == 400
    assert response.json()["error"] == "invalid_request"


def test_predict_endpoint_handles_negative_value():
    response = test_client.post("/predict", json={"value": -3})

    assert response.status_code == 200
    assert response.json()["prediction"] == -6
