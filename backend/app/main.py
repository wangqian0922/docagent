from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import upload, chat
import uvicorn

app = FastAPI(title="DocAgent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(chat.router, prefix="/api", tags=["chat"])


@app.get("/")
async def root():
    return {"message": "DocAgent API is running"}


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)