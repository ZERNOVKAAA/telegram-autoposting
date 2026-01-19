#!/usr/bin/env python3
"""
Railway App - специальная версия для Railway
"""

import os
import sys
import logging
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Создаем FastAPI приложение
app = FastAPI(title="Telegram AutoPosting", version="2.0.0")

# Пути
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Проверяем существование фронтенда
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
    templates = Jinja2Templates(directory=FRONTEND_DIR)
    logger.info(f"✅ Фронтенд найден: {FRONTEND_DIR}")
else:
    logger.warning(f"⚠️ Фронтенд не найден: {FRONTEND_DIR}")
    templates = None

@app.get("/")
async def root():
    """Главная страница"""
    if templates and os.path.exists(os.path.join(FRONTEND_DIR, "index.html")):
        return templates.TemplateResponse("index.html", {"request": {}})
    
    # Если фронтенда нет, вернем JSON
    return JSONResponse({
        "service": "Telegram AutoPosting",
        "status": "running",
        "version": "2.0.0",
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "production"),
        "message": "Фронтенд не найден. Используйте API endpoints.",
        "endpoints": {
            "api_docs": "/docs",
            "health": "/health",
            "status": "/status",
            "users": "/api/users",
            "campaigns": "/api/campaigns"
        }
    })

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "telegram-autoposting"}

@app.get("/status")
async def status():
    return {
        "status": "running",
        "frontend_available": os.path.exists(FRONTEND_DIR),
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "production")
    }

# API endpoints (упрощенные версии)
@app.get("/api/users")
async def get_users():
    return {"users": [], "count": 0, "status": "success"}

@app.get("/api/campaigns")
async def get_campaigns():
    return {"campaigns": [], "count": 0, "status": "success"}

# Статический контент
@app.get("/{path:path}")
async def serve_frontend(path: str):
    """Отдавать файлы из папки фронтенда"""
    if not os.path.exists(FRONTEND_DIR):
        return JSONResponse({"error": "Frontend not found"}, status_code=404)
    
    file_path = os.path.join(FRONTEND_DIR, path)
    
    # Если это файл - отдать его
    if os.path.isfile(file_path):
        return HTMLResponse(open(file_path, 'r', encoding='utf-8').read())
    
    # Если это папка - ищем index.html
    index_path = os.path.join(FRONTEND_DIR, path, "index.html")
    if os.path.isfile(index_path):
        return HTMLResponse(open(index_path, 'r', encoding='utf-8').read())
    
    # Если ничего не найдено - вернуть главный index.html
    main_index = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.isfile(main_index):
        return HTMLResponse(open(main_index, 'r', encoding='utf-8').read())
    
    return JSONResponse({"error": "Not found"}, status_code=404)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    logger.info(f"🚀 Запуск Railway приложения на порту {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)