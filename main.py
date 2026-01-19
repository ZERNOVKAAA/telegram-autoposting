#!/usr/bin/env python3
"""
Telegram AutoPosting - Полная версия с фронтендом и исправлением БД
"""

import sys
import os
import logging
import threading
import time
import sqlite3
import asyncio
from datetime import datetime

# Для запуска сервера
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
import uvicorn
import jwt
import hashlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Глобальные переменные
SECRET_KEY = "telegram-autoposting-secret-key-2024"  # Замените в продакшене

class DatabaseManager:
    """Менеджер базы данных для фронтенда"""
    
    def __init__(self):
        self.db_path = 'data/database.db'
        self.init_database()
    
    def init_database(self):
        """Инициализировать базу данных для фронтенда"""
        os.makedirs("data", exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица пользователей с паролями для аутентификации
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
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)

db_manager = DatabaseManager()

def hash_password(password: str) -> str:
    """Хешировать пароль"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверить пароль"""
    return hash_password(plain_password) == hashed_password

def create_jwt_token(user_id: int, username: str, is_admin: bool = False) -> str:
    """Создать JWT токен"""
    payload = {
        'user_id': user_id,
        'username': username,
        'is_admin': is_admin,
        'exp': datetime.utcnow().timestamp() + 3600 * 24 * 7  # 7 дней
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_jwt_token(token: str):
    """Верифицировать JWT токен"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

async def get_current_user(token: str = Depends(lambda: None)):
    """Получить текущего пользователя из токена"""
    if token is None:
        return None
    
    payload = verify_jwt_token(token)
    if payload is None:
        return None
    
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (payload['user_id'],))
    user = cursor.fetchone()
    conn.close()
    
    if user and user[6]:  # is_active
        return {
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'is_admin': bool(user[5]),
            'is_active': bool(user[6])
        }
    return None

def check_dependencies():
    """Проверить зависимости"""
    print("🔍 Проверка зависимостей...")
    
    required = ['fastapi', 'uvicorn', 'sqlalchemy', 'pyrogram', 'streamlit', 'PyQt6', 'jwt', 'hashlib']
    missing = []
    
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"❌ {package}")
    
    if missing:
        print(f"\n⚠️ Отсутствуют: {', '.join(missing)}")
        print("Установите: pip install fastapi uvicorn PyJWT")
        return False
    
    print("\n✅ Все зависимости установлены")
    return True

def create_complete_api_file():
    """Создать полный API файл с фронтендом"""
    print("\n📝 Создание полного API файла с фронтендом...")
    
    api_content = '''#!/usr/bin/env python3
"""
Telegram AutoPosting API - Полная версия с фронтендом
"""

import os
import sys
import sqlite3
import hashlib
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn

# Настройка пути
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Конфигурация
SECRET_KEY = "telegram-autoposting-secret-key-2024"
DB_PATH = "data/database.db"

app = FastAPI(
    title="Telegram AutoPosting API",
    description="API для системы автоматической публикации в Telegram",
    version="2.0.0",
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
    print(f"✅ Фронтенд подключен: {frontend_path}")
else:
    print(f"⚠️ Папка фронтенда не найдена: {frontend_path}")

# Безопасность
security = HTTPBearer()

# Вспомогательные функции
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_token(user_id: int, username: str, is_admin: bool = False) -> str:
    payload = {
        "user_id": user_id,
        "username": username,
        "is_admin": is_admin,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или истекший токен"
        )
    
    return payload

# Маршруты для фронтенда
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Главная страница фронтенда"""
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/login", response_class=HTMLResponse)
async def serve_login():
    """Страница входа"""
    return FileResponse(os.path.join(frontend_path, "login.html"))

@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    """Личный кабинет"""
    return FileResponse(os.path.join(frontend_path, "dashboard.html"))

@app.get("/admin", response_class=HTMLResponse)
async def serve_admin():
    """Админ-панель"""
    return FileResponse(os.path.join(frontend_path, "admin.html"))

# Основные API эндпоинты
@app.get("/api/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {
        "status": "healthy",
        "service": "telegram-autoposting",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"
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
async def login(username: str, password: str):
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
    username: str, 
    password: str, 
    email: Optional[str] = None,
    telegram_contact: Optional[str] = None
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
                end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
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
                    "active_subscriptions": total_subscriptions,  # Упрощенно
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
                        WHERE s.user_id = u.id AND s.is_active = 1) as has_subscription
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

# Основные API эндпоинты из main.py
@app.get("/api/users")
async def get_all_users():
    """Получить список пользователей"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, phone, created_at FROM users ORDER BY id")
            users = cursor.fetchall()
            
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

@app.post("/api/users")
async def create_user(username: str, phone: str):
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
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, message, status, created_at FROM campaigns ORDER BY id")
            campaigns = cursor.fetchall()
            
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

@app.post("/api/campaigns")
async def create_campaign(name: str, message: str):
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

# Тестовые эндпоинты
@app.get("/api/test")
async def test_endpoint():
    """Тестовый эндпоинт"""
    return {"message": "API работает корректно", "timestamp": datetime.utcnow().isoformat()}

# Запуск сервера
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"🚀 Запуск Telegram AutoPosting API на порту {port}")
    print(f"📚 Документация: http://localhost:{port}/api/docs")
    print(f"🌐 Фронтенд: http://localhost:{port}/")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=True
    )
'''
    
    os.makedirs("src/api", exist_ok=True)
    
    with open("src/api/server.py", "w", encoding="utf-8") as f:
        f.write(api_content)
    
    print("✅ Полный API файл создан: src/api/server.py")
    print("📁 Включает:")
    print("  - Полную аутентификацию (JWT)")
    print("  - Все необходимые API эндпоинты")
    print("  - Поддержку фронтенда")
    print("  - Админ-панель API")
    print("  - CORS настройки")

def create_frontend_structure():
    """Создать структуру фронтенда"""
    print("\n📁 Создание структуры фронтенда...")
    
    # Создаем папки
    frontend_dirs = ["frontend", "frontend/js", "frontend/css"]
    for directory in frontend_dirs:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Создана папка: {directory}")
    
    # Базовые файлы фронтенда
    frontend_files = {
        "frontend/index.html": """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram AutoPosting System</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        .gradient-bg {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .card-hover {
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .card-hover:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        .loader {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body class="bg-gray-50">
    <!-- Навигация -->
    <nav class="bg-white shadow-lg">
        <div class="container mx-auto px-4">
            <div class="flex justify-between items-center py-4">
                <div class="flex items-center">
                    <i class="fab fa-telegram text-blue-500 text-2xl mr-2"></i>
                    <span class="text-xl font-bold text-gray-800">Telegram AutoPosting</span>
                </div>
                <div class="flex space-x-4" id="nav-buttons">
                    <div class="flex space-x-4">
                        <a href="/login" class="text-blue-600 hover:text-blue-800 font-medium">
                            <i class="fas fa-sign-in-alt mr-1"></i>Войти
                        </a>
                        <a href="/login?register=true" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 font-medium">
                            <i class="fas fa-user-plus mr-1"></i>Регистрация
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </nav>

    <!-- Hero секция -->
    <header class="gradient-bg text-white">
        <div class="container mx-auto px-4 py-20">
            <div class="text-center">
                <h1 class="text-4xl md:text-5xl font-bold mb-6">
                    Автоматизируйте публикации в Telegram
                </h1>
                <p class="text-xl mb-8 max-w-2xl mx-auto">
                    Создавайте сценарии, настраивайте расписание и запускайте автоматические рассылки в Telegram каналах и группах
                </p>
                <div class="flex flex-col sm:flex-row justify-center gap-4">
                    <a href="#features" class="bg-white text-purple-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition">
                        <i class="fas fa-rocket mr-2"></i>Начать бесплатно
                    </a>
                    <a href="/login" class="bg-transparent border-2 border-white px-6 py-3 rounded-lg font-semibold hover:bg-white hover:text-purple-600 transition">
                        <i class="fas fa-play-circle mr-2"></i>Начать работу
                    </a>
                </div>
            </div>
        </div>
    </header>

    <!-- Статус системы -->
    <section class="container mx-auto px-4 py-12">
        <div class="bg-white rounded-xl shadow-lg p-6">
            <h2 class="text-2xl font-bold mb-6 text-center">Статус системы</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6" id="system-status">
                <div class="text-center p-4">
                    <div class="loader mx-auto mb-2"></div>
                    <p>Проверка API...</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Возможности -->
    <section id="features" class="container mx-auto px-4 py-12">
        <h2 class="text-3xl font-bold text-center mb-12">Что умеет система</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div class="card-hover bg-white rounded-xl shadow-lg p-6">
                <div class="text-blue-500 text-4xl mb-4">
                    <i class="fas fa-robot"></i>
                </div>
                <h3 class="text-xl font-bold mb-3">Автоматические сценарии</h3>
                <p class="text-gray-600">Создавайте сложные сценарии публикаций с задержками между сообщениями</p>
            </div>
            <div class="card-hover bg-white rounded-xl shadow-lg p-6">
                <div class="text-green-500 text-4xl mb-4">
                    <i class="fas fa-user-shield"></i>
                </div>
                <h3 class="text-xl font-bold mb-3">Безопасные сессии</h3>
                <p class="text-gray-600">Хранение Telegram сессий в зашифрованном виде с защитой от взлома</p>
            </div>
            <div class="card-hover bg-white rounded-xl shadow-lg p-6">
                <div class="text-purple-500 text-4xl mb-4">
                    <i class="fas fa-chart-line"></i>
                </div>
                <h3 class="text-xl font-bold mb-3">Подробная статистика</h3>
                <p class="text-gray-600">Отслеживайте эффективность рассылок и активность пользователей</p>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-800 text-white py-8">
        <div class="container mx-auto px-4">
            <div class="flex flex-col md:flex-row justify-between items-center">
                <div class="mb-4 md:mb-0">
                    <div class="flex items-center mb-2">
                        <i class="fab fa-telegram text-blue-400 text-2xl mr-2"></i>
                        <span class="text-xl font-bold">Telegram AutoPosting</span>
                    </div>
                    <p class="text-gray-400">© 2024 Все права защищены</p>
                </div>
                <div class="flex space-x-6">
                    <a href="#" class="text-gray-300 hover:text-white transition">
                        <i class="fab fa-github text-xl"></i>
                    </a>
                    <a href="#" class="text-gray-300 hover:text-white transition">
                        <i class="fab fa-telegram text-xl"></i>
                    </a>
                </div>
            </div>
        </div>
    </footer>

    <!-- JavaScript -->
    <script>
        // Проверка статуса системы
        async function checkSystemStatus() {
            const statusContainer = document.getElementById('system-status');
            
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                if (data.status === 'ok') {
                    statusContainer.innerHTML = `
                        <div class="text-center p-4 border-r">
                            <div class="text-green-500 text-3xl mb-2">
                                <i class="fas fa-server"></i>
                            </div>
                            <h3 class="font-bold">API Сервер</h3>
                            <p class="text-green-600 font-semibold">✅ Работает</p>
                            <p class="text-sm text-gray-500 mt-1">Версия: ${data.server?.python_version?.split(' ')[0] || '3.x'}</p>
                        </div>
                        <div class="text-center p-4 border-r">
                            <div class="text-blue-500 text-3xl mb-2">
                                <i class="fas fa-database"></i>
                            </div>
                            <h3 class="font-bold">База данных</h3>
                            <p class="text-green-600 font-semibold">✅ Подключена</p>
                            <p class="text-sm text-gray-500 mt-1">
                                Пользователей: ${data.database?.users || 0}
                            </p>
                        </div>
                        <div class="text-center p-4">
                            <div class="text-purple-500 text-3xl mb-2">
                                <i class="fas fa-code"></i>
                            </div>
                            <h3 class="font-bold">Версия</h3>
                            <p class="text-gray-700">2.0.0</p>
                            <p class="text-sm text-gray-500 mt-1">
                                ${data.server?.environment || 'development'}
                            </p>
                        </div>
                    `;
                }
            } catch (error) {
                statusContainer.innerHTML = `
                    <div class="col-span-3 text-center p-4">
                        <div class="text-red-500 text-3xl mb-2">
                            <i class="fas fa-exclamation-triangle"></i>
                        </div>
                        <h3 class="font-bold">Ошибка подключения</h3>
                        <p class="text-red-600">API сервер недоступен</p>
                        <p class="text-sm text-gray-500 mt-1">Проверьте, запущен ли сервер</p>
                    </div>
                `;
            }
        }
        
        // Проверка авторизации
        function checkAuth() {
            const token = localStorage.getItem('auth_token');
            const navButtons = document.getElementById('nav-buttons');
            
            if (token) {
                // Парсим токен (упрощенно)
                try {
                    const payload = JSON.parse(atob(token.split('.')[1]));
                    const isAdmin = payload.is_admin || false;
                    
                    navButtons.innerHTML = `
                        <div class="flex items-center space-x-4">
                            <span class="text-gray-700">
                                <i class="fas fa-user mr-1"></i>${payload.username}
                            </span>
                            ${isAdmin ? 
                                '<span class="bg-red-100 text-red-800 text-xs px-2 py-1 rounded">Админ</span>' : 
                                ''
                            }
                            <a href="${isAdmin ? '/admin' : '/dashboard'}" class="text-blue-600 hover:text-blue-800 font-medium">
                                <i class="fas fa-tachometer-alt mr-1"></i>${isAdmin ? 'Админка' : 'Личный кабинет'}
                            </a>
                            <button onclick="logout()" class="text-gray-600 hover:text-gray-800 font-medium">
                                <i class="fas fa-sign-out-alt mr-1"></i>Выйти
                            </button>
                        </div>
                    `;
                } catch (e) {
                    localStorage.removeItem('auth_token');
                }
            }
        }
        
        function logout() {
            localStorage.removeItem('auth_token');
            window.location.href = '/';
        }
        
        // При загрузке страницы
        document.addEventListener('DOMContentLoaded', () => {
            checkSystemStatus();
            checkAuth();
        });
    </script>
</body>
</html>""",
        
        "frontend/login.html": """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Вход / Регистрация - Telegram AutoPosting</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        .gradient-bg {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
        }
    </style>
</head>
<body class="gradient-bg min-h-screen flex items-center justify-center p-4">
    <div class="max-w-md w-full">
        <!-- Логотип и заголовок -->
        <div class="text-center mb-8">
            <div class="inline-block bg-white p-4 rounded-full shadow-lg mb-4">
                <i class="fab fa-telegram text-blue-500 text-4xl"></i>
            </div>
            <h1 class="text-3xl font-bold text-white">Telegram AutoPosting</h1>
            <p class="text-blue-100 mt-2">Автоматизация публикаций в Telegram</p>
        </div>

        <!-- Контейнер формы -->
        <div class="card rounded-2xl shadow-2xl p-8">
            <!-- Вкладки -->
            <div class="flex mb-8 border-b">
                <button id="tab-login" class="flex-1 py-3 text-center font-semibold text-blue-600 border-b-2 border-blue-600">
                    <i class="fas fa-sign-in-alt mr-2"></i>Вход
                </button>
                <button id="tab-register" class="flex-1 py-3 text-center font-semibold text-gray-500">
                    <i class="fas fa-user-plus mr-2"></i>Регистрация
                </button>
            </div>

            <!-- Форма входа -->
            <div id="login-form" class="space-y-6">
                <div>
                    <label class="block text-gray-700 text-sm font-medium mb-2">
                        <i class="fas fa-user mr-2"></i>Логин
                    </label>
                    <input type="text" id="login-username" 
                           class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                           placeholder="Введите логин">
                </div>

                <div>
                    <label class="block text-gray-700 text-sm font-medium mb-2">
                        <i class="fas fa-lock mr-2"></i>Пароль
                    </label>
                    <input type="password" id="login-password" 
                           class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                           placeholder="Введите пароль">
                </div>

                <button id="login-button" 
                        class="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition duration-300">
                    <i class="fas fa-sign-in-alt mr-2"></i>Войти в систему
                </button>

                <div class="text-center">
                    <p class="text-gray-600 text-sm">Нет аккаунта? 
                        <button class="text-blue-600 font-medium switch-to-register">Зарегистрируйтесь</button>
                    </p>
                </div>
            </div>

            <!-- Форма регистрации -->
            <div id="register-form" class="space-y-6 hidden">
                <div>
                    <label class="block text-gray-700 text-sm font-medium mb-2">
                        <i class="fas fa-user mr-2"></i>Логин *
                    </label>
                    <input type="text" id="register-username" 
                           class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                           placeholder="Придумайте логин" required>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-gray-700 text-sm font-medium mb-2">
                            <i class="fas fa-lock mr-2"></i>Пароль *
                        </label>
                        <input type="password" id="register-password" 
                               class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                               placeholder="Не менее 6 символов" required>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-sm font-medium mb-2">
                            <i class="fas fa-lock mr-2"></i>Повторите пароль *
                        </label>
                        <input type="password" id="register-password2" 
                               class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                               placeholder="Повторите пароль" required>
                    </div>
                </div>

                <div>
                    <label class="block text-gray-700 text-sm font-medium mb-2">
                        <i class="fas fa-envelope mr-2"></i>Email (необязательно)
                    </label>
                    <input type="email" id="register-email" 
                           class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                           placeholder="email@example.com">
                </div>

                <div>
                    <label class="block text-gray-700 text-sm font-medium mb-2">
                        <i class="fab fa-telegram mr-2"></i>Telegram контакт
                    </label>
                    <input type="text" id="register-telegram" 
                           class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                           placeholder="@username или +79991234567">
                </div>

                <div class="flex items-center">
                    <input type="checkbox" id="terms" class="h-4 w-4 text-blue-600 rounded" required>
                    <label for="terms" class="ml-2 text-sm text-gray-600">
                        Я согласен с правилами использования
                    </label>
                </div>

                <button id="register-button" 
                        class="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 transition duration-300">
                    <i class="fas fa-user-plus mr-2"></i>Создать аккаунт
                </button>

                <div class="text-center">
                    <p class="text-gray-600 text-sm">Уже есть аккаунт? 
                        <button class="text-blue-600 font-medium switch-to-login">Войдите</button>
                    </p>
                </div>
            </div>

            <!-- Уведомления -->
            <div id="notification" class="mt-6 hidden p-4 rounded-lg"></div>
        </div>

        <!-- Ссылка на главную -->
        <div class="text-center mt-6">
            <a href="/" class="text-white hover:text-blue-200 transition">
                <i class="fas fa-arrow-left mr-2"></i>Вернуться на главную
            </a>
        </div>
    </div>

    <script>
        // Переключение между вкладками
        document.getElementById('tab-login').addEventListener('click', () => {
            showLoginForm();
        });
        
        document.getElementById('tab-register').addEventListener('click', () => {
            showRegisterForm();
        });
        
        document.querySelectorAll('.switch-to-register').forEach(btn => {
            btn.addEventListener('click', showRegisterForm);
        });
        
        document.querySelectorAll('.switch-to-login').forEach(btn => {
            btn.addEventListener('click', showLoginForm);
        });

        function showLoginForm() {
            document.getElementById('login-form').classList.remove('hidden');
            document.getElementById('register-form').classList.add('hidden');
            document.getElementById('tab-login').classList.add('text-blue-600', 'border-blue-600');
            document.getElementById('tab-login').classList.remove('text-gray-500');
            document.getElementById('tab-register').classList.remove('text-blue-600', 'border-blue-600');
            document.getElementById('tab-register').classList.add('text-gray-500');
        }

        function showRegisterForm() {
            document.getElementById('register-form').classList.remove('hidden');
            document.getElementById('login-form').classList.add('hidden');
            document.getElementById('tab-register').classList.add('text-blue-600', 'border-blue-600');
            document.getElementById('tab-register').classList.remove('text-gray-500');
            document.getElementById('tab-login').classList.remove('text-blue-600', 'border-blue-600');
            document.getElementById('tab-login').classList.add('text-gray-500');
        }

        // Обработка входа
        document.getElementById('login-button').addEventListener('click', async () => {
            const username = document.getElementById('login-username').value.trim();
            const password = document.getElementById('login-password').value;
            
            if (!username || !password) {
                showNotification('Заполните все поля', 'error');
                return;
            }
            
            const button = document.getElementById('login-button');
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Вход...';
            button.disabled = true;
            
            try {
                const response = await fetch(`/api/auth/login?username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`, {
                    method: 'POST'
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    if (result.token) {
                        // Сохраняем токен
                        localStorage.setItem('auth_token', result.token);
                        
                        showNotification('Вход выполнен успешно!', 'success');
                        
                        // Редирект через 1 секунду
                        setTimeout(() => {
                            if (result.user && result.user.is_admin) {
                                window.location.href = '/admin';
                            } else {
                                window.location.href = '/dashboard';
                            }
                        }, 1000);
                    } else {
                        showNotification('Ошибка авторизации', 'error');
                    }
                } else {
                    showNotification(result.detail || 'Неверный логин или пароль', 'error');
                }
            } catch (error) {
                showNotification('Ошибка подключения к серверу', 'error');
            } finally {
                button.innerHTML = originalText;
                button.disabled = false;
            }
        });

        // Обработка регистрации
        document.getElementById('register-button').addEventListener('click', async () => {
            const username = document.getElementById('register-username').value.trim();
            const password = document.getElementById('register-password').value;
            const password2 = document.getElementById('register-password2').value;
            const email = document.getElementById('register-email').value.trim();
            const telegram = document.getElementById('register-telegram').value.trim();
            const terms = document.getElementById('terms').checked;
            
            // Валидация
            if (!username || !password) {
                showNotification('Заполните обязательные поля', 'error');
                return;
            }
            
            if (password.length < 6) {
                showNotification('Пароль должен быть не менее 6 символов', 'error');
                return;
            }
            
            if (password !== password2) {
                showNotification('Пароли не совпадают', 'error');
                return;
            }
            
            if (!terms) {
                showNotification('Примите правила использования', 'error');
                return;
            }
            
            const button = document.getElementById('register-button');
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Регистрация...';
            button.disabled = true;
            
            try {
                const response = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        username: username,
                        password: password,
                        email: email || null,
                        telegram_contact: telegram || null
                    })
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    if (result.token) {
                        localStorage.setItem('auth_token', result.token);
                        showNotification('Регистрация успешна! Выполняется вход...', 'success');
                        
                        setTimeout(() => {
                            window.location.href = '/dashboard';
                        }, 1500);
                    }
                } else {
                    showNotification(result.detail || 'Ошибка регистрации', 'error');
                }
            } catch (error) {
                showNotification('Ошибка подключения к серверу', 'error');
            } finally {
                button.innerHTML = originalText;
                button.disabled = false;
            }
        });

        // Показать уведомление
        function showNotification(message, type = 'info') {
            const notification = document.getElementById('notification');
            const colors = {
                success: 'bg-green-100 text-green-800 border-green-200',
                error: 'bg-red-100 text-red-800 border-red-200',
                info: 'bg-blue-100 text-blue-800 border-blue-200'
            };
            
            notification.className = `mt-6 p-4 rounded-lg border ${colors[type]}`;
            notification.innerHTML = `
                <div class="flex items-center">
                    <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} mr-3"></i>
                    <span>${message}</span>
                </div>
            `;
            notification.classList.remove('hidden');
            
            // Автоскрытие для success/info
            if (type !== 'error') {
                setTimeout(() => {
                    notification.classList.add('hidden');
                }, 5000);
            }
        }

        // Проверка URL параметров
        document.addEventListener('DOMContentLoaded', () => {
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.get('register') === 'true') {
                showRegisterForm();
            }
            
            // Проверка существующего токена
            const token = localStorage.getItem('auth_token');
            if (token) {
                try {
                    const payload = JSON.parse(atob(token.split('.')[1]));
                    if (payload.exp > Date.now() / 1000) {
                        // Если уже авторизован, редирект
                        if (payload.is_admin) {
                            window.location.href = '/admin';
                        } else {
                            window.location.href = '/dashboard';
                        }
                    } else {
                        localStorage.removeItem('auth_token');
                    }
                } catch (e) {
                    localStorage.removeItem('auth_token');
                }
            }
        });
    </script>
</body>
</html>""",
        
        "frontend/dashboard.html": """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Личный кабинет - Telegram AutoPosting</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-gray-50">
    <div id="app">
        <div class="text-center py-12">
            <div class="loader mx-auto mb-4"></div>
            <p>Загрузка личного кабинета...</p>
        </div>
    </div>

    <script>
        // Проверка авторизации
        const token = localStorage.getItem('auth_token');
        
        if (!token) {
            window.location.href = '/login';
        } else {
            // Парсим токен
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                
                if (payload.exp < Date.now() / 1000) {
                    localStorage.removeItem('auth_token');
                    window.location.href = '/login';
                } else if (payload.is_admin) {
                    window.location.href = '/admin';
                } else {
                    // Загружаем личный кабинет
                    loadDashboard();
                }
            } catch (e) {
                localStorage.removeItem('auth_token');
                window.location.href = '/login';
            }
        }
        
        async function loadDashboard() {
            const app = document.getElementById('app');
            
            app.innerHTML = `
                <!-- Навигация -->
                <nav class="bg-white shadow-md">
                    <div class="container mx-auto px-4 py-3">
                        <div class="flex justify-between items-center">
                            <div class="flex items-center space-x-4">
                                <i class="fab fa-telegram text-blue-500 text-2xl"></i>
                                <span class="text-xl font-bold">Telegram AutoPosting</span>
                                <span class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">Личный кабинет</span>
                            </div>
                            <div class="flex items-center space-x-4">
                                <span id="user-name" class="text-gray-700"></span>
                                <button onclick="logout()" class="text-gray-600 hover:text-gray-800">
                                    <i class="fas fa-sign-out-alt mr-1"></i>Выйти
                                </button>
                            </div>
                        </div>
                    </div>
                </nav>

                <div class="container mx-auto px-4 py-8">
                    <div class="mb-8">
                        <h1 class="text-2xl font-bold text-gray-800 mb-2">Мой личный кабинет</h1>
                        <p class="text-gray-600">Добро пожаловать в систему автоматической публикации в Telegram</p>
                    </div>
                    
                    <!-- Статус подписки -->
                    <div class="bg-white rounded-xl shadow p-6 mb-8">
                        <h2 class="text-lg font-bold mb-4">Статус подписки</h2>
                        <div id="subscription-info" class="text-center py-4">
                            <div class="loader mx-auto mb-2"></div>
                            <p>Проверка подписки...</p>
                        </div>
                    </div>
                    
                    <!-- Быстрые действия -->
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div class="bg-white rounded-xl shadow p-6">
                            <div class="text-blue-500 text-3xl mb-4">
                                <i class="fab fa-telegram"></i>
                            </div>
                            <h3 class="font-bold text-lg mb-2">Telegram аккаунты</h3>
                            <p class="text-gray-600 mb-4">Добавьте и управляйте Telegram аккаунтами для рассылок</p>
                            <button class="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">
                                Управлять аккаунтами
                            </button>
                        </div>
                        
                        <div class="bg-white rounded-xl shadow p-6">
                            <div class="text-green-500 text-3xl mb-4">
                                <i class="fas fa-code"></i>
                            </div>
                            <h3 class="font-bold text-lg mb-2">Сценарии</h3>
                            <p class="text-gray-600 mb-4">Создавайте сценарии автоматических публикаций</p>
                            <button class="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700">
                                Создать сценарий
                            </button>
                        </div>
                        
                        <div class="bg-white rounded-xl shadow p-6">
                            <div class="text-purple-500 text-3xl mb-4">
                                <i class="fas fa-paper-plane"></i>
                            </div>
                            <h3 class="font-bold text-lg mb-2">Рассылки</h3>
                            <p class="text-gray-600 mb-4">Запускайте автоматические рассылки в группы и каналы</p>
                            <button class="w-full bg-purple-600 text-white py-2 rounded-lg hover:bg-purple-700">
                                Запустить рассылку
                            </button>
                        </div>
                    </div>
                </div>
                
                <style>
                    .loader {
                        border: 3px solid #f3f3f3;
                        border-top: 3px solid #3B82F6;
                        border-radius: 50%;
                        width: 40px;
                        height: 40px;
                        animation: spin 1s linear infinite;
                    }
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                </style>
            `;
            
            // Обновляем имя пользователя
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                document.getElementById('user-name').textContent = payload.username;
            } catch (e) {
                console.error('Ошибка парсинга токена:', e);
            }
            
            // Проверяем подписку
            await checkSubscription();
        }
        
        async function checkSubscription() {
            try {
                const response = await fetch('/api/subscription/check', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    const subscriptionInfo = document.getElementById('subscription-info');
                    
                    if (data.has_subscription) {
                        subscriptionInfo.innerHTML = `
                            <div class="text-center">
                                <div class="text-green-500 text-4xl mb-3">
                                    <i class="fas fa-crown"></i>
                                </div>
                                <h3 class="text-xl font-bold text-green-600 mb-2">Подписка активна</h3>
                                <p class="text-gray-600">Осталось дней: ${data.subscription.days_left}</p>
                                <p class="text-sm text-gray-500">Действует до: ${data.subscription.end_date}</p>
                            </div>
                        `;
                    } else {
                        subscriptionInfo.innerHTML = `
                            <div class="text-center">
                                <div class="text-red-500 text-4xl mb-3">
                                    <i class="fas fa-exclamation-circle"></i>
                                </div>
                                <h3 class="text-xl font-bold text-red-600 mb-2">Нет активной подписки</h3>
                                <p class="text-gray-600 mb-4">Для доступа к функциям требуется подписка</p>
                                <button class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                                    Оформить подписку
                                </button>
                            </div>
                        `;
                    }
                }
            } catch (error) {
                console.error('Ошибка проверки подписки:', error);
                document.getElementById('subscription-info').innerHTML = `
                    <div class="text-center text-red-600">
                        <i class="fas fa-exclamation-triangle mr-2"></i>
                        Ошибка загрузки информации о подписке
                    </div>
                `;
            }
        }
        
        function logout() {
            if (confirm('Вы уверены, что хотите выйти?')) {
                localStorage.removeItem('auth_token');
                window.location.href = '/';
            }
        }
    </script>
</body>
</html>""",
        
        "frontend/admin.html": """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Админ-панель - Telegram AutoPosting</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-gray-100">
    <div id="app">
        <div class="text-center py-12">
            <div class="loader mx-auto mb-4"></div>
            <p>Загрузка админ-панели...</p>
        </div>
    </div>

    <script>
        // Проверка авторизации и прав
        const token = localStorage.getItem('auth_token');
        
        if (!token) {
            window.location.href = '/login';
        } else {
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                
                if (payload.exp < Date.now() / 1000) {
                    localStorage.removeItem('auth_token');
                    window.location.href = '/login';
                } else if (!payload.is_admin) {
                    window.location.href = '/dashboard';
                } else {
                    // Загружаем админ-панель
                    loadAdminPanel();
                }
            } catch (e) {
                localStorage.removeItem('auth_token');
                window.location.href = '/login';
            }
        }
        
        async function loadAdminPanel() {
            const app = document.getElementById('app');
            
            app.innerHTML = `
                <!-- Навигация -->
                <nav class="bg-gray-800 text-white shadow-lg">
                    <div class="container mx-auto px-4">
                        <div class="flex justify-between items-center py-4">
                            <div class="flex items-center space-x-3">
                                <i class="fab fa-telegram text-blue-400 text-2xl"></i>
                                <span class="text-xl font-bold">Telegram AutoPosting</span>
                                <span class="bg-red-600 text-white text-xs px-2 py-1 rounded">Админ</span>
                            </div>
                            <div class="flex items-center space-x-4">
                                <span id="admin-name"></span>
                                <button onclick="logout()" class="text-gray-300 hover:text-white">
                                    <i class="fas fa-sign-out-alt mr-1"></i>Выйти
                                </button>
                            </div>
                        </div>
                    </div>
                </nav>

                <div class="container mx-auto px-4 py-6">
                    <div class="flex flex-col lg:flex-row gap-6">
                        <!-- Боковая панель -->
                        <div class="lg:w-1/4">
                            <div class="bg-white rounded-xl shadow p-6 mb-6">
                                <div class="text-center mb-6">
                                    <div class="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                                        <i class="fas fa-user-shield text-blue-600 text-3xl"></i>
                                    </div>
                                    <h3 id="admin-username" class="font-bold text-lg"></h3>
                                    <p class="text-gray-500 text-sm">Администратор системы</p>
                                </div>
                                
                                <nav class="space-y-2">
                                    <button onclick="loadAdminSection('dashboard')" class="admin-menu-item active">
                                        <i class="fas fa-tachometer-alt mr-3"></i>Дашборд
                                    </button>
                                    <button onclick="loadAdminSection('users')" class="admin-menu-item">
                                        <i class="fas fa-users mr-3"></i>Пользователи
                                    </button>
                                    <button onclick="loadAdminSection('campaigns')" class="admin-menu-item">
                                        <i class="fas fa-paper-plane mr-3"></i>Рассылки
                                    </button>
                                    <button onclick="loadAdminSection('system')" class="admin-menu-item">
                                        <i class="fas fa-cogs mr-3"></i>Система
                                    </button>
                                </nav>
                            </div>
                        </div>
                        
                        <!-- Основной контент -->
                        <div class="lg:w-3/4">
                            <div class="bg-white rounded-xl shadow p-6">
                                <div id="admin-content">
                                    <!-- Динамический контент -->
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <style>
                    .admin-menu-item {
                        display: flex;
                        align-items: center;
                        width: 100%;
                        padding: 12px 16px;
                        border-radius: 8px;
                        text-align: left;
                        background: transparent;
                        border: none;
                        color: #4B5563;
                        transition: all 0.3s;
                    }
                    .admin-menu-item:hover {
                        background-color: #F3F4F6;
                        color: #111827;
                    }
                    .admin-menu-item.active {
                        background-color: #3B82F6;
                        color: white;
                    }
                    .loader {
                        border: 3px solid #f3f3f3;
                        border-top: 3px solid #3B82F6;
                        border-radius: 50%;
                        width: 40px;
                        height: 40px;
                        animation: spin 1s linear infinite;
                    }
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                </style>
            `;
            
            // Обновляем информацию
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                document.getElementById('admin-name').textContent = payload.username;
                document.getElementById('admin-username').textContent = payload.username;
            } catch (e) {
                console.error('Ошибка парсинга токена:', e);
            }
            
            // Загружаем дашборд
            loadAdminSection('dashboard');
        }
        
        function loadAdminSection(section) {
            // Обновляем активную кнопку
            document.querySelectorAll('.admin-menu-item').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            const content = document.getElementById('admin-content');
            
            switch(section) {
                case 'dashboard':
                    loadAdminDashboard(content);
                    break;
                case 'users':
                    loadAdminUsers(content);
                    break;
                case 'campaigns':
                    loadAdminCampaigns(content);
                    break;
                case 'system':
                    loadAdminSystem(content);
                    break;
            }
        }
        
        async function loadAdminDashboard(content) {
            content.innerHTML = `
                <div class="mb-8">
                    <h1 class="text-2xl font-bold text-gray-800 mb-2">Административная панель</h1>
                    <p class="text-gray-600">Обзор системы и статистика</p>
                </div>
                
                <!-- Карточки статистики -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8" id="admin-stats">
                    <div class="text-center p-6">
                        <div class="loader mx-auto mb-2"></div>
                        <p>Загрузка...</p>
                    </div>
                </div>
            `;
            
            // Загружаем статистику
            await loadAdminStats();
        }
        
        async function loadAdminStats() {
            try {
                const response = await fetch('/api/admin/stats', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    const statsContainer = document.getElementById('admin-stats');
                    
                    statsContainer.innerHTML = `
                        <div class="bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl shadow p-6">
                            <div class="flex justify-between items-start">
                                <div>
                                    <p class="text-blue-100">Всего пользователей</p>
                                    <h3 class="text-3xl font-bold mt-2">${data.stats.total_users}</h3>
                                </div>
                                <div class="bg-blue-400 p-3 rounded-lg">
                                    <i class="fas fa-users text-xl"></i>
                                </div>
                            </div>
                        </div>
                        
                        <div class="bg-gradient-to-r from-green-500 to-green-600 text-white rounded-xl shadow p-6">
                            <div class="flex justify-between items-start">
                                <div>
                                    <p class="text-green-100">Активные подписки</p>
                                    <h3 class="text-3xl font-bold mt-2">${data.stats.active_subscriptions}</h3>
                                </div>
                                <div class="bg-green-400 p-3 rounded-lg">
                                    <i class="fas fa-crown text-xl"></i>
                                </div>
                            </div>
                        </div>
                        
                        <div class="bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-xl shadow p-6">
                            <div class="flex justify-between items-start">
                                <div>
                                    <p class="text-purple-100">Всего рассылок</p>
                                    <h3 class="text-3xl font-bold mt-2">${data.stats.total_campaigns}</h3>
                                </div>
                                <div class="bg-purple-400 p-3 rounded-lg">
                                    <i class="fas fa-paper-plane text-xl"></i>
                                </div>
                            </div>
                        </div>
                        
                        <div class="bg-gradient-to-r from-yellow-500 to-yellow-600 text-white rounded-xl shadow p-6">
                            <div class="flex justify-between items-start">
                                <div>
                                    <p class="text-yellow-100">Активные пользователи</p>
                                    <h3 class="text-3xl font-bold mt-2">${data.stats.active_users}</h3>
                                </div>
                                <div class="bg-yellow-400 p-3 rounded-lg">
                                    <i class="fas fa-user-check text-xl"></i>
                                </div>
                            </div>
                        </div>
                    `;
                }
            } catch (error) {
                console.error('Ошибка загрузки статистики:', error);
            }
        }
        
        function loadAdminUsers(content) {
            content.innerHTML = `
                <div class="mb-8">
                    <div class="flex justify-between items-center">
                        <div>
                            <h1 class="text-2xl font-bold text-gray-800 mb-2">Управление пользователями</h1>
                            <p class="text-gray-600">Просмотр и управление всеми пользователями системы</p>
                        </div>
                    </div>
                </div>
                
                <div class="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
                    <div class="overflow-x-auto">
                        <table class="min-w-full divide-y divide-gray-200">
                            <thead class="bg-gray-50">
                                <tr>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Пользователь</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Статус</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Дата регистрации</th>
                                </tr>
                            </thead>
                            <tbody id="users-table-body" class="bg-white divide-y divide-gray-200">
                                <tr>
                                    <td colspan="4" class="px-6 py-8 text-center">
                                        <div class="loader mx-auto mb-2"></div>
                                        <p class="text-gray-500">Загрузка пользователей...</p>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
            
            // Загружаем пользователей
            loadAdminUsersData();
        }
        
        async function loadAdminUsersData() {
            try {
                const response = await fetch('/api/admin/users', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    const tbody = document.getElementById('users-table-body');
                    
                    let html = '';
                    data.users.forEach(user => {
                        const statusBadge = user.is_active ? 
                            '<span class="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">Активен</span>' :
                            '<span class="bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full">Неактивен</span>';
                        
                        const adminBadge = user.is_admin ? 
                            '<span class="bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full ml-1">Админ</span>' : '';
                        
                        html += \`
                            <tr>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">\${user.id}</td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <div class="flex items-center">
                                        <div class="text-sm font-medium text-gray-900">\${user.username}</div>
                                        \${adminBadge}
                                    </div>
                                    <div class="text-sm text-gray-500">\${user.email || 'Нет email'}</div>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    \${statusBadge}
                                    \${user.has_subscription ? 
                                        '<span class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full ml-1">Подписка</span>' : 
                                        '<span class="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded-full ml-1">Без подписки</span>'
                                    }
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    \${user.created_at}
                                </td>
                            </tr>
                        \`;
                    });
                    
                    tbody.innerHTML = html;
                }
            } catch (error) {
                console.error('Ошибка загрузки пользователей:', error);
            }
        }
        
        function loadAdminCampaigns(content) {
            content.innerHTML = \`
                <div class="mb-8">
                    <h1 class="text-2xl font-bold text-gray-800 mb-2">Управление рассылками</h1>
                    <p class="text-gray-600">Просмотр всех рассылок в системе</p>
                </div>
                
                <div class="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
                    <div class="overflow-x-auto">
                        <table class="min-w-full divide-y divide-gray-200">
                            <thead class="bg-gray-50">
                                <tr>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Название</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Статус</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Дата создания</th>
                                </tr>
                            </thead>
                            <tbody id="campaigns-table-body" class="bg-white divide-y divide-gray-200">
                                <tr>
                                    <td colspan="4" class="px-6 py-8 text-center">
                                        <div class="loader mx-auto mb-2"></div>
                                        <p class="text-gray-500">Загрузка рассылок...</p>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            \`;
            
            // Загружаем рассылки
            loadAdminCampaignsData();
        }
        
        async function loadAdminCampaignsData() {
            try {
                const response = await fetch('/api/campaigns');
                const data = await response.json();
                
                if (data.status === 'success') {
                    const tbody = document.getElementById('campaigns-table-body');
                    
                    let html = '';
                    data.campaigns.forEach(campaign => {
                        const statusBadge = campaign.status === 'pending' ? 
                            '<span class="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full">Ожидает</span>' :
                            campaign.status === 'running' ?
                            '<span class="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">Запущена</span>' :
                            '<span class="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded-full">' + campaign.status + '</span>';
                        
                        html += \`
                            <tr>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">\${campaign.id}</td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <div class="text-sm font-medium text-gray-900">\${campaign.name}</div>
                                    <div class="text-sm text-gray-500 truncate max-w-xs">\${campaign.message || 'Без сообщения'}</div>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    \${statusBadge}
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    \${campaign.created_at}
                                </td>
                            </tr>
                        \`;
                    });
                    
                    tbody.innerHTML = html;
                }
            } catch (error) {
                console.error('Ошибка загрузки рассылок:', error);
            }
        }
        
        function loadAdminSystem(content) {
            content.innerHTML = \`
                <div class="mb-8">
                    <h1 class="text-2xl font-bold text-gray-800 mb-2">Настройки системы</h1>
                    <p class="text-gray-600">Основные параметры и конфигурация</p>
                </div>
                
                <div class="bg-white border border-gray-200 rounded-xl shadow-sm p-6">
                    <div class="space-y-6">
                        <div>
                            <h3 class="text-lg font-bold mb-3">Информация о системе</h3>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div class="bg-gray-50 p-4 rounded-lg">
                                    <p class="text-sm text-gray-500">Версия API</p>
                                    <p class="font-medium">2.0.0</p>
                                </div>
                                <div class="bg-gray-50 p-4 rounded-lg">
                                    <p class="text-sm text-gray-500">База данных</p>
                                    <p class="font-medium">SQLite</p>
                                </div>
                            </div>
                        </div>
                        
                        <div>
                            <h3 class="text-lg font-bold mb-3">Действия</h3>
                            <div class="flex flex-wrap gap-4">
                                <button onclick="checkSystemHealth()" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                                    <i class="fas fa-heartbeat mr-2"></i>Проверить здоровье
                                </button>
                                <button onclick="clearOldData()" class="bg-yellow-600 text-white px-4 py-2 rounded-lg hover:bg-yellow-700">
                                    <i class="fas fa-broom mr-2"></i>Очистить старые данные
                                </button>
                                <button onclick="createBackup()" class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700">
                                    <i class="fas fa-download mr-2"></i>Создать резервную копию
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            \`;
        }
        
        function checkSystemHealth() {
            fetch('/api/health')
                .then(response => response.json())
                .then(data => {
                    alert('Статус системы: ' + data.status + '\\nСервис: ' + data.service);
                })
                .catch(error => {
                    alert('Ошибка проверки здоровья системы');
                });
        }
        
        function clearOldData() {
            if (confirm('Вы уверены, что хотите очистить старые данные?')) {
                alert('Функция очистки данных будет реализована позже');
            }
        }
        
        function createBackup() {
            alert('Функция резервного копирования будет реализована позже');
        }
        
        function logout() {
            if (confirm('Вы уверены, что хотите выйти?')) {
                localStorage.removeItem('auth_token');
                window.location.href = '/';
            }
        }
    </script>
</body>
</html>""",
        
        "frontend/js/api.js": """class TelegramAutoPostingAPI {
    constructor() {
        this.baseURL = window.location.origin;
        this.token = localStorage.getItem('auth_token');
        this.user = JSON.parse(localStorage.getItem('user_data') || 'null');
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        const config = {
            ...options,
            headers
        };
        
        try {
            const response = await fetch(url, config);
            
            if (response.status === 401) {
                this.logout();
                window.location.href = '/login';
                return null;
            }
            
            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new Error(error.detail || error.message || `HTTP ${response.status}`);
            }
            
            return await response.json();
            
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    async login(username, password) {
        const data = await this.request('/api/auth/login', {
            method: 'POST'
        }, { username, password });
        
        if (data && data.token) {
            this.token = data.token;
            this.user = data.user;
            
            localStorage.setItem('auth_token', data.token);
            localStorage.setItem('user_data', JSON.stringify(data.user));
            
            if (data.subscription) {
                localStorage.setItem('subscription', JSON.stringify(data.subscription));
            }
        }
        
        return data;
    }

    async register(username, password, email = '', telegram = '') {
        return await this.request('/api/auth/register', {
            method: 'POST',
            body: JSON.stringify({ 
                username, 
                password, 
                email, 
                telegram_contact: telegram 
            })
        });
    }

    async getSystemStatus() {
        return await this.request('/api/status');
    }

    async getHealth() {
        return await this.request('/api/health');
    }

    async getUsers() {
        return await this.request('/api/users');
    }

    async createUser(username, phone) {
        return await this.request('/api/users', {
            method: 'POST',
            body: JSON.stringify({ username, phone })
        });
    }

    async getCampaigns() {
        return await this.request('/api/campaigns');
    }

    async createCampaign(name, message) {
        return await this.request('/api/campaigns', {
            method: 'POST',
            body: JSON.stringify({ name, message })
        });
    }

    async checkSubscription() {
        return await this.request('/api/subscription/check');
    }

    async getAdminStats() {
        return await this.request('/api/admin/stats');
    }

    async getAdminUsers() {
        return await this.request('/api/admin/users');
    }

    logout() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_data');
        localStorage.removeItem('subscription');
    }

    isAuthenticated() {
        return !!this.token && !!this.user;
    }

    isAdmin() {
        return this.isAuthenticated() && this.user.is_admin === true;
    }
}

window.api = new TelegramAutoPostingAPI();""",
        
        "frontend/js/app.js": """async function initApp() {
    updateNavigation();
    checkSystemStatus();
    checkAuth();
}

function updateNavigation() {
    const navButtons = document.getElementById('nav-buttons');
    
    if (!navButtons) return;
    
    if (api.isAuthenticated()) {
        const userName = api.user.username;
        const isAdmin = api.isAdmin();
        
        navButtons.innerHTML = `
            <div class="flex items-center space-x-4">
                <span class="text-gray-700">
                    <i class="fas fa-user mr-1"></i>${userName}
                </span>
                ${isAdmin ? 
                    '<span class="bg-red-100 text-red-800 text-xs px-2 py-1 rounded">Админ</span>' : 
                    ''
                }
                <a href="${isAdmin ? '/admin' : '/dashboard'}" class="text-blue-600 hover:text-blue-800 font-medium">
                    <i class="fas fa-tachometer-alt mr-1"></i>${isAdmin ? 'Админка' : 'Личный кабинет'}
                </a>
                <button onclick="logout()" class="text-gray-600 hover:text-gray-800 font-medium">
                    <i class="fas fa-sign-out-alt mr-1"></i>Выйти
                </button>
            </div>
        `;
    } else {
        navButtons.innerHTML = `
            <div class="flex space-x-4">
                <a href="/login" class="text-blue-600 hover:text-blue-800 font-medium">
                    <i class="fas fa-sign-in-alt mr-1"></i>Войти
                </a>
                <a href="/login?register=true" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 font-medium">
                    <i class="fas fa-user-plus mr-1"></i>Регистрация
                </a>
            </div>
        `;
    }
}

async function checkSystemStatus() {
    const statusContainer = document.getElementById('system-status');
    
    if (!statusContainer) return;
    
    try {
        const status = await api.getSystemStatus();
        
        if (status) {
            statusContainer.innerHTML = `
                <div class="text-center p-4 border-r">
                    <div class="text-green-500 text-3xl mb-2">
                        <i class="fas fa-server"></i>
                    </div>
                    <h3 class="font-bold">API Сервер</h3>
                    <p class="text-green-600 font-semibold">✅ Работает</p>
                    <p class="text-sm text-gray-500 mt-1">Версия: ${status.server?.python_version?.split(' ')[0] || '3.x'}</p>
                </div>
                <div class="text-center p-4 border-r">
                    <div class="text-blue-500 text-3xl mb-2">
                        <i class="fas fa-database"></i>
                    </div>
                    <h3 class="font-bold">База данных</h3>
                    <p class="${status.database?.connection === 'established' ? 'text-green-600' : 'text-red-600'} font-semibold">
                        ${status.database?.connection === 'established' ? '✅ Подключена' : '❌ Ошибка'}
                    </p>
                    <p class="text-sm text-gray-500 mt-1">
                        Пользователей: ${status.database?.users || 0}
                    </p>
                </div>
                <div class="text-center p-4">
                    <div class="text-purple-500 text-3xl mb-2">
                        <i class="fas fa-code"></i>
                    </div>
                    <h3 class="font-bold">Версия</h3>
                    <p class="text-gray-700">${status.server?.environment === 'railway' ? 'Railway' : '2.0.0'}</p>
                    <p class="text-sm text-gray-500 mt-1">
                        ${status.server?.environment || 'development'}
                    </p>
                </div>
            `;
        }
    } catch (error) {
        statusContainer.innerHTML = `
            <div class="col-span-3 text-center p-4">
                <div class="text-red-500 text-3xl mb-2">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <h3 class="font-bold">Ошибка подключения</h3>
                <p class="text-red-600">Не удалось подключиться к серверу</p>
                <p class="text-sm text-gray-500 mt-1">Проверьте, запущен ли API сервер</p>
            </div>
        `;
    }
}

function checkAuth() {
    if (!api.isAuthenticated()) {
        const currentPage = window.location.pathname;
        if (!currentPage.includes('index.html') && !currentPage.includes('login.html') && currentPage !== '/') {
            window.location.href = '/';
        }
    } else {
        if (window.location.pathname.includes('login.html')) {
            window.location.href = api.isAdmin() ? '/admin' : '/dashboard';
        }
    }
}

function logout() {
    if (confirm('Вы уверены, что хотите выйти?')) {
        api.logout();
        window.location.href = '/';
    }
}

function showNotification(message, type = 'info') {
    const colors = {
        success: 'bg-green-100 border-green-500 text-green-700',
        error: 'bg-red-100 border-red-500 text-red-700',
        warning: 'bg-yellow-100 border-yellow-500 text-yellow-700',
        info: 'bg-blue-100 border-blue-500 text-blue-700'
    };
    
    const notification = document.createElement('div');
    notification.className = \`fixed top-4 right-4 z-50 px-6 py-4 rounded-lg border-l-4 \${colors[type]} shadow-lg max-w-md transform translate-x-full transition-transform duration-300\`;
    notification.innerHTML = \`
        <div class="flex items-start">
            <div class="flex-shrink-0">
                \${type === 'success' ? '<i class="fas fa-check-circle text-green-500"></i>' : ''}
                \${type === 'error' ? '<i class="fas fa-exclamation-circle text-red-500"></i>' : ''}
                \${type === 'warning' ? '<i class="fas fa-exclamation-triangle text-yellow-500"></i>' : ''}
                \${type === 'info' ? '<i class="fas fa-info-circle text-blue-500"></i>' : ''}
            </div>
            <div class="ml-3">
                <p class="font-medium">\${message}</p>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-auto text-gray-400 hover:text-gray-600">
                <i class="fas fa-times"></i>
            </button>
        </div>
    \`;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.remove('translate-x-full');
        notification.classList.add('translate-x-0');
    }, 10);
    
    setTimeout(() => {
        notification.classList.remove('translate-x-0');
        notification.classList.add('translate-x-full');
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

window.showNotification = showNotification;
window.logout = logout;
window.initApp = initApp;"""
    }
    
    # Создаем файлы фронтенда
    for file_path, content in frontend_files.items():
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Создан файл: {file_path}")
    
    print("\n✅ Структура фронтенда создана!")
    print("📁 Папки: frontend/, frontend/js/, frontend/css/")
    print("📄 Файлы:")
    print("  - index.html      - Главная страница")
    print("  - login.html      - Вход/регистрация")
    print("  - dashboard.html  - Личный кабинет")
    print("  - admin.html      - Админ-панель")
    print("  - js/api.js       - API клиент")
    print("  - js/app.js       - Основной скрипт")

def test_telegram_api():
    """Протестировать Telegram API"""
    print("\n🔧 Тестирование Telegram API...")
    
    try:
        from pyrogram import Client
        
        # Проверка возможности импортировать
        print("✅ Pyrogram импортирован успешно")
        
        # Проверка наличия необходимых файлов
        print("\n📁 Проверка файлов сессий...")
        if os.path.exists("data/sessions"):
            session_files = os.listdir("data/sessions")
            print(f"✅ Найдено сессий: {len(session_files)}")
        else:
            print("ℹ️ Папка сессий не найдена, будет создана при запуске")
        
        # Создание тестового клиента
        print("\n🧪 Создание тестового клиента...")
        
        test_client = Client(
            name="test_session",
            api_id=12345,  # Тестовые данные
            api_hash="test_hash",
            workdir="data/sessions"
        )
        
        print("✅ Клиент создан успешно")
        print("⚠️ Для реальной работы нужны действительные api_id и api_hash")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка Telegram API: {e}")
        return False

def run_development_mode():
    """Запустить в режиме разработки с фронтендом"""
    print("\n🔧 Запуск в режиме разработки...")
    
    try:
        # Создаем полный API файл, если его нет
        if not os.path.exists("src/api/server.py"):
            print("📝 Создание полного API файла...")
            create_complete_api_file()
        else:
            print("✅ API файл уже существует")
        
        # Создаем структуру фронтенда, если ее нет
        if not os.path.exists("frontend"):
            create_frontend_structure()
        else:
            print("✅ Структура фронтенда уже существует")
        
        print("\n1. Запуск API сервера с фронтендом...")
        
        # Запуск сервера в отдельном потоке
        def run_server():
            try:
                os.system("python -m uvicorn src.api.server:app --host 127.0.0.1 --port 5000 --reload")
            except Exception as e:
                print(f"❌ Ошибка сервера: {e}")
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        time.sleep(3)
        
        print("\n📢 Система запущена:")
        print("- Фронтенд: http://localhost:5000/")
        print("- API сервер: http://localhost:5000/api/docs")
        print("- Вход в систему: http://localhost:5000/login")
        print("- Админ-панель: http://localhost:5000/admin")
        print("\n🔑 Тестовый аккаунт:")
        print("  Логин: admin")
        print("  Пароль: admin123")
        print("\n⏹️ Для остановки нажмите Ctrl+C")
        
        # Ждем
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Система остановлена")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

def init_system():
    """Инициализировать систему"""
    print("\n🔧 Инициализация системы...")
    
    # Инициализируем базу данных
    db_manager.init_database()
    
    # Создаем необходимые директории
    os.makedirs("data/sessions", exist_ok=True)
    os.makedirs("src/api", exist_ok=True)
    os.makedirs("frontend", exist_ok=True)
    
    print("✅ Система инициализирована")
    print("📁 Созданы папки: data/, data/sessions/, src/api/, frontend/")
    return True

def main():
    """Главная функция"""
    print("=" * 60)
    print("🤖 TELEGRAM AUTOPOSTING SYSTEM v2.0")
    print("=" * 60)
    print("📁 Полная версия с фронтендом и API")
    print("=" * 60)
    
    # Проверяем зависимости
    if not check_dependencies():
        return
    
    # Инициализируем систему (с исправленной БД)
    if not init_system():
        return
    
    # Проверяем, запускаем ли на Railway
    if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("PORT"):
        print("\n🚀 Обнаружена среда Railway, запускаем полную версию...")
        railway_start()
    else:
        # Показываем меню для локального запуска
        while True:
            main_menu()
            print("\n" + "=" * 60)
            print("Возврат в главное меню...")
            print("=" * 60)

def main_menu():
    """Главное меню"""
    print("\n" + "=" * 50)
    print("🤖 TELEGRAM AUTOPOSTING - ГЛАВНОЕ МЕНЮ v2.0")
    print("=" * 50)
    
    print("\n1. Запустить систему с фронтендом (режим разработки)")
    print("2. Проверить Telegram API")
    print("3. Создать/обновить API файл")
    print("4. Создать/обновить фронтенд")
    print("5. Выход")
    
    while True:
        choice = input("\nВыберите вариант (1-5): ").strip()
        
        if choice == "1":
            run_development_mode()
            break
        elif choice == "2":
            test_telegram_api()
            break
        elif choice == "3":
            create_complete_api_file()
            break
        elif choice == "4":
            create_frontend_structure()
            break
        elif choice == "5":
            print("👋 До свидания!")
            sys.exit(0)
        else:
            print("❌ Неверный выбор")

def railway_start():
    """Запуск на Railway - ПОЛНАЯ ВЕРСИЯ"""
    print("=" * 60)
    print("🚀 TELEGRAM AUTOPOSTING - RAILWAY EDITION v2.0")
    print("=" * 60)
    
    # Проверяем зависимости
    if not check_dependencies():
        print("\n❌ Зависимости не установлены")
        return
    
    # Инициализируем систему (с исправленной БД)
    if not init_system():
        print("\n❌ Ошибка инициализации")
        return
    
    # Создаем полный API файл
    create_complete_api_file()
    
    # Создаем фронтенд
    create_frontend_structure()
    
    print("\n✅ Система инициализирована!")
    print("🚀 Запуск полной версии на Railway...")
    
    # Запуск API сервера
    if os.path.exists("src/api/server.py"):
        print("\n🌐 API будет доступен с фронтендом")
        try:
            import uvicorn
            port = int(os.getenv("PORT", 8000))
            print(f"📍 Порт: {port}")
            print(f"🌐 Домен: ваш-проект.railway.app")
            print(f"📚 Документация API: ваш-проект.railway.app/api/docs")
            
            uvicorn.run(
                "src.api.server:app",
                host="0.0.0.0",
                port=port,
                log_level="info"
            )
        except Exception as e:
            print(f"❌ Ошибка API: {e}")
    else:
        print("\n❌ API файл не найден")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Программа завершена")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()