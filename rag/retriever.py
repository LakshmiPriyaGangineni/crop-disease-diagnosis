import json
import os
import pathlib
import pickle

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "rag" / "crop_data.json"
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", str(BASE_DIR / "rag" / "faiss_index.bin"))
METADATA_PATH = os.getenv("FAISS_METADATA_PATH", str(BASE_DIR / "rag" / "faiss_metadata.pkl"))

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def _load_data() -> list:
    """Load the JSON knowledge base and return the list of disease entries.

    Returns
    -------
    list
        A list of dictionaries, each representing a disease record.
    """
    if not DATA_PATH.is_file():
        raise FileNotFoundError(f"Knowledge base not found at {DATA_PATH}")
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("diseases", [])

def _make_documents(diseases_list: list) -> list:
    """Convert disease entries into plain‑text documents for embedding.

    Parameters
    ----------
    diseases_list: list
        List of disease dictionaries.

    Returns
    -------
    list
        List of concatenated strings.
    """
    docs = []
    for item in diseases_list:
        # Repeat symptoms to give them higher weight for symptom‑focused queries
        symptoms_text = ' '.join(item.get('symptoms', []))
        doc = (
            f"Crop: {item.get('crop', '')}. "
            f"Disease: {item.get('disease', '')}. Disease: {item.get('disease', '')}. "
            f"Symptoms: {symptoms_text}. Symptoms: {symptoms_text}. "
            f"Treatment: {item.get('treatment', '')}. "
            f"Prevention: {item.get('prevention', '')}."
        )
        docs.append(doc)
    return docs

# Load the embedding model once – it is relatively heavy but can be reused.
_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def _embed_texts(texts: list) -> np.ndarray:
    """Encode a list of texts into normalized ``float32`` embeddings.
    """
    return _model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype("float32")

# ---------------------------------------------------------------------------
# Index construction / loading
# ---------------------------------------------------------------------------
def build_faiss_index(diseases_list: list = None) -> tuple:
    """Build a FAISS index from the knowledge base and persist it.

    Parameters
    ----------
    diseases_list: list, optional
        Provide a pre‑loaded list of disease entries to avoid re‑reading the JSON.

    Returns
    -------
    tuple
        ``(index, documents, diseases_list)``
    """
    if diseases_list is None:
        diseases_list = _load_data()
    documents = _make_documents(diseases_list)
    embeddings = _embed_texts(documents)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)
    # Persist index and accompanying metadata for fast reloads.
    faiss.write_index(index, FAISS_INDEX_PATH)
    with open(METADATA_PATH, "wb") as mf:
        pickle.dump({"documents": documents, "entries": diseases_list}, mf)
    return index, documents, diseases_list

def load_faiss_index() -> tuple:
    """Load an existing FAISS index and its metadata.

    If the index files are missing, they are built on‑the‑fly.
    """
    if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(METADATA_PATH):
        index = faiss.read_index(FAISS_INDEX_PATH)
        with open(METADATA_PATH, "rb") as mf:
            meta = pickle.load(mf)
        return index, meta["documents"], meta["entries"]
    # Fallback – create a fresh index.
    return build_faiss_index()

# Load (or create) the index at import time – this is cheap after the first run.
index, _documents, _entries = load_faiss_index()

# ---------------------------------------------------------------------------
# Public retrieval API
# ---------------------------------------------------------------------------
def retrieve(query: str, top_k: int = 3) -> list:
    """Return the most relevant disease records for a natural‑language query.

    Parameters
    ----------
    query: str
        The user question.
    top_k: int, optional
        Number of results to return (default = 3).

    Returns
    -------
    list of dict
        Each dict contains ``score`` (float similarity) and ``data`` (original entry).
    """
    if not query:
        return []
    # Encode query
    query_emb = _embed_texts([query])
    # Retrieve a larger candidate set for re‑ranking with disease name boost
    raw_k = max(top_k * 5, 10)
    scores, indices = index.search(query_emb, raw_k)
    results = []
    query_lc = query.lower()
    for score, idx in zip(scores[0], indices[0]):
        if 0 <= idx < len(_entries):
            entry = _entries[int(idx)]
            boost = 0.0
            disease_name = entry.get('disease', '').lower()
            if disease_name and disease_name in query_lc:
                boost = 0.15  # modest boost when disease name appears in query
            results.append({"score": float(score) + boost, "data": entry})
    # Sort by boosted score and return top_k results
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


def get_disease_entry(disease_name: str):
    """Look up a disease record from the knowledge base by disease or class name.

    Matches formats like 'Tomato_Early_Blight' or 'Tomato Early Blight'.
    Returns the entry dict, or None if the disease is not in the knowledge base.
    """
    if not disease_name:
        return None
    normalized_target = disease_name.replace("_", " ").strip().lower()
    for entry in _entries:
        entry_dis = entry.get("disease", "").strip().lower()
        if entry_dis == normalized_target:
            return entry
    for entry in _entries:
        entry_dis = entry.get("disease", "").strip().lower()
        if normalized_target in entry_dis or entry_dis in normalized_target:
            return entry
    return None


def retrieve_for_candidate(candidate_name: str, query: str = "", top_k: int = 2) -> list:
    """Retrieve relevant knowledge specifically for a candidate disease.

    If the candidate disease is supported in the knowledge base, returns authoritative
    and relevant records. If the candidate is missing/unsupported, returns an empty list.
    """
    if not candidate_name:
        return []

    entry = get_disease_entry(candidate_name)
    if entry is None:
        # Candidate disease is not present in our knowledge base
        return []

    clean_name = candidate_name.replace("_", " ").strip()
    search_str = f"{clean_name} {query}".strip() if query else clean_name
    results = retrieve(search_str, top_k=top_k)

    # Ensure the exact candidate entry is always present at the top of the candidate's context
    has_exact = any(
        r["data"].get("disease", "").strip().lower() == entry.get("disease", "").strip().lower()
        for r in results
    )
    if not has_exact:
        results.insert(0, {"score": 1.0, "data": entry})
        results = results[:top_k]

    return results

# ---------------------------------------------------------------------------
# Simple command‑line demo (useful for quick testing)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    demo_queries = [
        "What are the symptoms of tomato early blight?",
        "How can I prevent potato late blight?",
        "What treatment is recommended for bacterial spot?",
    ]
    for q in demo_queries:
        print("\nQuery:", q)
        for res in retrieve(q, top_k=2):
            print(f"  - [{res['score']:.4f}] {res['data']['crop']} – {res['data']['disease']}")
    # Uncomment the line below to rebuild the index after editing the JSON.
    # build_faiss_index()