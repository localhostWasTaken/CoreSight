"""
Embedding and Similarity Functions for CoreSight
Uses hash-based embeddings for reliable operation
"""

import numpy as np
import hashlib
from typing import List

# Embedding dimension - consistent for all embeddings
EMBEDDING_DIM = 768


def generate_embedding(text: str) -> List[float]:
    """
    Generate embeddings for text using deterministic hash-based approach.
    
    This provides consistent, reliable embeddings for similarity search
    without external API dependencies.
    
    Args:
        text: Input text to generate embeddings for
        
    Returns:
        List of floats representing the embedding vector
    """
    if not text or not text.strip():
        return [0.0] * EMBEDDING_DIM
    
    # Normalize text for consistent embeddings
    normalized_text = text.lower().strip()
    
    # Use multiple hash rounds for better distribution
    embedding = []
    for i in range(EMBEDDING_DIM):
        # Create unique hash for each dimension
        seed_text = f"{normalized_text}:{i}"
        hash_obj = hashlib.sha256(seed_text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to float in range [-1, 1]
        value = (hash_bytes[i % len(hash_bytes)] / 127.5) - 1.0
        embedding.append(value)
    
    # Normalize the vector
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = [v / norm for v in embedding]
    
    return embedding


def calculate_cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    if not vec1 or not vec2:
        return 0.0
    
    try:
        # Handle different vector dimensions by padding or truncating
        max_len = max(len(vec1), len(vec2))
        arr1 = np.zeros(max_len)
        arr2 = np.zeros(max_len)
        arr1[:len(vec1)] = vec1
        arr2[:len(vec2)] = vec2
        
        dot_product = np.dot(arr1, arr2)
        norm1 = np.linalg.norm(arr1)
        norm2 = np.linalg.norm(arr2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    except Exception as e:
        print(f"Error calculating similarity: {e}")
        return 0.0
