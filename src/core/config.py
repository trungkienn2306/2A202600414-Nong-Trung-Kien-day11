"""
Lab 11 — Configuration & API Key Setup
"""
import os
from pathlib import Path


def setup_api_key():
    """Load API keys from .env file or environment variables.

    Priority:
    1. Already set in os.environ (e.g., from shell export)
    2. Loaded from .env file in project root
    3. Interactive prompt as fallback

    Supports both Google Gemini (GOOGLE_API_KEY) and OpenAI (OPENAI_API_KEY).
    The assignment notebook uses whichever key is available.
    """
    # Try to load .env from project root (one level up from src/)
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    if key.strip() not in os.environ:
                        os.environ[key.strip()] = value.strip()

    # Google API key setup (used by ADK + Gemini models)
    if "GOOGLE_API_KEY" not in os.environ:
        # If only OpenAI key is available, we can still run
        # the assignment using OpenAI models directly.
        if "OPENAI_API_KEY" in os.environ:
            print("OpenAI API key loaded from .env — will use OpenAI for LLM calls.")
        else:
            os.environ["GOOGLE_API_KEY"] = input("Enter Google API Key: ")

    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "0"
    print("API key(s) loaded.")
    if os.environ.get("OPENAI_API_KEY"):
        print("  ✓ OPENAI_API_KEY set")
    if os.environ.get("GOOGLE_API_KEY"):
        print("  ✓ GOOGLE_API_KEY set")


# Allowed banking topics (used by topic_filter)
ALLOWED_TOPICS = [
    "banking", "account", "transaction", "transfer",
    "loan", "interest", "savings", "credit",
    "deposit", "withdrawal", "balance", "payment",
    "tai khoan", "giao dich", "tiet kiem", "lai suat",
    "chuyen tien", "the tin dung", "so du", "vay",
    "ngan hang", "atm",
]

# Blocked topics (immediate reject)
BLOCKED_TOPICS = [
    "hack", "exploit", "weapon", "drug", "illegal",
    "violence", "gambling", "bomb", "kill", "steal",
]
