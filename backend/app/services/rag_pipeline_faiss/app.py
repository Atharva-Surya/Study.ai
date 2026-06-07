from fastapi import FastAPI
from pydantic import BaseModel

from langchain_huggingface import HuggingFaceEmbeddings, data
from langchain_community.vectorstores import FAISS


import requests

from prompt import PROMPT_TEMPLATE

app = FastAPI(title="RAG PDF Chatbot")

print("Loading Embedding Model...")

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5"
)

print("Loading vector database (FAISS)...")

vectordb = FAISS.load_local(
    "faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)

SIMILARITY_THRESHOLD = 1.0


class QueryRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {"message": "RAG API Running"}


@app.post("/ask")
def ask_question(request: QueryRequest):

    question = request.question

    results = vectordb.similarity_search_with_score(
        question,
        k=5
    )

    if len(results) == 0:
        return {
            "answer":
            "The answer is not available in the uploaded documents."
        }

    best_score = results[0][1]

    print("Best Score:", best_score)

    if best_score > SIMILARITY_THRESHOLD:
        return {
            "answer":
            "The answer is not available in the uploaded documents."
        }

    context = "\n\n".join(
        [doc.page_content for doc, score in results]
    )

    prompt = PROMPT_TEMPLATE.format(
        context=context,
        question=question
    )
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen3:8b",
                "prompt": prompt,
                "stream": False,
                "think": False,
                "options": {
                    "num_predict": 1000
                }
            },
            timeout=300
        )

        data = response.json()

        print("OLLAMA RESPONSE:")
        print(data)

        answer = data.get("response", "")

        if not answer:
            answer = data.get("thinking", "")

    except Exception as e:
        return {
            "answer": f"Ollama error: {str(e)}"
        }

    return {
        "answer": answer,
        "similarity_score": float(best_score)
    }