#!/usr/bin/env python3
"""
Telegram AutoPosting - Версия для Railway
"""

import sys
import os
import logging
import threading
import time

# Для Railway: добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """Проверить зависимости"""
    print("🔍 Проверка зависимостей...")
    
    required = ['fastapi', 'sqlalchemy', 'pyrogram', 'streamlit', 'PyQt6']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError as e:
            missing.append(package)
            print(f"❌ {package}: {e}")
    
    if missing:
        print(f"\n⚠️ Отсутствуют: {', '.join(missing)}")
        return False
    
    print("\n✅ Все зависимости установлены")
    return True

def init_system():
    """Инициализировать систему"""
    print("\n🗄️ Инициализация базы данных...")
    
    try:
        # Создаем директорию для данных
        os.makedirs("data", exist_ok=True)
        
        # Простая инициализация БД для Railway
        import sqlite3
        db_path = 'data/database.db'
        
        # Проверяем существование БД
        db_exists = os.path.exists(db_path)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if not db_exists:
            print("📁 Создаем новую базу данных...")
            
            # Создаем таблицу users без колонки password (упрощенно)
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
            
            # Добавляем админа по умолчанию
            cursor.execute('''
                INSERT INTO users (username, phone) 
                VALUES (?, ?)
            ''', ('admin', '+79991234567'))
            
            conn.commit()
            print("✅ Новая база данных создана")
            print("📍 Админ: admin / +79991234567")
        else:
            print("📁 База данных уже существует")
            
            # Просто проверяем подключение
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"✅ Таблицы в БД: {[t[0] for t in tables]}")
            
        conn.close()
        
        print("✅ База данных инициализирована")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_basic_api():
    """Создать базовый API для Railway"""
    print("\n📝 Создание API...")
    
    api_content = '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os

app = FastAPI(title="Telegram AutoPosting API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "service": "Telegram AutoPosting",
        "status": "running",
        "version": "1.0.0",
        "endpoints": ["/", "/health", "/status", "/docs"]
    }

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

@app.get("/status")
def status():
    try:
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        
        # Считаем пользователей
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        # Считаем рассылки
        cursor.execute("SELECT COUNT(*) FROM campaigns")
        campaign_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "status": "ok",
            "users": user_count,
            "campaigns": campaign_count,
            "environment": os.getenv("RAILWAY_ENVIRONMENT", "local")
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/users")
def get_users():
    try:
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, phone, created_at FROM users")
        users = cursor.fetchall()
        conn.close()
        
        return {
            "users": [
                {"id": u[0], "username": u[1], "phone": u[2], "created_at": u[3]}
                for u in users
            ]
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/users")
def create_user(username: str, phone: str):
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
        
        return {"status": "created", "user_id": user_id}
    except Exception as e:
        return {"error": str(e)}
'''
    
    os.makedirs("src/api", exist_ok=True)
    
    with open("src/api/server.py", "w", encoding="utf-8") as f:
        f.write(api_content)
    
    print("✅ API создан: src/api/server.py")
    return True

def start_api_server():
    """Запустить API сервер"""
    try:
        print("🚀 Запуск API сервера...")
        
        # Проверяем порт Railway
        port = int(os.getenv("PORT", 8000))
        host = "0.0.0.0"
        
        print(f"🌐 Запуск на {host}:{port}")
        
        # Импортируем и запускаем uvicorn
        import uvicorn
        
        # Запускаем напрямую
        uvicorn.run(
            "src.api.server:app",
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        print(f"❌ Ошибка API сервера: {e}")
        import traceback
        traceback.print_exc()

def create_basic_admin_panel():
    """Создать базовую админ-панель"""
    print("📝 Создание админ-панели...")
    
    admin_content = '''import streamlit as st
import sqlite3
import pandas as pd
import time
import os

st.set_page_config(
    page_title="Telegram AutoPosting Admin",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Telegram AutoPosting Admin Panel")

# Проверяем окружение
st.sidebar.info(f"Environment: {os.getenv('RAILWAY_ENVIRONMENT', 'local')}")

# Боковая панель
with st.sidebar:
    st.header("Навигация")
    page = st.selectbox("Выберите страницу:", ["📊 Дашборд", "👥 Пользователи", "📢 Рассылки", "ℹ️ Информация"])
    
    st.markdown("---")
    
    if st.button("🔄 Обновить"):
        st.rerun()

if page == "📊 Дашборд":
    st.header("📊 Дашборд")
    
    try:
        conn = sqlite3.connect('data/database.db')
        
        # Статистика
        users_count = pd.read_sql("SELECT COUNT(*) as count FROM users", conn)['count'][0]
        campaigns_count = pd.read_sql("SELECT COUNT(*) as count FROM campaigns", conn)['count'][0]
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("👥 Пользователи", users_count)
        with col2:
            st.metric("📢 Рассылки", campaigns_count)
        
        # Последние пользователи
        st.subheader("Последние пользователи")
        users_df = pd.read_sql("SELECT id, username, phone, created_at FROM users ORDER BY id DESC LIMIT 10", conn)
        
        if not users_df.empty:
            st.dataframe(users_df, use_container_width=True)
        else:
            st.info("Нет пользователей")
        
        conn.close()
    except Exception as e:
        st.error(f"Ошибка БД: {e}")

elif page == "👥 Пользователи":
    st.header("👥 Управление пользователями")
    
    # Таблица пользователей
    try:
        conn = sqlite3.connect('data/database.db')
        users_df = pd.read_sql("SELECT * FROM users ORDER BY id", conn)
        conn.close()
        
        if not users_df.empty:
            st.dataframe(users_df, use_container_width=True)
        else:
            st.info("Нет пользователей")
    except Exception as e:
        st.error(f"Ошибка БД: {e}")
    
    # Добавить пользователя
    with st.expander("➕ Добавить пользователя"):
        with st.form("add_user_form"):
            username = st.text_input("Имя пользователя")
            phone = st.text_input("Телефон", placeholder="+79991234567")
            
            if st.form_submit_button("Добавить"):
                if username and phone:
                    try:
                        conn = sqlite3.connect('data/database.db')
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO users (username, phone) VALUES (?, ?)",
                            (username, phone)
                        )
                        conn.commit()
                        conn.close()
                        st.success(f"✅ Пользователь {username} добавлен!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Ошибка: {e}")
                else:
                    st.error("⚠️ Заполните все поля")

elif page == "📢 Рассылки":
    st.header("📢 Управление рассылками")
    
    # Таблица рассылок
    try:
        conn = sqlite3.connect('data/database.db')
        campaigns_df = pd.read_sql("SELECT * FROM campaigns ORDER BY id", conn)
        conn.close()
        
        if not campaigns_df.empty:
            st.dataframe(campaigns_df, use_container_width=True)
        else:
            st.info("Нет рассылок")
    except Exception as e:
        st.error(f"Ошибка БД: {e}")
    
    # Создать рассылку
    with st.expander("➕ Создать рассылку"):
        with st.form("add_campaign_form"):
            name = st.text_input("Название рассылки")
            message = st.text_area("Текст сообщения", height=100)
            
            if st.form_submit_button("Создать"):
                if name and message:
                    try:
                        conn = sqlite3.connect('data/database.db')
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO campaigns (name, message) VALUES (?, ?)",
                            (name, message)
                        )
                        conn.commit()
                        conn.close()
                        st.success(f"✅ Рассылка '{name}' создана!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Ошибка: {e}")
                else:
                    st.error("⚠️ Заполните все поля")

elif page == "ℹ️ Информация":
    st.header("ℹ️ Информация о системе")
    
    st.info("""
    ## Telegram AutoPosting System
    
    **Версия:** 1.0.0
    **Окружение:** Производственное
    **Платформа:** Railway
    
    ### Доступные сервисы:
    - **API сервер:** Порт 8000
    - **Админ-панель:** Порт 8501
    
    ### API endpoints:
    - `GET /` - Информация о сервисе
    - `GET /health` - Проверка здоровья
    - `GET /status` - Статус системы
    - `GET /api/users` - Список пользователей
    - `POST /api/users` - Добавить пользователя
    """)
    
    # Показать переменные окружения (без секретов)
    with st.expander("Переменные окружения"):
        env_vars = {
            "RAILWAY_ENVIRONMENT": os.getenv("RAILWAY_ENVIRONMENT"),
            "PORT": os.getenv("PORT"),
            "PYTHON_VERSION": os.getenv("PYTHON_VERSION"),
        }
        st.json(env_vars)

# Футер
st.markdown("---")
st.caption(f"Telegram AutoPosting v1.0.0 | {time.strftime('%Y-%m-%d %H:%M:%S')} | Railway")
'''
    
    os.makedirs("src/admin_panel", exist_ok=True)
    
    with open("src/admin_panel/admin.py", "w", encoding="utf-8") as f:
        f.write(admin_content)
    
    print("✅ Админ-панель создана: src/admin_panel/admin.py")
    return True

def start_admin_panel():
    """Запустить админ-панель"""
    try:
        print("👨‍💼 Запуск админ-панели...")
        
        # Создаем базовую админ-панель если нет
        if not os.path.exists("src/admin_panel/admin.py"):
            create_basic_admin_panel()
        
        # Простой запуск Streamlit
        import subprocess
        
        # Запускаем Streamlit в фоне
        subprocess.Popen([
            "streamlit", "run", "src/admin_panel/admin.py",
            "--server.port=8501",
            "--server.address=0.0.0.0",
            "--browser.serverAddress=0.0.0.0",
            "--server.headless=true",
            "--theme.base=light"
        ])
        
        print("✅ Админ-панель запущена на порту 8501")
        
    except Exception as e:
        print(f"❌ Ошибка админ-панели: {e}")
        import traceback
        traceback.print_exc()

def railway_start():
    """Старт на Railway"""
    print("=" * 60)
    print("🚀 TELEGRAM AUTOPOSTING - RAILWAY EDITION")
    print("=" * 60)
    
    # Проверяем зависимости
    if not check_dependencies():
        print("\n❌ Зависимости не установлены")
        return
    
    # Инициализируем систему
    if not init_system():
        print("\n❌ Ошибка инициализации")
        return
    
    # Создаем API если нет
    if not os.path.exists("src/api/server.py"):
        create_basic_api()
    
    print("\n🔄 Запуск сервисов...")
    
    # Запускаем админ-панель в отдельном потоке
    admin_thread = threading.Thread(target=start_admin_panel, daemon=True)
    admin_thread.start()
    
    # Даем время на запуск админ-панели
    time.sleep(2)
    
    print("\n✅ Система запущена!")
    print(f"🌐 API: http://0.0.0.0:{os.getenv('PORT', 8000)}")
    print("📊 Админ-панель: http://0.0.0.0:8501")
    print("\n🎯 Запуск API сервера...")
    
    # Запускаем API сервер (блокирующий вызов)
    start_api_server()

def main():
    """Главная функция для локального запуска"""
    print("=" * 50)
    print("🤖 TELEGRAM AUTOPOSTING SYSTEM")
    print("=" * 50)
    
    if not check_dependencies():
        return
    
    if not init_system():
        return
    
    print("\n1. Запустить на Railway/Production")
    print("2. Локальная разработка")
    print("3. Выход")
    
    choice = input("\nВыберите вариант (1-3): ").strip()
    
    if choice == "1":
        railway_start()
    elif choice == "2":
        print("\n🔧 Локальный запуск...")
        # Для локального запуска можно использовать railway_start
        os.environ["PORT"] = "8000"
        railway_start()
    elif choice == "3":
        print("👋 До свидания!")
        sys.exit(0)

if __name__ == "__main__":
    try:
        # Если запускаем на Railway или порт указан
        if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("PORT") or os.getenv("RAILWAY_PROJECT_NAME"):
            railway_start()
        else:
            main()
    except KeyboardInterrupt:
        print("\n👋 Программа завершена")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()