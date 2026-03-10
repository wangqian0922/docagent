from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from typing import List, Optional
import os
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
        self._load_vectorstore()
    
    def _load_vectorstore(self):
        if os.path.exists(settings.chroma_persist_directory):
            self.vectorstore = Chroma(
                persist_directory=settings.chroma_persist_directory,
                embedding_function=self.embeddings
            )
    
    def load_document(self, file_path: str) -> List:
        if file_path.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        else:
            loader = TextLoader(file_path, encoding='utf-8')
        
        documents = loader.load()
        splits = self.text_splitter.split_documents(documents)
        return splits
    
    def add_documents(self, file_path: str) -> int:
        splits = self.load_document(file_path)
        
        self.vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=settings.chroma_persist_directory
        )
        self.vectorstore.persist()
        return len(splits)
    
    def get_retriever(self, k: int = 3):
        if self.vectorstore is None:
            return None
        return self.vectorstore.as_retriever(
            search_kwargs={"k": k}
        )
    
    def clear(self):
        if os.path.exists(settings.chroma_persist_directory):
            import shutil
            shutil.rmtree(settings.chroma_persist_directory)
        self.vectorstore = None


rag_service = RAGService()
