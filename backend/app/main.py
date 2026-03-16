from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import upload, chat, monitor
import uvicorn

app = FastAPI(title="DocAgent API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(monitor.router, prefix="/api", tags=["monitor"])

@app.get("/")
async def root():
    return {"message": "DocAgent API v2.0 is running", "version": "2.0.0"}

@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
