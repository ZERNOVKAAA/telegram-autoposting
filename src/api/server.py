#!/usr/bin/env python3
"""
Telegram AutoPosting API - Полная версия с фронтендом
"""

import os
import sys
import sqlite3
import hashlib
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException, Depends, status, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse, RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.templating import Jinja2Templates
import uvicorn

# Настройка пути для импортов
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Конфигурация
SECRET_KEY = "telegram-autoposting-secret-key-2024-change-this-in-production"
DB_PATH = "data/database.db"

app = FastAPI(
    title="Telegram AutoPosting API",
    description="API для системы автоматической публикации в Telegram",
    version="3.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Настройка CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене укажите домен фронтенда
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Монтирование статических файлов фронтенда
frontend_path = os.path.join(os.path.dirname(__file__), "../../frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
    app.mount("/js", StaticFiles(directory=os.path.join(frontend_path, "js")), name="js")
    app.mount("/css", StaticFiles(directory=os.path.join(frontend_path, "css")), name="css")
    print(f"✅ Фронтенд подключен: {frontend_path}")
else:
    print(f"⚠️ Папка фронтенда не найдена: {frontend_path}")
    frontend_path = None

# Шаблоны для рендеринга HTML
templates_path = os.path.join(frontend_path, "templates") if frontend_path else None
if templates_path and os.path.exists(templates_path):
    templates = Jinja2Templates(directory=templates_path)
else:
    templates = None

# Безопасность
security = HTTPBearer()

# Инициализация базы данных
def init_database():
    """Инициализировать базу данных"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            password_hash TEXT NOT NULL,
            phone TEXT,
            is_admin BOOLEAN DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            telegram_contact TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица подписок
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_date TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            payment_amount INTEGER,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Таблица Telegram аккаунтов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS telegram_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            phone_number TEXT,
            session_string TEXT,
            is_authenticated BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Таблица рассылок
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            message TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Создаем администратора по умолчанию, если его нет
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        password_hash = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute('''
            INSERT INTO users (username, password_hash, is_admin, is_active) 
            VALUES (?, ?, 1, 1)
        ''', ('admin', password_hash))
        print("✅ Администратор создан: admin / admin123")
    
    conn.commit()
    conn.close()
    print("✅ База данных инициализирована")

# Инициализируем БД при старте
init_database()

# Вспомогательные функции
def get_db():
    """Получить подключение к БД"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def hash_password(password: str) -> str:
    """Хешировать пароль"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_token(user_id: int, username: str, is_admin: bool = False) -> str:
    """Создать JWT токен"""
    payload = {
        "user_id": user_id,
        "username": username,
        "is_admin": is_admin,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Верифицировать JWT токен"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Получить текущего пользователя из токена"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или истекший токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload

# Маршруты для фронтенда
@app.get("/", response_class=HTMLResponse)
async def serve_frontend(request: Request):
    """Главная страница фронтенда"""
    if frontend_path and os.path.exists(os.path.join(frontend_path, "index.html")):
        return FileResponse(os.path.join(frontend_path, "index.html"))
    return HTMLResponse("""
        <html>
            <head><title>Telegram AutoPosting</title></head>
            <body>
                <h1>Telegram AutoPosting System</h1>
                <p>API сервер работает. Фронтенд не настроен.</p>
                <p><a href="/api/docs">Документация API</a></p>
            </body>
        </html>
    """)

@app.get("/login", response_class=HTMLResponse)
async def serve_login():
    """Страница входа"""
    if frontend_path and os.path.exists(os.path.join(frontend_path, "login.html")):
        return FileResponse(os.path.join(frontend_path, "login.html"))
    return RedirectResponse(url="/api/docs")

@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    """Личный кабинет"""
    if frontend_path and os.path.exists(os.path.join(frontend_path, "dashboard.html")):
        return FileResponse(os.path.join(frontend_path, "dashboard.html"))
    return RedirectResponse(url="/login")

@app.get("/admin", response_class=HTMLResponse)
async def serve_admin():
    """Админ-панель"""
    if frontend_path and os.path.exists(os.path.join(frontend_path, "admin.html")):
        return FileResponse(os.path.join(frontend_path, "admin.html"))
    return RedirectResponse(url="/login")

# Основные API эндпоинты
@app.get("/api/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {
        "status": "healthy",
        "service": "telegram-autoposting",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "3.0.0",
        "database": "connected"
    }

@app.get("/api/status")
async def system_status():
    """Статус системы"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            # Статистика пользователей
            cursor.execute("SELECT COUNT(*) FROM users")
            users_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM campaigns")
            campaigns_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM telegram_accounts")
            accounts_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM subscriptions WHERE is_active = 1")
            active_subs = cursor.fetchone()[0]
            
            return {
                "status": "ok",
                "database": {
                    "users": users_count,
                    "campaigns": campaigns_count,
                    "telegram_accounts": accounts_count,
                    "active_subscriptions": active_subs,
                    "connection": "established"
                },
                "server": {
                    "environment": os.getenv("RAILWAY_ENVIRONMENT", "development"),
                    "python_version": sys.version,
                    "timestamp": datetime.now().isoformat()
                }
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Аутентификация
@app.post("/api/auth/login")
async def login(username: str = Form(...), password: str = Form(...)):
    """Вход в систему"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, password_hash, is_admin FROM users WHERE username = ? AND is_active = 1",
                (username,)
            )
            user = cursor.fetchone()
            
            if not user:
                raise HTTPException(status_code=400, detail="Пользователь не найден")
            
            user_id, username, password_hash, is_admin = user
            
            # Проверка пароля
            if hash_password(password) != password_hash:
                raise HTTPException(status_code=400, detail="Неверный пароль")
            
            # Создание токена
            token = create_token(user_id, username, bool(is_admin))
            
            # Проверка подписки
            cursor.execute(
                "SELECT COUNT(*) FROM subscriptions WHERE user_id = ? AND is_active = 1 AND end_date > datetime('now')",
                (user_id,)
            )
            has_subscription = cursor.fetchone()[0] > 0
            
            return {
                "status": "success",
                "token": token,
                "user": {
                    "id": user_id,
                    "username": username,
                    "is_admin": bool(is_admin)
                },
                "subscription": {
                    "has_subscription": has_subscription,
                    "message": "Подписка активна" if has_subscription else "Нет активной подписки"
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")

@app.post("/api/auth/register")
async def register(
    username: str = Form(...),
    password: str = Form(...),
    email: Optional[str] = Form(None),
    telegram_contact: Optional[str] = Form(None)
):
    """Регистрация нового пользователя"""
    try:
        # Проверка длины пароля
        if len(password) < 6:
            raise HTTPException(status_code=400, detail="Пароль должен быть не менее 6 символов")
        
        # Проверка существующего пользователя
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
            if cursor.fetchone()[0] > 0:
                raise HTTPException(status_code=400, detail="Пользователь уже существует")
            
            # Хеширование пароля
            password_hash = hash_password(password)
            
            # Создание пользователя
            cursor.execute(
                """
                INSERT INTO users (username, email, password_hash, telegram_contact, is_active)
                VALUES (?, ?, ?, ?, 1)
                """,
                (username, email, password_hash, telegram_contact)
            )
            user_id = cursor.lastrowid
            
            # Создание токена
            token = create_token(user_id, username, False)
            
            # Создаем тестовую подписку на 1 день
            end_date = datetime.now() + timedelta(days=1)
            cursor.execute(
                """
                INSERT INTO subscriptions (user_id, end_date, is_active, notes)
                VALUES (?, ?, 1, 'Тестовая подписка (1 день)')
                """,
                (user_id, end_date.isoformat())
            )
            
            conn.commit()
            
            return {
                "status": "success",
                "token": token,
                "user": {
                    "id": user_id,
                    "username": username,
                    "is_admin": False
                },
                "message": "Регистрация успешна"
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка регистрации: {str(e)}")

@app.get("/api/subscription/check")
async def check_subscription(current_user: dict = Depends(get_current_user)):
    """Проверить статус подписки"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            # Ищем активную подписку
            cursor.execute(
                """
                SELECT id, start_date, end_date, is_active
                FROM subscriptions 
                WHERE user_id = ? AND is_active = 1 AND end_date > datetime('now')
                ORDER BY end_date DESC LIMIT 1
                """,
                (current_user["user_id"],)
            )
            subscription = cursor.fetchone()
            
            if subscription:
                sub_id, start_date, end_date, is_active = subscription
                
                # Вычисляем оставшиеся дни
                if isinstance(end_date, str):
                    end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                else:
                    end_datetime = datetime.fromisoformat(end_date)
                
                days_left = (end_datetime - datetime.utcnow()).days
                days_left = max(0, days_left)
                
                return {
                    "has_subscription": True,
                    "subscription": {
                        "id": sub_id,
                        "start_date": start_date,
                        "end_date": end_date,
                        "days_left": days_left,
                        "is_active": bool(is_active)
                    },
                    "user": {
                        "id": current_user["user_id"],
                        "username": current_user["username"],
                        "is_admin": current_user.get("is_admin", False)
                    }
                }
            else:
                return {
                    "has_subscription": False,
                    "message": "Нет активной подписки",
                    "user": {
                        "id": current_user["user_id"],
                        "username": current_user["username"],
                        "is_admin": current_user.get("is_admin", False)
                    }
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка проверки подписки: {str(e)}")

# Управление пользователями (только для админов)
@app.get("/api/admin/stats")
async def admin_stats(current_user: dict = Depends(get_current_user)):
    """Статистика для админ-панели"""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Требуются права администратора")
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            # Общая статистика
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
            active_users = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM subscriptions WHERE is_active = 1")
            total_subscriptions = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM campaigns")
            total_campaigns = cursor.fetchone()[0]
            
            # Активные подписки
            cursor.execute("SELECT COUNT(*) FROM subscriptions WHERE is_active = 1 AND end_date > datetime('now')")
            active_subscriptions = cursor.fetchone()[0]
            
            # Последние пользователи
            cursor.execute(
                "SELECT id, username, email, created_at FROM users ORDER BY id DESC LIMIT 10"
            )
            recent_users = [
                {
                    "id": row[0],
                    "username": row[1],
                    "email": row[2],
                    "created_at": row[3]
                }
                for row in cursor.fetchall()
            ]
            
            return {
                "success": True,
                "stats": {
                    "total_users": total_users,
                    "active_users": active_users,
                    "total_subscriptions": total_subscriptions,
                    "active_subscriptions": active_subscriptions,
                    "total_campaigns": total_campaigns
                },
                "recent_users": recent_users
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения статистики: {str(e)}")

@app.get("/api/admin/users")
async def get_users(current_user: dict = Depends(get_current_user)):
    """Получить список всех пользователей (админ)"""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Требуются права администратора")
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT u.*, 
                       (SELECT COUNT(*) FROM subscriptions s 
                        WHERE s.user_id = u.id AND s.is_active = 1 AND s.end_date > datetime('now')) as has_subscription
                FROM users u 
                ORDER BY u.id DESC
            """)
            
            users = []
            for row in cursor.fetchall():
                users.append({
                    "id": row["id"],
                    "username": row["username"],
                    "email": row["email"],
                    "phone": row["phone"],
                    "is_admin": bool(row["is_admin"]),
                    "is_active": bool(row["is_active"]),
                    "telegram_contact": row["telegram_contact"],
                    "created_at": row["created_at"],
                    "has_subscription": bool(row["has_subscription"])
                })
            
            return {"success": True, "users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения пользователей: {str(e)}")

# Основные API эндпоинты
@app.get("/api/users")
async def get_all_users():
    """Получить список пользователей"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, phone, created_at FROM users ORDER BY id")
            users = cursor.fetchall()
            
            return {
                "status": "success",
                "count": len(users),
                "users": [
                    {
                        "id": user["id"],
                        "username": user["username"],
                        "phone": user["phone"],
                        "created_at": user["created_at"]
                    }
                    for user in users
                ]
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/users")
async def create_user(username: str = Form(...), phone: str = Form(...)):
    """Создать нового пользователя"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, phone) VALUES (?, ?)",
                (username, phone)
            )
            conn.commit()
            user_id = cursor.lastrowid
            
            return {
                "status": "created",
                "user_id": user_id,
                "username": username,
                "phone": phone
            }
    except sqlite3.IntegrityError:
        return {"status": "error", "message": "Пользователь уже существует"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/campaigns")
async def get_campaigns():
    """Получить список рассылок"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, message, status, created_at FROM campaigns ORDER BY id")
            campaigns = cursor.fetchall()
            
            return {
                "status": "success",
                "count": len(campaigns),
                "campaigns": [
                    {
                        "id": campaign["id"],
                        "name": campaign["name"],
                        "message": campaign["message"],
                        "status": campaign["status"],
                        "created_at": campaign["created_at"]
                    }
                    for campaign in campaigns
                ]
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/campaigns")
async def create_campaign(name: str = Form(...), message: str = Form(...)):
    """Создать новую рассылку"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO campaigns (name, message) VALUES (?, ?)",
                (name, message)
            )
            conn.commit()
            campaign_id = cursor.lastrowid
            
            return {
                "status": "created",
                "campaign_id": campaign_id,
                "name": name,
                "message": message
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Простые эндпоинты (из старой версии)
@app.get("/", include_in_schema=False)
async def root():
    """Главная страница API"""
    return {
        "message": "Telegram AutoPosting API", 
        "status": "online",
        "version": "3.0.0",
        "endpoints": [
            "/api/health",
            "/api/status",
            "/api/docs",
            "/api/auth/login",
            "/api/auth/register",
            "/api/users",
            "/api/campaigns",
            "/api/admin/stats (admin only)"
        ]
    }

@app.get("/health", include_in_schema=False)
async def health():
    """Проверка здоровья"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/test", include_in_schema=False)
async def test():
    """Тестовый эндпоинт"""
    return {"test": "ok", "timestamp": datetime.utcnow().isoformat()}

# Запуск сервера
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print("=" * 60)
    print("🚀 Telegram AutoPosting API v3.0")
    print("=" * 60)
    print(f"📍 Порт: {port}")
    print(f"🌐 API: http://localhost:{port}/api/docs")
    print(f"🔑 Авторизация: JWT токены")
    print(f"📁 Фронтенд: {'Подключен' if frontend_path else 'Не найден'}")
    print(f"🗄️ База данных: {DB_PATH}")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=True
    )