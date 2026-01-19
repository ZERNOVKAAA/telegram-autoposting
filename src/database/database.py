import os
import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Менеджер базы данных"""
    
    def __init__(self, db_path=None):
        if db_path is None:
            app_data_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'TelegramAutoPosting', 'data')
            os.makedirs(app_data_dir, exist_ok=True)
            db_path = os.path.join(app_data_dir, 'database.db')
        
        self.db_path = db_path
        self._init_tables()
    
    def _init_tables(self):
        """Инициализировать таблицы"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            phone_number TEXT,
            first_name TEXT,
            last_name TEXT,
            username TEXT,
            subscription_end DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
        ''')
        
        # Таблица рассылок
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            message_text TEXT,
            scheduled_time TIMESTAMP,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Таблица настроек
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        ''')
        
        # Базовые настройки
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('admin_user', 'admin')")
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('admin_pass', 'admin123')")
        
        conn.commit()
        conn.close()
        
        logger.info(f"Таблицы созданы в {self.db_path}")
    
    def get_connection(self):
        """Получить подключение к БД"""
        return sqlite3.connect(self.db_path)
    
    # Другие методы работы с БД...

def init_database():
    """Функция для обратной совместимости"""
    db_manager = DatabaseManager()
    return db_manager