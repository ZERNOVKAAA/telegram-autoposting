#!/usr/bin/env python3
"""
Telegram AutoPosting - Упрощенная версия для теста
"""

import sys
import os
import logging

logging.basicConfig(level=logging.INFO)
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
        except ImportError:
            missing.append(package)
            print(f"❌ {package}")
    
    if missing:
        print(f"\n⚠️ Отсутствуют: {', '.join(missing)}")
        print("Установите: pip install fastapi uvicorn sqlalchemy pyrogram streamlit PyQt6")
        return False
    
    print("\n✅ Все зависимости установлены")
    return True

def init_system():
    """Инициализировать систему"""
    print("\n🗄️ Инициализация базы данных...")
    
    try:
        # Инициализируем базу данных
        from src.database.database import init_database
        db_manager = init_database()
        
        print("✅ База данных инициализирована")
        print("📍 Админ для входа: admin / admin123")
        
        return db_manager
        
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        import traceback
        traceback.print_exc()
        return None

def main_menu():
    """Главное меню"""
    print("\n" + "=" * 50)
    print("🤖 TELEGRAM AUTOPOSTING - ГЛАВНОЕ МЕНЮ")
    print("=" * 50)
    
    print("\n1. Запустить систему (режим разработки)")
    print("2. Проверить Telegram API")
    print("3. Выход")
    
    while True:
        choice = input("\nВыберите вариант (1-3): ").strip()
        
        if choice == "1":
            run_development_mode()
            break
        elif choice == "2":
            test_telegram_api()
            break
        elif choice == "3":
            print("👋 До свидания!")
            sys.exit(0)
        else:
            print("❌ Неверный выбор")

def run_development_mode():
    """Запустить в режиме разработки"""
    print("\n🔧 Запуск в режиме разработки...")
    
    try:
        # Сначала проверим, есть ли необходимые файлы
        if not os.path.exists("src/api/server.py"):
            print("❌ Файл src/api/server.py не найден")
            print("Создайте базовый файл API")
            create_basic_api_file()
        
        print("1. Запуск API сервера...")
        import subprocess
        import threading
        import time
        
        # Запуск сервера в отдельном потоке
        def run_server():
            try:
                # ИСПРАВЛЕНО: запуск через python -m
                os.system("python -m uvicorn src.api.server:app --host 127.0.0.1 --port 5000 --reload")
            except Exception as e:
                print(f"❌ Ошибка сервера: {e}")
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        time.sleep(3)
        
        # Проверяем админ-панель
        if os.path.exists("src/admin_panel/admin.py"):
            print("2. Запуск админ-панели...")
            admin_thread = threading.Thread(
                target=lambda: os.system("python -m streamlit run src/admin_panel/admin.py"),  # ИСПРАВЛЕНО
                daemon=True
            )
            admin_thread.start()
            time.sleep(2)
        else:
            print("⚠️ Админ-панель не найдена (src/admin_panel/admin.py)")
            print("📝 Создание базовой админ-панели...")
            create_basic_admin_panel()
            time.sleep(1)
            admin_thread = threading.Thread(
                target=lambda: os.system("python -m streamlit run src/admin_panel/admin.py"),  # ИСПРАВЛЕНО
                daemon=True
            )
            admin_thread.start()
            time.sleep(2)
        
        print("3. Проверка системы...")
        print("\n📢 Система запущена:")
        print("- API сервер: http://localhost:5000")
        print("- Админ-панель: http://localhost:8501")
        print("- Документация API: http://localhost:5000/docs")
        print("\n⏹️ Для остановки нажмите Ctrl+C два раза")
        
        # Ждем
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Система остановлена")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

def test_telegram_api():
    """Тест Telegram API"""
    print("\n📱 Тест Telegram API...")
    
    try:
        # Проверяем наличие .env файла
        if not os.path.exists(".env"):
            print("❌ Файл .env не найден")
            print("Создайте файл .env с API_ID, API_HASH, PHONE")
            return
        
        from dotenv import load_dotenv
        load_dotenv()
        
        API_ID = os.getenv("API_ID")
        API_HASH = os.getenv("API_HASH")
        
        if not API_ID or not API_HASH:
            print("❌ API_ID или API_HASH не найдены в .env")
            return
        
        print(f"✅ API ID: {API_ID}")
        print(f"✅ API Hash: {API_HASH[:10]}...")
        
        # Простой тест Pyrogram с существующей сессией
        from pyrogram import Client
        
        print("\n🔄 Подключение к Telegram...")
        
        # Используем существующую сессию
        if os.path.exists("telegram_session.session"):
            print("📁 Используем сохраненную сессию...")
            client = Client("telegram_session")
        else:
            print("⚠️ Сессия не найдена, создаем новую...")
            PHONE = os.getenv("PHONE")
            if not PHONE:
                print("❌ PHONE не найден в .env")
                return
            
            client = Client(
                name="telegram_session",
                api_id=int(API_ID),
                api_hash=API_HASH,
                phone_number=PHONE
            )
        
        async def test_connection():
            await client.connect()
            me = await client.get_me()
            await client.disconnect()
            return me
        
        import asyncio
        me = asyncio.run(test_connection())
        
        if me:
            print(f"✅ Подключение успешно!")
            print(f"👤 Пользователь: {me.first_name or 'Не указано'}")
            print(f"📱 Телефон: {me.phone_number}")
            print(f"🆔 ID: {me.id}")
            print("\n🎉 Telegram API работает корректно!")
        else:
            print("❌ Не удалось подключиться")
            
    except Exception as e:
        print(f"❌ Ошибка Telegram API: {e}")
        import traceback
        traceback.print_exc()

def create_basic_api_file():
    """Создать базовый API файл"""
    print("\n📝 Создание базового API файла...")
    
    api_content = '''from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
'''
    
    os.makedirs("src/api", exist_ok=True)
    
    with open("src/api/server.py", "w", encoding="utf-8") as f:
        f.write(api_content)
    
    print("✅ Базовый API файл создан: src/api/server.py")

def create_basic_admin_panel():
    """Создать базовую админ-панель"""
    print("\n📝 Создание базовой админ-панели...")
    
    admin_content = '''import streamlit as st
import pandas as pd
import time

st.set_page_config(
    page_title="Telegram AutoPosting Admin",
    page_icon="🤖",
    layout="wide"
)

# Заголовок
st.title("🤖 Telegram AutoPosting Admin Panel")
st.markdown("---")

# Боковая панель
with st.sidebar:
    st.header("Навигация")
    menu_option = st.selectbox(
        "Выберите раздел:",
        ["📊 Дашборд", "👥 Пользователи", "📢 Рассылка", "⚙️ Настройки"]
    )
    
    st.markdown("---")
    st.info("Система управления автоматической рассылкой в Telegram")

# Основной контент
if menu_option == "📊 Дашборд":
    st.header("📊 Дашборд системы")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("👥 Пользователи", "125", "+12")
    
    with col2:
        st.metric("📢 Рассылки", "47", "+3")
    
    with col3:
        st.metric("✅ Успешно", "98%", "+2%")
    
    # Пример данных
    data = pd.DataFrame({
        'Дата': pd.date_range(start='2024-01-01', periods=10, freq='D'),
        'Отправлено': [10, 15, 12, 18, 20, 22, 19, 25, 30, 28],
        'Доставлено': [9, 14, 11, 17, 19, 21, 18, 24, 29, 27]
    })
    
    st.line_chart(data.set_index('Дата'))

elif menu_option == "👥 Пользователи":
    st.header("👥 Управление пользователями")
    
    # Таблица пользователей
    users_data = pd.DataFrame({
        'ID': [1, 2, 3, 4, 5],
        'Имя': ['Алексей', 'Мария', 'Иван', 'Ольга', 'Дмитрий'],
        'Телефон': ['+79991234567', '+79997654321', '+79995556677', '+79998887766', '+79993334455'],
        'Статус': ['Активен', 'Активен', 'Неактивен', 'Активен', 'Тестовый'],
        'Дата регистрации': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05']
    })
    
    st.dataframe(users_data, use_container_width=True)

elif menu_option == "📢 Рассылка":
    st.header("📢 Управление рассылками")
    
    # Форма создания рассылки
    with st.form("new_campaign"):
        st.subheader("Создать новую рассылку")
        
        campaign_name = st.text_input("Название рассылки")
        message_text = st.text_area("Текст сообщения", height=150)
        target_group = st.multiselect("Целевая группа", ["Все пользователи", "Активные", "Тестовые"])
        send_time = st.time_input("Время отправки")
        
        submitted = st.form_submit_button("Создать рассылку")
        
        if submitted:
            if campaign_name and message_text:
                st.success(f"Рассылка '{campaign_name}' создана!")
                st.info(f"Отправка в {send_time} для {len(target_group)} групп")
            else:
                st.error("Заполните все обязательные поля")

elif menu_option == "⚙️ Настройки":
    st.header("⚙️ Настройки системы")
    
    with st.form("settings_form"):
        st.subheader("Основные настройки")
        
        api_id = st.text_input("API ID", value="36543854")
        api_hash = st.text_input("API Hash", value="bf8037bc98...", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            max_users = st.number_input("Макс. пользователей", min_value=1, value=1000)
        with col2:
            messages_per_day = st.number_input("Сообщений в день", min_value=1, value=100)
        
        auto_backup = st.checkbox("Автоматическое резервное копирование", value=True)
        
        saved = st.form_submit_button("Сохранить настройки")
        if saved:
            st.success("Настройки сохранены!")
            
            # Имитация сохранения
            with st.spinner("Сохранение..."):
                time.sleep(1)

# Статус внизу
st.markdown("---")
st.caption(f"Telegram AutoPosting v1.0.0 | {time.strftime('%Y-%m-%d %H:%M:%S')}")
'''
    
    os.makedirs("src/admin_panel", exist_ok=True)
    
    with open("src/admin_panel/admin.py", "w", encoding="utf-8") as f:
        f.write(admin_content)
    
    print("✅ Базовая админ-панель создана: src/admin_panel/admin.py")

def main():
    """Главная функция"""
    print("=" * 50)
    print("🤖 TELEGRAM AUTOPOSTING SYSTEM")
    print("=" * 50)
    
    # Проверяем зависимости
    if not check_dependencies():
        return
    
    # Инициализируем систему
    db_manager = init_system()
    if not db_manager:
        return
    
    # Показываем меню
    while True:
        main_menu()
        print("\n" + "=" * 50)
        print("Возврат в главное меню...")
        print("=" * 50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Программа завершена")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()