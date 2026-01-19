#!/usr/bin/env python3
"""
Telegram AutoPosting - Стабильная версия для Railway
"""

import sys
import os
import logging
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """Проверить зависимости"""
    print("🔍 Проверка зависимостей...")
    
    required = ['fastapi', 'sqlalchemy', 'pyrogram', 'streamlit']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"❌ {package}")
    
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
        
        import sqlite3
        db_path = 'data/database.db'
        
        # Удаляем старую базу данных если она есть
        if os.path.exists(db_path):
            print("⚠️ Удаляем старую базу данных...")
            os.remove(db_path)
            print("✅ Старая БД удалена")
        
        # Создаем новую базу данных
        print("📁 Создаем новую базу данных...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Упрощенная схема БЕЗ password
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
        cursor.execute('INSERT INTO users (username, phone) VALUES (?, ?)', ('admin', '+79991234567'))
        cursor.execute('INSERT INTO users (username, phone) VALUES (?, ?)', ('user1', '+79997654321'))
        cursor.execute('INSERT INTO campaigns (name, message) VALUES (?, ?)', ('Первая рассылка', 'Привет! Это тест'))
        
        conn.commit()
        conn.close()
        
        print("✅ База данных создана")
        print("📍 Тестовый пользователь: admin / +79991234567")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_api():
    """Создать API"""
    print("\n📝 Создание API...")
    
    api_content = '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os

app = FastAPI(title="Telegram AutoPosting API", version="1.0.0")

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
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "local"),
        "endpoints": ["/", "/health", "/status", "/users", "/docs"]
    }

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

@app.get("/status")
def status():
    try:
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM campaigns")
        campaign_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "status": "ok",
            "users": user_count,
            "campaigns": campaign_count,
            "database": "connected"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/users")
def get_users():
    try:
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, phone, created_at FROM users")
        users = cursor.fetchall()
        conn.close()
        
        return {
            "users": [
                {
                    "id": u[0],
                    "username": u[1],
                    "phone": u[2],
                    "created_at": u[3]
                }
                for u in users
            ]
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/campaigns")
def get_campaigns():
    try:
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, message, status, created_at FROM campaigns")
        campaigns = cursor.fetchall()
        conn.close()
        
        return {
            "campaigns": [
                {
                    "id": c[0],
                    "name": c[1],
                    "message": c[2],
                    "status": c[3],
                    "created_at": c[4]
                }
                for c in campaigns
            ]
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/users")
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

@app.post("/campaigns")
def create_campaign(name: str, message: str):
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
        
        return {"status": "created", "campaign_id": campaign_id}
    except Exception as e:
        return {"error": str(e)}
'''
    
    os.makedirs("src/api", exist_ok=True)
    with open("src/api/server.py", "w", encoding="utf-8") as f:
        f.write(api_content)
    
    print("✅ API создан: src/api/server.py")
    return True

def start_api():
    """Запустить API сервер"""
    print("\n🚀 Запуск API сервера...")
    
    try:
        import uvicorn
        
        # Получаем порт из переменных окружения Railway
        port = int(os.getenv("PORT", 8000))
        
        print(f"🌐 API будет доступен на: http://0.0.0.0:{port}")
        print(f"📚 Документация: http://0.0.0.0:{port}/docs")
        
        # Запускаем uvicorn
        uvicorn.run(
            "src.api.server:app",
            host="0.0.0.0",
            port=port,
            log_level="info",
            reload=False  # На Railway reload не нужен
        )
    except Exception as e:
        print(f"❌ Ошибка запуска API: {e}")
        import traceback
        traceback.print_exc()

def create_admin_panel():
    """Создать админ-панель"""
    print("\n📝 Создание админ-панели...")
    
    admin_content = '''import streamlit as st
import sqlite3
import pandas as pd
import time
import os

st.set_page_config(
    page_title="Telegram AutoPosting",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Telegram AutoPosting Admin")

# Информация о среде
st.sidebar.info(f"**Среда:** {os.getenv('RAILWAY_ENVIRONMENT', 'Локальная')}")
st.sidebar.info(f"**Порт API:** {os.getenv('PORT', 8000)}")

# Навигация
page = st.sidebar.selectbox(
    "Навигация",
    ["📊 Дашборд", "👥 Пользователи", "📢 Рассылки", "ℹ️ О системе"]
)

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
        
        # Последние записи
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Последние пользователи")
            users_df = pd.read_sql("SELECT username, phone, created_at FROM users ORDER BY id DESC LIMIT 5", conn)
            if not users_df.empty:
                st.dataframe(users_df, use_container_width=True, hide_index=True)
            else:
                st.info("Нет пользователей")
        
        with col2:
            st.subheader("Последние рассылки")
            campaigns_df = pd.read_sql("SELECT name, status, created_at FROM campaigns ORDER BY id DESC LIMIT 5", conn)
            if not campaigns_df.empty:
                st.dataframe(campaigns_df, use_container_width=True, hide_index=True)
            else:
                st.info("Нет рассылок")
        
        conn.close()
        
    except Exception as e:
        st.error(f"Ошибка БД: {e}")

elif page == "👥 Пользователи":
    st.header("👥 Управление пользователями")
    
    # Показать всех пользователей
    try:
        conn = sqlite3.connect('data/database.db')
        users_df = pd.read_sql("SELECT * FROM users ORDER BY id", conn)
        conn.close()
        
        if not users_df.empty:
            st.dataframe(users_df, use_container_width=True, hide_index=True)
        else:
            st.info("Нет пользователей")
    except Exception as e:
        st.error(f"Ошибка БД: {e}")
    
    # Добавить пользователя
    with st.expander("➕ Добавить пользователя", expanded=True):
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
    
    # Показать все рассылки
    try:
        conn = sqlite3.connect('data/database.db')
        campaigns_df = pd.read_sql("SELECT * FROM campaigns ORDER BY id", conn)
        conn.close()
        
        if not campaigns_df.empty:
            st.dataframe(campaigns_df, use_container_width=True, hide_index=True)
        else:
            st.info("Нет рассылок")
    except Exception as e:
        st.error(f"Ошибка БД: {e}")
    
    # Создать рассылку
    with st.expander("➕ Создать рассылку", expanded=True):
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

elif page == "ℹ️ О системе":
    st.header("ℹ️ Информация о системе")
    
    st.success("""
    ## 🎉 Telegram AutoPosting успешно запущен!
    
    ### 📊 Статус системы:
    - ✅ API сервер: **работает**
    - ✅ База данных: **подключена**
    - ✅ Админ-панель: **доступна**
    
    ### 🌐 Доступные сервисы:
    - **API сервер:** `http://0.0.0.0:8000`
    - **Документация API:** `http://0.0.0.0:8000/docs`
    - **Админ-панель:** `http://0.0.0.0:8501`
    
    ### 📝 Основные endpointы:
    - `GET /` - Информация о сервисе
    - `GET /health` - Проверка здоровья
    - `GET /status` - Статус системы
    - `GET /users` - Список пользователей
    - `GET /campaigns` - Список рассылок
    - `POST /users` - Добавить пользователя
    - `POST /campaigns` - Создать рассылку
    """)

# Футер
st.sidebar.markdown("---")
st.sidebar.caption(f"Telegram AutoPosting v1.0.0")
st.sidebar.caption(f"Время: {time.strftime('%Y-%m-%d %H:%M:%S')}")
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
        
        # Создаем админ-панель если нет
        if not os.path.exists("src/admin_panel/admin.py"):
            create_admin_panel()
        
        # Импортируем и запускаем Streamlit напрямую
        import subprocess
        import signal
        
        # Команда для запуска Streamlit
        cmd = [
            sys.executable,  # Используем текущий интерпретатор Python
            "-m", "streamlit", "run",
            "src/admin_panel/admin.py",
            "--server.port=8501",
            "--server.address=0.0.0.0",
            "--server.headless=true",
            "--browser.serverAddress=0.0.0.0",
            "--server.enableCORS=false",
            "--server.enableXsrfProtection=false"
        ]
        
        # Запускаем в отдельном процессе
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Даем время на запуск
        time.sleep(3)
        
        print(f"✅ Админ-панель запущена на порту 8501 (PID: {process.pid})")
        
        # Возвращаем процесс для отслеживания
        return process
        
    except Exception as e:
        print(f"❌ Ошибка запуска админ-панели: {e}")
        import traceback
        traceback.print_exc()
        return None

def railway_start():
    """Запуск на Railway"""
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
        create_api()
    
    print("\n🔄 Запуск сервисов...")
    
    # Запускаем админ-панель в отдельном процессе
    admin_process = start_admin_panel()
    
    if admin_process:
        print(f"✅ Админ-панель запущена (PID: {admin_process.pid})")
    
    # Даем время на запуск
    time.sleep(2)
    
    print("\n" + "=" * 60)
    print("✅ СИСТЕМА УСПЕШНО ЗАПУЩЕНА!")
    print("=" * 60)
    print(f"🌐 API сервер: http://0.0.0.0:{os.getenv('PORT', 8000)}")
    print(f"📚 Документация API: http://0.0.0.0:{os.getenv('PORT', 8000)}/docs")
    print(f"📊 Админ-панель: http://0.0.0.0:8501")
    print(f"🏥 Health check: http://0.0.0.0:{os.getenv('PORT', 8000)}/health")
    print("=" * 60)
    print("\n⚡ Запуск основного API сервера...\n")
    
    # Запускаем API сервер (это блокирующий вызов)
    start_api()

def main():
    """Главная функция для локального запуска"""
    print("=" * 50)
    print("🤖 TELEGRAM AUTOPOSTING SYSTEM")
    print("=" * 50)
    
    print("\n1. Запустить на Railway/Production")
    print("2. Проверить зависимости")
    print("3. Выход")
    
    choice = input("\nВыберите вариант (1-3): ").strip()
    
    if choice == "1":
        railway_start()
    elif choice == "2":
        check_dependencies()
    elif choice == "3":
        print("👋 До свидания!")
        sys.exit(0)

if __name__ == "__main__":
    try:
        # Проверяем, запускаем ли мы на Railway
        is_railway = os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("PORT")
        
        if is_railway:
            # На Railway всегда запускаем railway_start
            railway_start()
        else:
            # Локально показываем меню
            main()
    except KeyboardInterrupt:
        print("\n👋 Программа завершена")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)