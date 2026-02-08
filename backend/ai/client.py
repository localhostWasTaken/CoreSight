"""
AI Client Configuration for CoreSight

Uses Featherless AI for LLM operations (Llama 3.1).
Embeddings use hash-based approach for reliability.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load .env file before accessing environment variables
load_dotenv()

# Initialize Featherless client for LLM (OpenAI-compatible)
featherless_api_key = os.getenv("FEATHERLESS_API_KEY")
featherless_base_url = os.getenv("FEATHERLESS_BASE_URL", "https://api.featherless.ai/v1")

client = None
if featherless_api_key:
    try:
        client = OpenAI(
            base_url=featherless_base_url,
            api_key=featherless_api_key,
        )
        print("[INFO] Featherless client initialized for LLM (Llama 3.1)")
    except Exception as e:
        print(f"[WARN] Failed to initialize Featherless client: {e}")

if not client:
    print("[WARN] WARNING: No LLM client configured. AI features will not work.")

# Model configuration
LLM_MODEL = os.getenv("LLM_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct")

# For backwards compatibility
featherless_client = client
gemini_client = None  # Not used - using hash-based embeddings
EMBEDDING_MODEL = None  # Not used - using hash-based embeddings
