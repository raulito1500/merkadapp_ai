import os

from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
SUPABASE_URL = os.environ["SUPABASE_URL"]
FIREBASE_API_KEY = os.environ["FIREBASE_API_KEY"]
FIREBASE_EMAIL = os.environ["FIREBASE_EMAIL"]
FIREBASE_PASSWORD = os.environ["FIREBASE_PASSWORD"]

MARKET_API_BASE_URL = os.environ["MARKET_API_BASE_URL"]
EXPENSES_API_BASE_URL = os.environ["EXPENSES_API_BASE_URL"]


MODEL_NAME = os.environ["MODEL_TEXT_NAME"]
