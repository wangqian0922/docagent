from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
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
        self.vectorstores: Dict[str, Chroma] = {}
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", "。", " ", ""]
        )
        self.knowledge_base_dir = settings.knowledge_base_dir
        os.makedirs(self.knowledge_base_dir, exist_ok=True)
        self._init_default_knowledge_base()
    
    def _init_default_knowledge_base(self):
        if not os.path.exists(os.path.join(self.knowledge_base_dir, "default")):
            os.makedirs(os.path.join(self.knowledge_base_dir, "default"), exist_ok=True)
    
    def _get_persist_directory(self, knowledge_base_id: str = "default") -> str:
        return os.path.join(self.knowledge_base_dir, knowledge_base_id, "chroma_db")
    
    def _get_registry_path(self, knowledge_base_id: str = "default") -> str:
        return os.path.join(self.knowledge_base_dir, knowledge_base_id, "file_registry.json")
    
    def _load_vectorstore(self, knowledge_base_id: str = "default") -> Optional[Chroma]:
        persist_dir = self._get_persist_directory(knowledge_base_id)
        if os.path.exists(persist_dir):
            return Chroma(
                persist_directory=persist_dir,
                embedding_function=self.embeddings
            )
        return None
    
    def _get_vectorstore(self, knowledge_base_id: str = "default") -> Chroma:
        if knowledge_base_id not in self.vectorstores:
            self.vectorstores[knowledge_base_id] = self._load_vectorstore(knowledge_base_id)
        return self.vectorstores[knowledge_base_id]
    
    def _load_file_registry(self, knowledge_base_id: str = "default") -> List[Dict]:
        registry_path = self._get_registry_path(knowledge_base_id)
        if os.path.exists(registry_path):
            try:
                with open(registry_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_file_registry(self, registry: List[Dict], knowledge_base_id: str = "default"):
        registry_path = self._get_registry_path(knowledge_base_id)
        os.makedirs(os.path.dirname(registry_path), exist_ok=True)
        with open(registry_path, 'w', encoding='utf-8') as f:
            json.dump(registry, f, ensure_ascii=False, indent=2)
    
    def load_document(self, file_path: str) -> List:
        if file_path.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        elif file_path.endswith('.docx'):
            loader = Docx2txtLoader(file_path)
        else:
            loader = TextLoader(file_path, encoding='utf-8')
        
        documents = loader.load()
        splits = self.text_splitter.split_documents(documents)
        return splits
    
    def add_documents(self, file_path: str, knowledge_base_id: str = "default") -> Dict:
        splits = self.load_document(file_path)
        
        file_id = str(uuid.uuid4())
        file_name = os.path.basename(file_path)
        
        for split in splits:
            split.metadata['file_id'] = file_id
            split.metadata['file_name'] = file_name
            split.metadata['knowledge_base_id'] = knowledge_base_id
        
        persist_dir = self._get_persist_directory(knowledge_base_id)
        os.makedirs(persist_dir, exist_ok=True)
        
        vectorstore = self._get_vectorstore(knowledge_base_id)
        
        if vectorstore is None:
            vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=self.embeddings,
                persist_directory=persist_dir
            )
        else:
            vectorstore.add_documents(splits)
        
        self.vectorstores[knowledge_base_id] = vectorstore
        
        registry = self._load_file_registry(knowledge_base_id)
        registry.append({
            "file_id": file_id,
            "file_name": file_name,
            "chunks": len(splits),
            "upload_time": datetime.now().isoformat()
        })
        self._save_file_registry(registry, knowledge_base_id)
        
        return {"file_id": file_id, "chunks": len(splits)}
    
    def get_retriever(self, k: int = 3, knowledge_base_id: str = "default"):
        vectorstore = self._get_vectorstore(knowledge_base_id)
        if vectorstore is None:
            return None
        return vectorstore.as_retriever(
            search_kwargs={"k": k}
        )
    
    def list_documents(self, knowledge_base_id: str = "default") -> List[Dict]:
        return self._load_file_registry(knowledge_base_id)
    
    def delete_document(self, file_id: str, knowledge_base_id: str = "default") -> bool:
        registry = self._load_file_registry(knowledge_base_id)
        file_info = next((f for f in registry if f["file_id"] == file_id), None)
        
        if not file_info:
            return False
        
        vectorstore = self._get_vectorstore(knowledge_base_id)
        if vectorstore is not None:
            try:
                vectorstore.delete(where={"file_id": file_id})
            except:
                pass
        
        registry = [f for f in registry if f["file_id"] != file_id]
        self._save_file_registry(registry, knowledge_base_id)
        
        return True
    
    def list_knowledge_bases(self) -> List[Dict]:
        bases = []
        if os.path.exists(self.knowledge_base_dir):
            for kb_id in os.listdir(self.knowledge_base_dir):
                kb_path = os.path.join(self.knowledge_base_dir, kb_id)
                if os.path.isdir(kb_path):
                    registry = self._load_file_registry(kb_id)
                    total_chunks = sum(doc.get("chunks", 0) for doc in registry)
                    bases.append({
                        "id": kb_id,
                        "name": kb_id,
                        "documents": len(registry),
                        "total_chunks": total_chunks
                    })
        if not bases:
            bases.append({
                "id": "default",
                "name": "default",
                "documents": 0,
                "total_chunks": 0
            })
        return bases
    
    def create_knowledge_base(self, name: str) -> Dict:
        kb_path = os.path.join(self.knowledge_base_dir, name)
        os.makedirs(kb_path, exist_ok=True)
        self._save_file_registry([], name)
        return {"id": name, "name": name}
    
    def clear(self, knowledge_base_id: str = "default"):
        persist_dir = self._get_persist_directory(knowledge_base_id)
        if os.path.exists(persist_dir):
            import shutil
            shutil.rmtree(persist_dir)
        self.vectorstores[knowledge_base_id] = None
        registry_path = self._get_registry_path(knowledge_base_id)
        if os.path.exists(registry_path):
            os.remove(registry_path)


rag_service = RAGService()
