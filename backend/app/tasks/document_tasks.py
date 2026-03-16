from celery import Task
from app.celery_app import celery_app
from app.services.rag import rag_service
import os
import tempfile


class DocumentProcessingTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print(f"Task {task_id} failed: {exc}")


@celery_app.task(base=DocumentProcessingTask, bind=True)
def process_document(self, file_path: str, file_name: str, knowledge_base_id: str = "default"):
    try:
        self.update_state(state="PROCESSING", meta={"status": "正在处理文档...", "progress": 10})
        
        result = rag_service.add_documents(file_path, knowledge_base_id)
        
        self.update_state(state="PROCESSING", meta={"status": "文档处理完成", "progress": 100})
        
        return {
            "success": True,
            "file_id": result["file_id"],
            "file_name": file_name,
            "chunks": result["chunks"],
            "knowledge_base_id": knowledge_base_id
        }
    except Exception as e:
        self.update_state(state="FAILURE", meta={"error": str(e)})
        raise


@celery_app.task
def delete_document_task(file_id: str, knowledge_base_id: str = "default"):
    try:
        success = rag_service.delete_document(file_id, knowledge_base_id)
        return {"success": success, "file_id": file_id}
    except Exception as e:
        return {"success": False, "error": str(e)}
