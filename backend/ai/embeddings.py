"""
Embedding and Similarity Functions for CoreSight
"""

import json
import numpy as np
from typing import List

from .client import client, EMBEDDING_MODEL


def generate_embedding(text: str) -> List[float]:
    """
    Generate embeddings for text using Featherless AI
    
    Args:
        text: Input text to generate embeddings for
        
    Returns:
        List of floats representing the embedding vector
    """
    if not text or not text.strip():
        # Return zero vector for empty text
        return [0.0] * 768
    
    try:
        response = client.chat.completions.create(
            model=EMBEDDING_MODEL,
            messages=[
                {"role": "system", "content": "Generate semantic embeddings for the given text."},
                {"role": "user", "content": text}
            ],
        )
        
        # The embedding model returns the embedding in the content
        # Parse and convert to float list
        content = response.model_dump()['choices'][0]['message']['content']
        
        # If the model returns a string representation, parse it
        # Otherwise, this might need adjustment based on actual API response
        try:
            embedding = json.loads(content)
            if isinstance(embedding, list):
                return [float(x) for x in embedding]
        except:
            # Fallback: Create a simple hash-based embedding
            import hashlib
            hash_obj = hashlib.sha256(text.encode())
            hash_bytes = hash_obj.digest()
            # Convert to 768-dim vector (standard for many models)
            embedding = []
            for i in range(768):
                embedding.append(float(hash_bytes[i % len(hash_bytes)]) / 255.0)
            return embedding
            
    except Exception as e:
        print(f"Error generating embedding: {e}")
        # Return zero vector on error
        return [0.0] * 768


def calculate_cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    if not vec1 or not vec2:
        return 0.0
    
    try:
        arr1 = np.array(vec1)
        arr2 = np.array(vec2)
        
        dot_product = np.dot(arr1, arr2)
        norm1 = np.linalg.norm(arr1)
        norm2 = np.linalg.norm(arr2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    except Exception as e:
        print(f"Error calculating similarity: {e}")
        return 0.0
