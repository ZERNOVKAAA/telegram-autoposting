#!/usr/bin/env python3
"""
Фикс для Railway - пересоздает БД с правильной структурой
"""

import os
import sqlite3
import sys

def fix_database():
    print("🔧 Исправляем базу данных...")
    
    db_path = 'data/database.db'
    
    # Удаляем старую БД
    if os.path.exists(db_path):
        print(f"🗑️ Удаляем {db_path}")
        os.remove(db_path)
    
    # Создаем директорию
    os.makedirs("data", exist_ok=True)
    
    # Создаем новую БД
    print("📁 Создаем новую базу данных...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Новая схема БЕЗ password
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
    cursor.execute("INSERT INTO campaigns (name, message) VALUES (?, ?)", 
                  ('Тест', 'Привет!'))
    
    conn.commit()
    conn.close()
    
    print("✅ База данных исправлена!")
    return True

if __name__ == "__main__":
    fix_database()