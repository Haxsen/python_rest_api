import pytest
import requests
from app.config import RUST_SERVICE_URL

@pytest.mark.asyncio
async def test_rust_start_restake():
    # Set up a test payload
    payload = {
        "user_id": 1,
        "amount": 100.0
    }

    # Call the Rust service endpoint to start a restake
    response = requests.post(f"{RUST_SERVICE_URL}/start-restake", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "operation_id" in data
    assert data["message"] == "Restake initiated"

@pytest.mark.asyncio
async def test_rust_confirm_restake():
    # Use a mock operation ID to confirm (should match what is set up in your Rust mock data or the start test)
    payload = {
        "operation_id": 1
    }

    # Call the Rust service endpoint to confirm the restake
    response = requests.post(f"{RUST_SERVICE_URL}/confirm-restake", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["message"] == "Restake operation confirmed and completed"
