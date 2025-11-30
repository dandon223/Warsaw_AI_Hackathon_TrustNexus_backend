import faiss
import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import numpy as np
# Directory where FAISS index + metadata are stored
FAISS_DIR = "./"
INDEX_PATH = f"{FAISS_DIR}/index.faiss"
META_PATH = f"{FAISS_DIR}/metadata.json"

# FREE embedding model
model = SentenceTransformer("BAAI/bge-small-en")

def embed(text: str) -> np.ndarray:
    """Return a normalized float32 vector."""
    return model.encode(text, normalize_embeddings=True).astype("float32")


# Load existing index or create a new one
def load_or_create_index(dim: int = 384):
    os.makedirs(FAISS_DIR, exist_ok=True)

    # Load index or create new
    if os.path.exists(INDEX_PATH):
        index = faiss.read_index(INDEX_PATH)
    else:
        index = faiss.IndexFlatIP(dim)  # cosine similarity

    # Load metadata or create new
    if os.path.exists(META_PATH):
        with open(META_PATH, "r") as f:
            metadata = json.load(f)
    else:
        metadata = []

    return index, metadata


# Save index + metadata
def save_index_and_metadata(index, metadata):
    faiss.write_index(index, INDEX_PATH)
    with open(META_PATH, "w") as f:
        json.dump(metadata, f)


def search_emails(query: str, k: int = 5):
    index, metadata = load_or_create_index()

    qvec = embed(query)
    qvec = np.expand_dims(qvec, axis=0)

    scores, idxs = index.search(qvec, k)

    email_ids = [metadata[i]["email_id"] for i in idxs[0]]
    return Email.objects.filter(id__in=email_ids)