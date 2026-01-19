#!/usr/bin/env python3
"""
Полная версия API для Railway
"""

import os
import sys
import sqlite3
import logging
import hashlib
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Создаем FastAPI приложение
app = FastAPI(title="Telegram AutoPosting API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        
        # Создаем новую базу данных с полной схемой
        logger.info("Создаем новую базу данных...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Таблица users
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT,
                phone TEXT,
                password_hash TEXT NOT NULL,
                telegram_contact TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                is_admin BOOLEAN DEFAULT 0
            )
        ''')
        
        # Таблица subscriptions
        cursor.execute('''
            CREATE TABLE subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_date TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                payment_amount INTEGER,
                payment_date TIMESTAMP,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Таблица campaigns (упрощенная)
        cursor.execute('''
            CREATE TABLE campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                message TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица tokens (для аутентификации)
        cursor.execute('''
            CREATE TABLE tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Создаем администратора
        admin_password = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, is_admin, is_active)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin@example.com', admin_password, 1, 1))
        
        # Тестовая подписка для админа
        end_date = datetime.now() + timedelta(days=365)
        cursor.execute('''
            INSERT INTO subscriptions (user_id, end_date, is_active, notes)
            VALUES (?, ?, ?, ?)
        ''', (1, end_date, 1, 'Администраторская подписка'))
        
        # Тестовая кампания
        cursor.execute('''
            INSERT INTO campaigns (name, message)
            VALUES (?, ?)
        ''', ('Тестовая рассылка', 'Привет! Это тестовое сообщение'))
        
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
    init_database()

# Вспомогательные функции
def verify_token(token: str = Header(...)):
    """Проверка токена"""
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT u.id, u.username, u.is_admin 
        FROM tokens t
        JOIN users u ON t.user_id = u.id
        WHERE t.token = ? AND t.expires_at > datetime('now') AND u.is_active = 1
    ''', (token,))
    
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=401, detail="Неверный или истекший токен")
    
    return {"user_id": user[0], "username": user[1], "is_admin": bool(user[2])}

# Маршруты
@app.get("/")
def root():
    """Главная страница"""
    return {
        "service": "Telegram AutoPosting API",
        "status": "running",
        "version": "2.0.0",
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "production"),
        "endpoints": [
            {"method": "POST", "path": "/api/auth/register", "description": "Регистрация"},
            {"method": "POST", "path": "/api/auth/login", "description": "Вход"},
            {"method": "GET", "path": "/api/subscription/check", "description": "Проверка подписки"},
            {"method": "GET", "path": "/api/users", "description": "Список пользователей"},
            {"method": "GET", "path": "/health", "description": "Health check"}
        ]
    }

@app.get("/health")
def health():
    """Health check"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Аутентификация
@app.post("/api/auth/register")
def register(
    username: str,
    password: str,
    email: str = None,
    phone: str = None,
    telegram_contact: str = None
):
    """Регистрация пользователя"""
    try:
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        
        # Проверка существования
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Пользователь уже существует")
        
        # Хеширование пароля
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Создание пользователя
        cursor.execute('''
            INSERT INTO users (username, email, phone, password_hash, telegram_contact)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, phone, password_hash, telegram_contact))
        
        user_id = cursor.lastrowid
        
        # Тестовая подписка (1 день)
        end_date = datetime.now() + timedelta(days=1)
        cursor.execute('''
            INSERT INTO subscriptions (user_id, end_date, is_active, notes)
            VALUES (?, ?, ?, ?)
        ''', (user_id, end_date, 1, 'Тестовая подписка (1 день)'))
        
        # Генерация токена
        token = hashlib.sha256(f"{username}{datetime.now()}{os.urandom(16).hex()}".encode()).hexdigest()
        expires_at = datetime.now() + timedelta(days=7)
        
        cursor.execute('''
            INSERT INTO tokens (user_id, token, expires_at)
            VALUES (?, ?, ?)
        ''', (user_id, token, expires_at))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": "Регистрация успешна",
            "token": token,
            "user": {
                "id": user_id,
                "username": username,
                "email": email,
                "has_subscription": True,
                "subscription_end": end_date.strftime("%d.%m.%Y %H:%M"),
                "days_left": 1
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка регистрации: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")

@app.post("/api/auth/login")
def login(username: str, password: str):
    """Вход пользователя"""
    try:
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        
        # Поиск пользователя
        cursor.execute('''
            SELECT id, username, password_hash, is_admin 
            FROM users 
            WHERE username = ? AND is_active = 1
        ''', (username,))
        
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=401, detail="Неверный логин или пароль")
        
        user_id, username_db, password_hash, is_admin = user
        
        # Проверка пароля
        if hashlib.sha256(password.encode()).hexdigest() != password_hash:
            raise HTTPException(status_code=401, detail="Неверный логин или пароль")
        
        # Проверка подписки
        cursor.execute('''
            SELECT end_date 
            FROM subscriptions 
            WHERE user_id = ? AND is_active = 1 AND end_date > datetime('now')
            ORDER BY end_date DESC LIMIT 1
        ''', (user_id,))
        
        sub = cursor.fetchone()
        
        # Генерация токена
        token = hashlib.sha256(f"{username}{datetime.now()}{os.urandom(16).hex()}".encode()).hexdigest()
        expires_at = datetime.now() + timedelta(days=7)
        
        cursor.execute('''
            INSERT INTO tokens (user_id, token, expires_at)
            VALUES (?, ?, ?)
        ''', (user_id, token, expires_at))
        
        conn.commit()
        
        response = {
            "success": True,
            "message": "Вход успешен",
            "token": token,
            "user": {
                "id": user_id,
                "username": username_db,
                "is_admin": bool(is_admin),
                "has_subscription": sub is not None
            }
        }
        
        if sub:
            end_date = datetime.strptime(sub[0], '%Y-%m-%d %H:%M:%S')
            days_left = (end_date - datetime.now()).days
            response["user"]["subscription_end"] = end_date.strftime("%d.%m.%Y %H:%M")
            response["user"]["days_left"] = days_left
        
        conn.close()
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка входа: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")

@app.get("/api/subscription/check")
def check_subscription(auth: dict = Depends(verify_token)):
    """Проверить подписку"""
    try:
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.end_date, s.is_active
            FROM subscriptions s
            WHERE s.user_id = ? AND s.is_active = 1
            ORDER BY s.end_date DESC LIMIT 1
        ''', (auth["user_id"],))
        
        sub = cursor.fetchone()
        conn.close()
        
        if sub and sub[1] == 1:
            end_date = datetime.strptime(sub[0], '%Y-%m-%d %H:%M:%S')
            days_left = (end_date - datetime.now()).days
            
            if days_left >= 0:
                return {
                    "has_subscription": True,
                    "subscription": {
                        "end_date": end_date.strftime("%d.%m.%Y %H:%M"),
                        "days_left": days_left,
                        "is_active": True
                    },
                    "user": {
                        "id": auth["user_id"],
                        "username": auth["username"]
                    }
                }
        
        return {
            "has_subscription": False,
            "message": "Нет активной подписки",
            "user": {
                "id": auth["user_id"],
                "username": auth["username"]
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка проверки подписки: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")

# Остальные маршруты...
@app.get("/api/users")
def get_users(auth: dict = Depends(verify_token)):
    """Получить список пользователей (только для админов)"""
    if not auth["is_admin"]:
        raise HTTPException(status_code=403, detail="Требуются права администратора")
    
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, username, email, phone, created_at, is_active, is_admin
        FROM users
        ORDER BY id
    ''')
    
    users = cursor.fetchall()
    conn.close()
    
    return {
        "success": True,
        "users": [
            {
                "id": u[0],
                "username": u[1],
                "email": u[2],
                "phone": u[3],
                "created_at": u[4],
                "is_active": bool(u[5]),
                "is_admin": bool(u[6])
            }
            for u in users
        ]
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"🚀 Запуск сервера на порту {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)