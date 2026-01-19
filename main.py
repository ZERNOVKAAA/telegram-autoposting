#!/usr/bin/env python3
"""
Telegram AutoPosting - Упрощенная рабочая версия для Railway
"""

import os
import sys
import sqlite3
import logging
from fastapi import FastAPI
import uvicorn

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Создаем FastAPI приложение
app = FastAPI(title="Telegram AutoPosting API", version="1.0.0")

def init_database():
    """Инициализировать базу данных"""
    try:
        db_path = 'data/database.db'
        
        # Удаляем старую базу данных если она есть
        if os.path.exists(db_path):
            logger.info("Удаляем старую базу данных...")
            os.remove(db_path)
        
        # Создаем директорию для данных
        os.makedirs("data", exist_ok=True)
        
        # Создаем новую базу данных
        logger.info("Создаем новую базу данных...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Создаем таблицы с простой структурой
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                message TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Добавляем тестовые данные
        cursor.execute('INSERT INTO users (username, phone) VALUES (?, ?)', 
                      ('admin', '+79991234567'))
        cursor.execute('INSERT INTO campaigns (name, message) VALUES (?, ?)', 
                      ('Тестовая рассылка', 'Привет! Это тестовое сообщение'))
        
        conn.commit()
        conn.close()
        
        logger.info("✅ База данных создана успешно")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка создания БД: {e}")
        return False

# Инициализируем БД при запуске
@app.on_event("startup")
def startup_event():
    """Действия при запуске приложения"""
    logger.info("🚀 Запуск Telegram AutoPosting API...")
    
    # Проверяем основные зависимости
    try:
        import fastapi
        import uvicorn
        logger.info("✅ Зависимости проверены")
    except ImportError as e:
        logger.error(f"❌ Отсутствует зависимость: {e}")
    
    # Инициализируем БД
    init_database()
    
    # Получаем порт из переменных окружения Railway
    port = int(os.getenv("PORT", 8000))
    logger.info(f"🌐 Сервер будет запущен на порту: {port}")

@app.get("/")
def root():
    """Главная страница"""
    return {
        "service": "Telegram AutoPosting",
        "status": "running",
        "version": "1.0.0",
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "development"),
        "endpoints": {
            "root": "/",
            "health": "/health",
            "status": "/status",
            "users": "/api/users",
            "campaigns": "/api/campaigns",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health")
def health_check():
    """Проверка здоровья сервиса"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "service": "telegram-autoposting"
    }

@app.get("/status")
def status():
    """Статус системы"""
    try:
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        
        # Получаем статистику
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM campaigns")
        campaigns_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT sqlite_version()")
        sqlite_version = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "status": "ok",
            "database": {
                "users": users_count,
                "campaigns": campaigns_count,
                "sqlite_version": sqlite_version,
                "connection": "established"
            },
            "server": {
                "port": int(os.getenv("PORT", 8000)),
                "environment": os.getenv("RAILWAY_ENVIRONMENT", "development"),
                "python_version": sys.version
            }
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/users")
def get_users():
    """Получить список пользователей"""
    try:
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, phone, created_at FROM users ORDER BY id")
        users = cursor.fetchall()
        conn.close()
        
        return {
            "status": "success",
            "count": len(users),
            "users": [
                {
                    "id": user[0],
                    "username": user[1],
                    "phone": user[2],
                    "created_at": user[3]
                }
                for user in users
            ]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/campaigns")
def get_campaigns():
    """Получить список рассылок"""
    try:
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, message, status, created_at FROM campaigns ORDER BY id")
        campaigns = cursor.fetchall()
        conn.close()
        
        return {
            "status": "success",
            "count": len(campaigns),
            "campaigns": [
                {
                    "id": campaign[0],
                    "name": campaign[1],
                    "message": campaign[2],
                    "status": campaign[3],
                    "created_at": campaign[4]
                }
                for campaign in campaigns
            ]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/users")
def create_user(username: str, phone: str):
    """Создать нового пользователя"""
    try:
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, phone) VALUES (?, ?)",
            (username, phone)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        return {
            "status": "created",
            "user_id": user_id,
            "username": username,
            "phone": phone
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/campaigns")
def create_campaign(name: str, message: str):
    """Создать новую рассылку"""
    try:
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO campaigns (name, message) VALUES (?, ?)",
            (name, message)
        )
        conn.commit()
        campaign_id = cursor.lastrowid
        conn.close()
        
        return {
            "status": "created",
            "campaign_id": campaign_id,
            "name": name,
            "message": message
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # Запуск сервера
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"
    
    logger.info(f"🚀 Запуск сервера на {host}:{port}")
    logger.info(f"📚 Документация доступна по адресу: http://{host}:{port}/docs")
    logger.info(f"🏥 Health check: http://{host}:{port}/health")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )