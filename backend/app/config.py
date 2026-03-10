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
    
    class Config:
        env_file = ".env"


settings = Settings()
