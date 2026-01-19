#!/usr/bin/env python3
"""
Чистый старт - удаляет всё и создает заново
"""

import os
import shutil
import sys

def clean_all():
    print("🧹 Полная очистка...")
    
    # Удаляем всё что может содержать старые данные
    folders_to_remove = ['data', '__pycache__', '.pytest_cache']
    files_to_remove = ['telegram_session.session']
    
    for folder in folders_to_remove:
        if os.path.exists(folder):
            print(f"🗑️ Удаляем папку: {folder}")
            shutil.rmtree(folder)
    
    for file in files_to_remove:
        if os.path.exists(file):
            print(f"🗑️ Удаляем файл: {file}")
            os.remove(file)
    
    print("✅ Очистка завершена")
    return True

if __name__ == "__main__":
    clean_all()
    
    # Запускаем основной скрипт
    print("\n🚀 Запуск основного приложения...")
    os.system("python main.py")