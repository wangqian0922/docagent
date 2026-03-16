from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from app.models.schemas import UploadResponse
from app.services.rag import rag_service
from app.tasks.document_tasks import process_document
import os
import tempfile

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    knowledge_base_id: str = Query("default")
):
    if not file.filename.endswith(('.pdf', '.txt', '.docx')):
        raise HTTPException(status_code=400, detail="仅支持 PDF、TXT 和 DOCX 文件")
    
    suffix = os.path.splitext(file.filename)[1] or ""
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        task = process_document.apply_async(
            args=[tmp_path, file.filename, knowledge_base_id]
        )
        return UploadResponse(
            success=True,
            message=f"文档 {file.filename} 已提交处理任务，任务ID: {task.id}",
            chunks=0,
            file_id=task.id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提交任务失败: {str(e)}")
    finally:
        pass


@router.get("/documents")
async def list_documents(knowledge_base_id: str = Query("default")):
    documents = rag_service.list_documents(knowledge_base_id)
    total_chunks = sum(doc.get("chunks", 0) for doc in documents)
    return {"documents": documents, "total_chunks": total_chunks}


@router.delete("/documents/{file_id}")
async def delete_document(file_id: str, knowledge_base_id: str = Query("default")):
    success = rag_service.delete_document(file_id, knowledge_base_id)
    if success:
        return {"message": "删除成功", "success": True}
    raise HTTPException(status_code=404, detail="文件不存在")


@router.get("/knowledge-bases")
async def list_knowledge_bases():
    bases = rag_service.list_knowledge_bases()
    return {"knowledge_bases": bases}


@router.post("/knowledge-bases")
async def create_knowledge_base(name: str = Query(...)):
    kb = rag_service.create_knowledge_base(name)
    return {"success": True, "knowledge_base": kb}


@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    from app.celery_app import celery_app
    from celery.result import AsyncResult
    result = AsyncResult(task_id, app=celery_app)
    
    if result.ready():
        if result.successful():
            return {
                "status": "success",
                "result": result.result
            }
        else:
            return {
                "status": "failed",
                "error": str(result.info)
            }
    elif result.state == "PROCESSING":
        return {
            "status": "processing",
            "meta": result.info
        }
    else:
        return {"status": result.state.lower()}
