from fastapi import APIRouter, File, HTTPException, UploadFile

from agents import ingestion_agent
from models.schemas import DocumentRecord, ExtractedEntities, UploadResponse
from services import supabase_service

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    file_bytes = await file.read()
    try:
        result = ingestion_agent.ingest(file.filename, file_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return UploadResponse(
        doc_id=result["doc_id"],
        filename=result["filename"],
        chunk_count=result["chunk_count"],
        entities=ExtractedEntities(**result["entities"]),
    )


@router.get("", response_model=list[DocumentRecord])
async def list_documents():
    records = supabase_service.list_documents()
    return [DocumentRecord(**record) for record in records]
