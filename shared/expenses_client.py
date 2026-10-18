import httpx

from shared.config import EXPENSES_API_BASE_URL, FIREBASE_API_KEY, FIREBASE_EMAIL, FIREBASE_PASSWORD
from shared.firebase_auth import get_firebase_token


def create_expense(
    description: str,
    amount: float,
    currency: str,
    date: str,
    paid_by: str,
    merchant: str | None = None,
    group_id: str | None = None,
) -> dict:
    token = get_firebase_token(
        email=FIREBASE_EMAIL, password=FIREBASE_PASSWORD, api_key=FIREBASE_API_KEY
    )
    body = {
        "description": description,
        "amount": amount,
        "currency": currency,
        "date": date,
        "paidBy": paid_by,
    }
    if merchant:
        body["merchant"] = merchant
    if group_id:
        body["groupId"] = group_id

    response = httpx.post(
        url=f"{EXPENSES_API_BASE_URL}/expenses",
        headers={"Authorization": f"Bearer {token}"},
        json=body,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()
