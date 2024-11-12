import requests
from app.config import RUST_SERVICE_URL

async def initiate_restake_on_chain(user_id: int, amount: float):
    try:
        response = requests.post(
            f"{RUST_SERVICE_URL}/start-restake",
            json={"user_id": user_id, "amount": amount},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error communicating with Rust service: {e}")
        return None