from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import UploadResponse
from app.services.rag import rag_service
import os
import tempfile

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(('.pdf', '.txt')):
        raise HTTPException(status_code=400, detail="仅支持 PDF 和 TXT 文件")
    
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        result = rag_service.add_documents(tmp_path)
        return UploadResponse(
            success=True,
            message=f"文档 {file.filename} 上传成功",
            chunks=result["chunks"],
            file_id=result["file_id"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理文档失败: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@router.get("/documents")
async def list_documents():
    documents = rag_service.list_documents()
    total_chunks = sum(doc.get("chunks", 0) for doc in documents)
    return {"documents": documents, "total_chunks": total_chunks}


@router.delete("/documents/{file_id}")
async def delete_document(file_id: str):
    success = rag_service.delete_document(file_id)
    if success:
        return {"message": "删除成功", "success": True}
    raise HTTPException(status_code=404, detail="文件不存在")
