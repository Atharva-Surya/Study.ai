import os
import runpy
import requests
from typing import Dict, Any, Optional

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Reuse prompt template from your uploaded pipeline
from app.services.rag_pipeline_faiss.prompt import PROMPT_TEMPLATE

BASE_DIR = os.path.join(os.path.dirname(__file__), "rag_pipeline_faiss")
DEFAULT_EMBED_MODEL = os.getenv("RAG_EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
DEFAULT_INDEX_DIR = os.getenv("RAG_FAISS_INDEX_PATH", os.path.join(BASE_DIR, "faiss_index"))
MODEL_SERVER_URL = os.getenv("RAG_MODEL_SERVER_URL", "http://localhost:11434/api/generate")
SIMILARITY_THRESHOLD = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "1.0"))

_embeddings = None
_vectordb = None

def _load_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name=DEFAULT_EMBED_MODEL)
    return _embeddings

def _load_index(index_dir: Optional[str] = None):
    global _vectordb
    if _vectordb is None:
        idx = index_dir or DEFAULT_INDEX_DIR
        emb = _load_embeddings()
        _vectordb = FAISS.load_local(idx, emb, allow_dangerous_deserialization=True)
    return _vectordb

def rebuild_index(run_ingest_script: bool = True) -> Dict[str, Any]:
    """
    Trigger rebuilding the FAISS index. By default runs the existing ingest.py script
    located in the uploaded pipeline folder. Returns a simple status dict.
    """
    try:
        if run_ingest_script:
            ingest_path = os.path.join(BASE_DIR, "ingest.py")
            if not os.path.exists(ingest_path):
                return {"ok": False, "error": f"ingest.py not found at {ingest_path}"}
            # run the script (it will create the faiss_index folder next to it)
            runpy.run_path(ingest_path, run_name="__main__")
        # invalidate cached vectordb so it reloads on next ask
        global _vectordb
        _vectordb = None
        _load_index()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def ask(question: str, k: int = 5) -> Dict[str, Any]:
    """
    Query the vector DB, call the model server and return a dict:
    { "answer": "...", "similarity_score": <float> } or error message.
    """
    try:
        vectordb = _load_index()
    except Exception as e:
        return {"answer": f"Failed to load index: {e}", "similarity_score": None}

    try:
        results = vectordb.similarity_search_with_score(question, k=k)
    except Exception as e:
        return {"answer": f"Vector search failed: {e}", "similarity_score": None}

    if not results:
        return {"answer": "The answer is not available in the uploaded documents.", "similarity_score": None}

    best_score = results[0][1]

    if best_score > SIMILARITY_THRESHOLD:
        return {"answer": "The answer is not available in the uploaded documents.", "similarity_score": float(best_score)}

    context = "\n\n".join([doc.page_content for doc, score in results])

    prompt = PROMPT_TEMPLATE.format(context=context, question=question)

    try:
        payload = {
            "model": os.getenv("RAG_GENERATION_MODEL", "qwen3:8b"),
            "prompt": prompt,
            "stream": False,
            "think": False,
            "options": {"num_predict": int(os.getenv("RAG_NUM_PREDICT", "1000"))}
        }
        resp = requests.post(MODEL_SERVER_URL, json=payload, timeout=int(os.getenv("RAG_MODEL_TIMEOUT", "300")))
        resp.raise_for_status()
        data = resp.json()
        answer = data.get("response") or data.get("thinking") or ""
    except Exception as e:
        return {"answer": f"Model server error: {e}", "similarity_score": float(best_score)}

    return {"answer": answer, "similarity_score": float(best_score)}
