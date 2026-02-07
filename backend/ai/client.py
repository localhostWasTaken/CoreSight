"""
AI Client Configuration for CoreSight

Initializes the OpenAI client for Featherless AI and defines model constants.
"""

import os
from openai import OpenAI

# Initialize OpenAI client with Featherless AI
client = OpenAI(
    base_url=os.getenv("FEATHERLESS_BASE_URL", "https://api.featherless.ai/v1"),
    api_key=os.getenv("FEATHERLESS_API_KEY", "rc_6592c9b70f6b793d73a2cb301a915a586d586fdad0e75d61e35e50ae22be29b7"),
)

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "IEITYuan/Yuan-embedding-2.0-en")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-ai/DeepSeek-R1-0528")
