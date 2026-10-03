import httpx

from shared.config import API_BASE_URL, FIREBASE_API_KEY, FIREBASE_EMAIL, FIREBASE_PASSWORD
from shared.firebase_auth import get_firebase_token


def get_recent_ingredients() -> list[dict]:
    token = get_firebase_token(
        email=FIREBASE_EMAIL,
        password=FIREBASE_PASSWORD,
        api_key=FIREBASE_API_KEY,
    )
    response = httpx.get(
        url=f"{API_BASE_URL}/market-list/recent-ingredients",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    response.raise_for_status()
    return response.json()
