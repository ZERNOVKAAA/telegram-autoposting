#!/usr/bin/env python3
"""
Тест системы Telegram AutoPosting
"""

import sys
import os

# Добавляем текущую папку в путь
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 50)
print("🤖 ТЕСТ СИСТЕМЫ TELEGRAM AUTOPOSTING")
print("=" * 50)

# Тест 1: Проверка структуры
print("\n📁 Проверка структуры папок...")

required_folders = [
    "src",
    "src/core",
    "src/database", 
    "src/telegram_client",
    "data"
]

all_ok = True
for folder in required_folders:
    if os.path.exists(folder):
        print(f"✅ {folder}/")
    else:
        print(f"❌ {folder}/ (отсутствует)")
        all_ok = False

# Тест 2: Проверка файлов
print("\n📄 Проверка файлов...")

required_files = [
    "src/core/config.py",
    "src/core/auth_manager.py",
    "src/database/database.py",
    "src/telegram_client/api_config.py",
    ".env",
    "main.py"
]

for file in required_files:
    if os.path.exists(file):
        print(f"✅ {file}")
    else:
        print(f"❌ {file} (отсутствует)")
        all_ok = False

# Тест 3: Проверка импортов
print("\n🔗 Проверка импортов...")

try:
    print("1. Импорт config...")
    from src.core.config import config
    print(f"✅ Config загружен. API_ID: {config.API_ID}")
    
    print("2. Импорт database...")
    from src.database.database import DatabaseManager
    print("✅ DatabaseManager импортирован")
    
    print("3. Импорт auth_manager...")
    from src.core.auth_manager import AuthManager, init_auth_manager
    print("✅ AuthManager импортирован")
    
    # Инициализируем auth_manager
    auth_manager = init_auth_manager()
    print("✅ AuthManager инициализирован")
    
    print("\n🎉 Все импорты работают корректно!")
    
except Exception as e:
    print(f"❌ Ошибка импорта: {e}")
    import traceback
    traceback.print_exc()
    all_ok = False

# Итог
print("\n" + "=" * 50)
if all_ok:
    print("✅ СИСТЕМА ГОТОВА К РАБОТЕ!")
    print("\n📝 Запустите команду:")
    print("python main.py")
    print("\n👤 Для входа используйте:")
    print("Логин: admin")
    print("Пароль: admin123")
else:
    print("⚠️ Есть проблемы с системой")
    print("\n🛠️ Проверьте структуру папок и файлов")