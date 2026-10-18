import httpx

from shared.config import MARKET_API_BASE_URL, FIREBASE_API_KEY, FIREBASE_EMAIL, FIREBASE_PASSWORD
from shared.firebase_auth import get_firebase_token


def get_recent_ingredients() -> list[dict]:
    token = get_firebase_token(
        email=FIREBASE_EMAIL,
        password=FIREBASE_PASSWORD,
        api_key=FIREBASE_API_KEY,
    )
    response = httpx.get(
        url=f"{MARKET_API_BASE_URL}/products/available-ingredients",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    response.raise_for_status()
    return response.json()


def get_bill(bill_id: str) -> dict:
    token = get_firebase_token(
        email=FIREBASE_EMAIL, password=FIREBASE_PASSWORD, api_key=FIREBASE_API_KEY
    )
    response = httpx.get(
        url=f"{MARKET_API_BASE_URL}/bills/{bill_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def submit_to_merkadapp_api(xml_bytes: bytes, filename: str = "factura.xml") -> str:
    token = get_firebase_token(
        email=FIREBASE_EMAIL,
        password=FIREBASE_PASSWORD,
        api_key=FIREBASE_API_KEY
    )
    response = httpx.post(
        url=f"{MARKET_API_BASE_URL}/bills/upload/xml",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": (filename, xml_bytes, "text/xml")},
        timeout=30,
    )
    response.raise_for_status()
    return response.json().get("id", "No se recibió ID")


def create_market_list(items: list[dict]) -> dict:
    token = get_firebase_token(
        email=FIREBASE_EMAIL, password=FIREBASE_PASSWORD, api_key=FIREBASE_API_KEY
    )
    response = httpx.post(
        url=f"{MARKET_API_BASE_URL}/market-list",
        headers={"Authorization": f"Bearer {token}"},
        json={"items": items},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()
