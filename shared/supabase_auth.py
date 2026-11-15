import httpx

from shared.config import SUPABASE_PROJECT_URL, SUPABASE_PUBLISHABLE_KEY


def get_supabase_token(email: str, password: str):
    response = httpx.post(
        f"{SUPABASE_PROJECT_URL}/auth/v1/token",
        params={"grant_type": "password"},
        headers={"apikey": SUPABASE_PUBLISHABLE_KEY},
        json={"email": email, "password": password},
    )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise RuntimeError(
            f"Supabase login failed: {get_error_message(e.response)}") from e
    return response.json()["access_token"]


def get_error_message(response: httpx.Response) -> str:
    try:
        return response.json().get("msg", "Sin mensaje")
    except ValueError:
        return response.text[:100]


if __name__ == "__main__":
    from shared.config import FIREBASE_EMAIL, FIREBASE_PASSWORD
    try:
        get_supabase_token(FIREBASE_EMAIL, FIREBASE_PASSWORD)
    except RuntimeError as e:
        print(e)
