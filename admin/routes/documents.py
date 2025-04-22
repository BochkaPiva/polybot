from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..models.document import Document
from ..document_manager import DocumentManager
from ..dependencies import get_opensearch_client

router = APIRouter()

@router.delete("/documents/{document_id}")
async def delete_document(document_id: int, document_manager: DocumentManager = Depends(get_document_manager)):
    """Удаление документа"""
    success = await document_manager.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Документ не найден или ошибка при удалении")
    return {"status": "success", "message": f"Документ {document_id} успешно удален"} 