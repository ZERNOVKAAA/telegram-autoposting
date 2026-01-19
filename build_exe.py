"""
Скрипт для сборки EXE файла
"""

import os
import sys
import shutil
from pathlib import Path
import PyInstaller.__main__

def build_exe():
    """Собрать EXE файл"""
    print("🔨 Сборка EXE файла...")
    
    # Пути
    base_dir = Path(__file__).parent
    src_dir = base_dir / "src"
    
    # Очищаем предыдущие сборки
    for folder in ["build", "dist"]:
        if (base_dir / folder).exists():
            shutil.rmtree(base_dir / folder)
    
    # Создаем временный файл для сборки
    temp_main = base_dir / "temp_main.py"
    
    with open(temp_main, 'w', encoding='utf-8') as f:
        f.write('''
import sys
import os
import threading
import time
import subprocess

# Добавляем пути
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def run_server():
    """Запустить сервер в фоне"""
    from api.server import app
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="error")

def run_admin():
    """Запустить админ-панель"""
    admin_script = os.path.join(os.path.dirname(__file__), 'src', 'admin_panel', 'admin.py')
    subprocess.Popen([sys.executable, "-m", "streamlit", "run", admin_script, "--server.headless", "true"])

def run_client():
    """Запустить клиент"""
    from client_app.main_window import run_client
    run_client()

if __name__ == "__main__":
    # Запускаем сервер в отдельном потоке
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Ждем запуска сервера
    time.sleep(2)
    
    # Запускаем админ-панель в отдельном потоке
    admin_thread = threading.Thread(target=run_admin, daemon=True)
    admin_thread.start()
    
    # Запускаем клиент (блокирующий вызов)
    run_client()
''')
    
    try:
        # Параметры PyInstaller
        pyinstaller_args = [
            'temp_main.py',
            '--name=TelegramAutoPosting',
            '--onefile',
            '--windowed',
            '--icon=NONE',  # Можно добавить иконку: --icon=icon.ico
            '--add-data=src;src',
            '--add-data=requirements.txt;.',
            '--hidden-import=uvicorn.loops.auto',
            '--hidden-import=uvicorn.loops.asyncio',
            '--hidden-import=uvicorn.protocols.http.auto',
            '--hidden-import=uvicorn.protocols.http.h11_impl',
            '--hidden-import=uvicorn.protocols.websockets.auto',
            '--hidden-import=uvicorn.protocols.websockets.websockets_impl',
            '--hidden-import=streamlit',
            '--hidden-import=streamlit.web.cli',
            '--hidden-import=pyrogram',
            '--hidden-import=pyrogram.raw',
            '--hidden-import=sqlalchemy',
            '--hidden-import=sqlalchemy.ext',
            '--collect-all=streamlit',
            '--collect-all=pyrogram',
            '--collect-all=sqlalchemy',
        ]
        
        print("⏳ Начало сборки (это займет несколько минут)...")
        PyInstaller.__main__.run(pyinstaller_args)
        
        print(f"\n✅ Сборка завершена!")
        print(f"📦 EXE файл: {base_dir / 'dist' / 'TelegramAutoPosting.exe'}")
        
    finally:
        # Удаляем временный файл
        if temp_main.exists():
            temp_main.unlink()
        
        print("\n📝 ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ:")
        print("1. Файл TelegramAutoPosting.exe - это ВЕСЬ проект в одном файле")
        print("2. При первом запуске создастся папка в %APPDATA%/TelegramAutoPosting")
        print("3. Для входа в админ-панель откройте http://localhost:8501")
        print("4. Логин админа по умолчанию: admin / admin123 (СМЕНИТЕ!)")
        print("5. Для работы нужны API данные от Telegram (в настройках админ-панели)")

if __name__ == "__main__":
    build_exe()