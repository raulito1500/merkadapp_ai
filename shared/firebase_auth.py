import httpx

FIREBASE_SIGN_IN_URL = (
    "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
)

def get_firebase_token(email: str, password: str, api_key: str) -> str:
    response = httpx.post(
        FIREBASE_SIGN_IN_URL,
        params={"key": api_key},
        json={"email": email, "password": password, "returnSecureToken": True},
        timeout=20,
    )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise RuntimeError(
            f"Firebase login failed: {get_error_message(e.response)}") from e
    return response.json()["idToken"]


def get_error_message(response: httpx.Response) -> str:
    try:
        return response.json().get("message", "Sin mensaje")
    except ValueError:
        return response.text[:100]
