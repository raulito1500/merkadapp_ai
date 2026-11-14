import os
import unittest
from unittest.mock import MagicMock, patch

import httpx

# shared.config reads required env vars at import time
for _var in (
    "GEMINI_API_KEY", "SUPABASE_URL", "FIREBASE_API_KEY", "FIREBASE_EMAIL",
    "FIREBASE_PASSWORD", "MARKET_API_BASE_URL", "EXPENSES_API_BASE_URL",
    "MODEL_TEXT_NAME", "BRAVE_API_KEY",
):
    os.environ.setdefault(_var, "test")

from services.recipes.images import search_photo  # noqa: E402


def _response(payload):
    resp = MagicMock()
    resp.json.return_value = payload
    resp.raise_for_status.return_value = None
    return resp


class SearchPhotoTest(unittest.TestCase):
    @patch("services.recipes.images.httpx.get")
    def test_returns_thumbnail_url(self, mock_get):
        mock_get.return_value = _response(
            {"results": [{"thumbnail": {"src": "https://imgs.search.brave.com/x.jpg"}}]}
        )
        self.assertEqual(search_photo("bockwurst"), "https://imgs.search.brave.com/x.jpg")

    @patch("services.recipes.images.httpx.get")
    def test_empty_results_returns_none(self, mock_get):
        mock_get.return_value = _response({"results": []})
        self.assertIsNone(search_photo("nothing"))

    @patch("services.recipes.images.httpx.get")
    def test_http_error_returns_none(self, mock_get):
        mock_get.side_effect = httpx.TimeoutException("timeout")
        self.assertIsNone(search_photo("bockwurst"))


if __name__ == "__main__":
    unittest.main()
