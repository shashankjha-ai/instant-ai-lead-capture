# Import pytest framework for unit testing assertions
import pytest
# Import TestClient from FastAPI to simulate asynchronous HTTP requests
from fastapi.testclient import TestClient
# Import FastAPI application instance from main module
from src.main import app

# Instantiate test client wrapping FastAPI application routes
client = TestClient(app)

# Define test function verifying health check endpoint return contract
def test_health_check():
    # Execute HTTP GET request to health route
    response = client.get("/health")
    # Assert HTTP response status code is 200 OK
    assert response.status_code == 200
    # Assert return JSON contains healthy status string
    assert response.json()["status"] == "healthy"

# Define test function verifying webhook capture endpoint with mock data
def test_handle_lead_capture():
    # Construct sample valid lead capture payload dictionary
    payload = {
        "name": "Mostafa Walid",
        "email": "mostafa@realates.com",
        "phone": "+201061929895",
        "company": "Realates AI Systems",
        "message": "Testing webhook SLA speed.",
        "channel": "whatsapp"
    }
    # Execute HTTP POST request to capture endpoint
    response = client.post("/api/v1/webhook/capture", json=payload)
    # Assert HTTP response status code is 200 OK
    assert response.status_code == 200
    # Extract JSON dictionary from response body
    data = response.json()
    # Assert status field is success
    assert data["status"] == "success"
    # Assert lead name matches submitted payload
    assert data["lead_name"] == "Mostafa Walid"
