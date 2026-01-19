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
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        
        # Создаем таблицы
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                message TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Добавляем админа по умолчанию
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, password, phone) 
            VALUES (?, ?, ?)
        ''', ('admin', 'admin123', '+79991234567'))
        
        conn.commit()
        conn.close()
        
        print("✅ База данных инициализирована")
        print("📍 Админ для входа: admin / admin123")
        
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
        "endpoints": ["/", "/health", "/docs"]
    }

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

@app.get("/api/status")
def status():
    import sqlite3
    import os
    
    try:
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM campaigns")
        campaign_count = cursor.fetchone()[0]
        conn.close()
        
        return {
            "users": user_count,
            "campaigns": campaign_count,
            "database": "ok",
            "uptime": "0"
        }
    except Exception as e:
        return {"error": str(e)}
'''
    
    os.makedirs("src/api", exist_ok=True)
    
    with open("src/api/server.py", "w", encoding="utf-8") as f:
        f.write(api_content)
    
    print("✅ API создан: src/api/server.py")

def start_api_server():
    """Запустить API сервер"""
    try:
        print("🚀 Запуск API сервера...")
        import uvicorn
        
        # Проверяем порт Railway
        port = int(os.getenv("PORT", 8000))
        
        uvicorn.run(
            "src.api.server:app",
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Ошибка API сервера: {e}")

def start_admin_panel():
    """Запустить админ-панель"""
    try:
        print("👨‍💼 Запуск админ-панели...")
        
        # Создаем базовую админ-панель если нет
        if not os.path.exists("src/admin_panel/admin.py"):
            create_basic_admin_panel()
        
        import streamlit.web.bootstrap
        from streamlit.web.cli import _main_run
        
        # Запускаем Streamlit в отдельном процессе
        sys.argv = ["streamlit", "run", "src/admin_panel/admin.py", "--server.port=8501", "--server.address=0.0.0.0"]
        _main_run()
    except Exception as e:
        print(f"❌ Ошибка админ-панели: {e}")

def create_basic_admin_panel():
    """Создать базовую админ-панель"""
    print("📝 Создание админ-панели...")
    
    admin_content = '''import streamlit as st
import sqlite3
import pandas as pd
import time

st.set_page_config(
    page_title="Telegram AutoPosting Admin",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Telegram AutoPosting Admin")

# Боковая панель
with st.sidebar:
    st.header("Навигация")
    page = st.selectbox("Выберите страницу:", ["📊 Дашборд", "👥 Пользователи", "📢 Рассылки"])
    
    st.markdown("---")
    st.button("🔄 Обновить данные")
    
    if st.button("🚪 Выход"):
        st.rerun()

if page == "📊 Дашборд":
    st.header("📊 Дашборд")
    
    # Подключаемся к БД
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
        st.dataframe(users_df)
        
        conn.close()
    except Exception as e:
        st.error(f"Ошибка БД: {e}")

elif page == "👥 Пользователи":
    st.header("👥 Управление пользователями")
    
    # Добавить пользователя
    with st.form("add_user"):
        st.subheader("Добавить пользователя")
        username = st.text_input("Имя пользователя")
        phone = st.text_input("Телефон")
        
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
                    st.success(f"Пользователь {username} добавлен!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Ошибка: {e}")
            else:
                st.error("Заполните все поля")

elif page == "📢 Рассылки":
    st.header("📢 Управление рассылками")
    
    with st.form("add_campaign"):
        st.subheader("Создать рассылку")
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
                    st.success(f"Рассылка '{name}' создана!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Ошибка: {e}")
            else:
                st.error("Заполните все поля")

st.markdown("---")
st.caption(f"Telegram AutoPosting v1.0.0 | {time.strftime('%Y-%m-%d %H:%M:%S')}")
'''
    
    os.makedirs("src/admin_panel", exist_ok=True)
    
    with open("src/admin_panel/admin.py", "w", encoding="utf-8") as f:
        f.write(admin_content)
    
    print("✅ Админ-панель создана")

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
    
    # Запускаем API сервер в отдельном потоке
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    
    # Ждем запуска API
    time.sleep(2)
    
    # Запускаем админ-панель в отдельном потоке
    admin_thread = threading.Thread(target=start_admin_panel, daemon=True)
    admin_thread.start()
    
    print("\n✅ Система запущена!")
    print(f"🌐 API: http://0.0.0.0:{os.getenv('PORT', 8000)}")
    print("📊 Админ-панель: http://0.0.0.0:8501")
    print("\n📝 Логи в реальном времени...")
    
    # Держим главный поток активным
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Остановка системы...")

def main():
    """Главная функция для локального запуска"""
    print("=" * 50)
    print("🤖 TELEGRAM AUTOPOSTING SYSTEM")
    print("=" * 50)
    
    if not check_dependencies():
        return
    
    if not init_system():
        return
    
    print("\n1. Запустить на Railway")
    print("2. Проверить Telegram API")
    print("3. Выход")
    
    choice = input("\nВыберите вариант: ").strip()
    
    if choice == "1":
        railway_start()
    elif choice == "2":
        print("Тест Telegram API...")
        # Здесь можно добавить тест
    elif choice == "3":
        print("👋 До свидания!")
        sys.exit(0)

if __name__ == "__main__":
    try:
        # Если запускаем на Railway
        if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_PROJECT_NAME"):
            railway_start()
        else:
            main()
    except KeyboardInterrupt:
        print("\n👋 Программа завершена")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()