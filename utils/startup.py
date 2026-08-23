"""
Startup utilities for the RAG Chatbot.

Provides:
- ``ensure_uploads_dir()`` — creates the uploads folder if missing.
- ``validate_env()``        — checks required env vars are set.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

UPLOADS_DIR = "uploads"

# Required environment variables and human-readable descriptions
_REQUIRED_ENV_VARS = {
    "MONGODB_URI": (
        "MongoDB Atlas connection string "
        "(e.g. mongodb+srv://user:pass@cluster.mongodb.net/)"
    ),
    "GROQ_API_KEY": (
        "Groq API key for the language model "
        "(get one at https://console.groq.com)"
    ),
}


def ensure_uploads_dir() -> None:
    """Create the uploads/ directory if it does not already exist."""
    path = Path(UPLOADS_DIR)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created '{UPLOADS_DIR}/' directory.")


def validate_env() -> list[str]:
    """
    Check that all required environment variables are set.

    Returns
    -------
    list[str]
        A list of human-readable error messages for missing variables.
        Empty list means all checks passed.
    """
    errors = []
    for var, description in _REQUIRED_ENV_VARS.items():
        value = os.getenv(var, "").strip()
        if not value or value.startswith("your_"):
            errors.append(
                f"**{var}** is not configured.\n"
                f"  → {description}"
            )
    return errors
