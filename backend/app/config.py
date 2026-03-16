from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    dashscope_api_key: str = "your_api_key_here"
    
    chroma_persist_directory: str = "./chroma_db"
    
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    chunk_size: int = 500
    chunk_overlap: int = 50
    max_iterations: int = 5
    
    history_file: str = "./chat_history.json"
    
    redis_url: str = "redis://localhost:6379/0"
    celery_task_track_started: bool = True
    celery_task_time_limit: int = 1800
    
    bm25_weight: float = 0.3
    vector_weight: float = 0.7
    rerank_top_k: int = 5
    hybrid_top_k: int = 10
    
    knowledge_base_dir: str = "./knowledge_bases"
    
    class Config:
        env_file = ".env"


settings = Settings()
