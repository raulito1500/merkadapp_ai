import httpx

from shared.config import BRAVE_API_KEY

BRAVE_IMAGES_URL = "https://api.search.brave.com/res/v1/images/search"


def search_photo(query: str) -> str | None:
    """Return a real image URL for the query, or None if anything goes wrong.

    A missing photo must never break recipe generation.
    """
    try:
        response = httpx.get(
            BRAVE_IMAGES_URL,
            params={"q": query, "count": 1, "safesearch": "strict"},
            headers={
                "X-Subscription-Token": BRAVE_API_KEY,
                "Accept": "application/json",
            },
            timeout=10,
        )
        response.raise_for_status()
        results = response.json().get("results", [])
        if not results:
            return None
        return results[0]["thumbnail"]["src"]
    except (httpx.HTTPError, KeyError, ValueError):
        return None
