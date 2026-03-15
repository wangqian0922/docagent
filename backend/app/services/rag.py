from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from typing import List, Optional, Dict
import os
import json
import uuid
from datetime import datetime
from app.config import settings


class RAGService:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding_model
        )
        self.vectorstore: Optional[Chroma] = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", "。", " ", ""]
        )
        self.file_registry_path = os.path.join(
            os.path.dirname(settings.chroma_persist_directory),
            "file_registry.json"
        )
        self._load_vectorstore()
    
    def _load_vectorstore(self):
        if os.path.exists(settings.chroma_persist_directory):
            self.vectorstore = Chroma(
                persist_directory=settings.chroma_persist_directory,
                embedding_function=self.embeddings
            )
    
    def _load_file_registry(self) -> List[Dict]:
        if os.path.exists(self.file_registry_path):
            try:
                with open(self.file_registry_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_file_registry(self, registry: List[Dict]):
        with open(self.file_registry_path, 'w', encoding='utf-8') as f:
            json.dump(registry, f, ensure_ascii=False, indent=2)
    
    def load_document(self, file_path: str) -> List:
        if file_path.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        else:
            loader = TextLoader(file_path, encoding='utf-8')
        
        documents = loader.load()
        splits = self.text_splitter.split_documents(documents)
        return splits
    
    def add_documents(self, file_path: str) -> Dict:
        splits = self.load_document(file_path)
        
        file_id = str(uuid.uuid4())
        file_name = os.path.basename(file_path)
        
        for split in splits:
            split.metadata['file_id'] = file_id
            split.metadata['file_name'] = file_name
        
        if self.vectorstore is None:
            self.vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=self.embeddings,
                persist_directory=settings.chroma_persist_directory
            )
        else:
            self.vectorstore.add_documents(splits)
        
        self.vectorstore.persist()
        
        registry = self._load_file_registry()
        registry.append({
            "file_id": file_id,
            "file_name": file_name,
            "chunks": len(splits),
            "upload_time": datetime.now().isoformat()
        })
        self._save_file_registry(registry)
        
        return {"file_id": file_id, "chunks": len(splits)}
    
    def get_retriever(self, k: int = 3):
        if self.vectorstore is None:
            return None
        return self.vectorstore.as_retriever(
            search_kwargs={"k": k}
        )
    
    def list_documents(self) -> List[Dict]:
        return self._load_file_registry()
    
    def delete_document(self, file_id: str) -> bool:
        registry = self._load_file_registry()
        file_info = next((f for f in registry if f["file_id"] == file_id), None)
        
        if not file_info:
            return False
        
        if self.vectorstore is not None:
            self.vectorstore.delete(where={"file_id": file_id})
            self.vectorstore.persist()
        
        registry = [f for f in registry if f["file_id"] != file_id]
        self._save_file_registry(registry)
        
        return True
    
    def clear(self):
        if os.path.exists(settings.chroma_persist_directory):
            import shutil
            shutil.rmtree(settings.chroma_persist_directory)
        self.vectorstore = None
        if os.path.exists(self.file_registry_path):
            os.remove(self.file_registry_path)


rag_service = RAGService()
