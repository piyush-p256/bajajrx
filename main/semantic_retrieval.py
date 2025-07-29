from typing import List, Dict, Tuple
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


def embed_chunks(chunks: List[Dict], model_name: str = 'all-MiniLM-L6-v2') -> Tuple[np.ndarray, List[str], List[Dict]]:
    """
    Embed each chunk's text and return (embeddings, chunk_texts, chunk_metadata)
    """
    model = SentenceTransformer(model_name)
    texts = [chunk['text'] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True, normalize_embeddings=True)
    metadata = [chunk['metadata'] for chunk in chunks]
    return embeddings, texts, metadata


def build_faiss_index(embeddings: np.ndarray):
    """
    Build a FAISS index from embeddings and return it.
    """
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # Use inner product for cosine similarity (with normalized vectors)
    index.add(embeddings)
    return index


def embed_query(query: str, model: SentenceTransformer) -> np.ndarray:
    """
    Embed a query string using the provided model.
    """
    return model.encode([query], convert_to_numpy=True, normalize_embeddings=True)[0]


def search_faiss(index, query_embedding: np.ndarray, top_k: int = 3) -> List[int]:
    """
    Search the FAISS index for the top_k most similar chunks to the query embedding.
    Return the indices of the top_k chunks.
    """
    D, I = index.search(query_embedding.reshape(1, -1), top_k)
    return I[0].tolist()


def retrieve_relevant_chunks(chunks: List[Dict], index, model: SentenceTransformer, questions: List[str], top_k: int = 3) -> List[List[Dict]]:
    """
    For each question, retrieve top_k relevant chunks.
    Return: List of lists of chunk dicts (one list per question)
    """
    results = []
    for question in questions:
        q_emb = embed_query(question, model)
        top_indices = search_faiss(index, q_emb, top_k=top_k)
        top_chunks = [chunks[i] for i in top_indices]
        results.append(top_chunks)
    return results 