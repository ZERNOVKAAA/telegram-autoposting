#!/usr/bin/env python3
"""
Railway-специфичный запуск с принудительной очисткой БД
"""

import os
import sys
import sqlite3

# Принудительно удаляем старую БД
DB_PATH = 'data/database.db'

# Удаляем папку data полностью
if os.path.exists('data'):
    import shutil
    shutil.rmtree('data')
    print("🗑️ Папка data удалена")

# Создаем новую папку
os.makedirs('data', exist_ok=True)

# Создаем новую БД с правильной схемой
print("📁 Создаем новую базу данных...")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ПРАВИЛЬНАЯ схема - БЕЗ password
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
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

# Тестовые данные
cursor.execute("INSERT OR IGNORE INTO users (username, phone) VALUES (?, ?)", 
              ('admin', '+79991234567'))

conn.commit()
conn.close()
print("✅ Новая БД создана")

# Теперь запускаем твой main.py
print("\n🚀 Запуск основного приложения...")
exec(open("main.py").read())