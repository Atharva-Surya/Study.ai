import os
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel

from app.auth.dependencies import get_current_user
from app.services.rag_service import ask as rag_ask, rebuild_index as rag_rebuild

router = APIRouter(prefix="/rag", tags=["RAG"])

class AskRequest(BaseModel):
    question: str

@router.post("/ask")
async def ask_endpoint(request: AskRequest, current_user = Depends(get_current_user)):
    """
    Query the RAG index and get an answer.
    """
    res = rag_ask(request.question)
    if "error" in res and not res.get("answer"):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=res.get("error"))
    return res

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...), current_user = Depends(get_current_user)):
    """
    Upload a PDF file and trigger FAISS index rebuild.
    """
    try:
        # Get the data directory path
        base_dir = os.path.join(os.path.dirname(__file__), "../services/rag_pipeline_faiss")
        data_dir = os.path.join(base_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        
        # Save the uploaded file
        dest = os.path.join(data_dir, file.filename)
        contents = await file.read()
        with open(dest, "wb") as f:
            f.write(contents)
        
        print(f"PDF saved: {dest}")
        
        # Trigger rebuild (ingest.py will pick up the file)
        res = rag_rebuild()
        if not res.get("ok"):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=res.get("error"))
        
        return {"ok": True, "filename": file.filename, "message": "PDF uploaded and indexed successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Upload failed: {str(e)}")

@router.post("/ingest")
async def ingest_endpoint(current_user = Depends(get_current_user)):
    """
    Trigger rebuilding the FAISS index from the uploaded pipeline's ingest.py.
    """
    res = rag_rebuild()
    if not res.get("ok"):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=res.get("error"))
    return {"ok": True}
