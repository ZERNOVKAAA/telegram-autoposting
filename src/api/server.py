from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel  # ← ДОБАВЬТЕ ЭТУ СТРОКУ!
import uvicorn
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Telegram AutoPosting API")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Verify2FARequest(BaseModel):
    code: str

@app.get("/")
async def root():
    return {
        "message": "Telegram AutoPosting API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "ok", 
        "service": "telegram-autoposting",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/api/test")
async def test_endpoint():
    return {"message": "API работает корректно"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000, reload=True)