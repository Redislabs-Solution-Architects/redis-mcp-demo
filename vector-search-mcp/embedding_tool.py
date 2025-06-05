"""
Text-to-embedding conversion tool for semantic search
"""

import os
# Fix HuggingFace tokenizers warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import numpy as np
from sentence_transformers import SentenceTransformer

class MovieEmbeddings:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """Initialize embedding model. Using MiniLM for fast, high-quality embeddings."""
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        print(f" Embedding model loaded! Dimension: {self.dimension}")
    
    def generate_embedding(self, text):
        """Generate embedding vector from text."""
        if not text:
            return None
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.astype(np.float32)

# Global model instance
_movie_embeddings = None

def get_movie_embeddings():
    """Get or initialize the movie embeddings model"""
    global _movie_embeddings
    if _movie_embeddings is None:
        print(" Loading embedding model (all-MiniLM-L6-v2)...")
        _movie_embeddings = MovieEmbeddings()
    return _movie_embeddings

def semantic_movie_search(query_text: str, k: int = 5) -> dict:
    """Prepare semantic search parameters for Redis vector search
    
    Args:
        query_text: Natural language query
        k: Number of results to return
        
    Returns:
        Dictionary with search parameters for vector_search_hash tool
    """
    model = get_movie_embeddings()
    embedding = model.generate_embedding(query_text)
    query_vector = embedding.astype(float).tolist()
    
    return {
        "query_vector": query_vector,
        "index_name": "idx:movies_vector", 
        "vector_field": "plot_embedding",
        "k": k,
        "return_fields": ["title", "plot", "genre", "release_year", "rating"]
    }