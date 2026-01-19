#!/usr/bin/env python3
"""
Фикс для регистрации - создает правильную схему БД
"""

import os
import sqlite3
import hashlib
from datetime import datetime, timedelta

def create_correct_database():
    print("🔧 Создаем правильную базу данных для регистрации...")
    
    db_path = 'data/database.db'
    
    # Удаляем старую БД
    if os.path.exists(db_path):
        print(f"🗑️ Удаляем {db_path}")
        os.remove(db_path)
    
    # Создаем директорию
    os.makedirs("data", exist_ok=True)
    
    # Создаем новую БД с ПРАВИЛЬНОЙ схемой
    print("📁 Создаем новую базу данных с таблицами для регистрации...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # ТАБЛИЦА users - ДЛЯ РЕГИСТРАЦИИ
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            password_hash TEXT NOT NULL,
            telegram_contact TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            is_admin BOOLEAN DEFAULT 0
        )
    ''')
    
    # ТАБЛИЦА subscriptions - для подписок
    cursor.execute('''
        CREATE TABLE subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_date TIMESTAMP NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            payment_amount INTEGER,
            payment_date TIMESTAMP,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # ТАБЛИЦА для аккаунтов Telegram
    cursor.execute('''
        CREATE TABLE telegram_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            phone_number TEXT,
            session_string TEXT,
            app_id INTEGER,
            app_hash TEXT,
            is_authenticated BOOLEAN DEFAULT 0,
            last_active TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Простая таблица campaigns для совместимости
    cursor.execute('''
        CREATE TABLE campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            message TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Создаем администратора
    admin_password = hashlib.sha256("admin123".encode()).hexdigest()
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, is_admin, is_active)
        VALUES (?, ?, ?, ?, ?)
    ''', ('admin', 'admin@example.com', admin_password, 1, 1))
    
    # Создаем тестовую подписку для админа
    end_date = datetime.now() + timedelta(days=365)
    cursor.execute('''
        INSERT INTO subscriptions (user_id, end_date, is_active, notes)
        VALUES (?, ?, ?, ?)
    ''', (1, end_date, 1, 'Администраторская подписка'))
    
    conn.commit()
    conn.close()
    
    print("✅ База данных создана!")
    print("\n👤 Тестовый администратор:")
    print("   Логин: admin")
    print("   Пароль: admin123")
    
    return True

if __name__ == "__main__":
    create_correct_database()
    
    # Также удаляем старые сессии
    if os.path.exists('telegram_session.session'):
        os.remove('telegram_session.session')
        print("🗑️ Удалена старая Telegram сессия")