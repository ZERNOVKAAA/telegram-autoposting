#!/usr/bin/env python3
"""
Railway запуск - исправленная версия
"""

import os
import sys
import sqlite3

print("🚀 Запуск Telegram AutoPosting на Railway...")

# Принудительно удаляем старую БД
DB_PATH = '/tmp/database.db'  # Используем /tmp для Railway

# Удаляем старую БД если существует
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print("🗑️ Старая БД удалена")

# Создаем новую БД
print("📁 Создаем новую базу данных...")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ПРАВИЛЬНАЯ схема - БЕЗ password
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

# Тестовые данные
cursor.execute("INSERT INTO users (username, phone) VALUES (?, ?)", 
              ('admin', '+79991234567'))

conn.commit()
conn.close()
print("✅ База данных создана")

# Простое FastAPI приложение для Railway
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def root():
    return {
        "service": "Telegram AutoPosting",
        "status": "running",
        "database": "ready",
        "message": "🎉 Сервер работает!"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/users")
def get_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    
    return {"users": users}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"🌐 Сервер запускается на порту {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)