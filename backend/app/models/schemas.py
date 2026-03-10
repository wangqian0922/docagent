from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    message: str
    use_history: bool = True


class ChatResponse(BaseModel):
    message: str
    sources: Optional[list] = None


class UploadResponse(BaseModel):
    success: bool
    message: str
    chunks: int = 0
