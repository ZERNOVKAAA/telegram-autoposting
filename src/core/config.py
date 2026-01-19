import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class Config:
    """Конфигурация приложения"""
    
    # Пути
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    
    # Создаем необходимые папки
    for folder in ['sessions', 'logs', 'backups', 'temp']:
        (DATA_DIR / folder).mkdir(parents=True, exist_ok=True)
    
    # База данных
    DB_PATH = DATA_DIR / "database.db"
    
    # Сервер
    SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")
    SERVER_PORT = int(os.getenv("SERVER_PORT", "5000"))
    
    # Админ-панель
    ADMIN_HOST = os.getenv("ADMIN_HOST", "127.0.0.1")
    ADMIN_PORT = int(os.getenv("ADMIN_PORT", "8501"))
    
    # Telegram API
    API_ID = os.getenv("API_ID", "36543854")  # Ваш API ID
    API_HASH = os.getenv("API_HASH", "bf8037bc98bf353fc649506562968857")  # Ваш API Hash
    
    # Уведомления
    ADMIN_TELEGRAM_ID = os.getenv("ADMIN_TELEGRAM_ID", "")
    NOTIFICATION_BOT_TOKEN = os.getenv("NOTIFICATION_BOT_TOKEN", "")
    
    # Безопасность
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    SUBSCRIPTION_DAYS = 7  # Длительность подписки
    
    # Пути к файлам
    SESSIONS_DIR = DATA_DIR / "sessions"
    LOGS_DIR = DATA_DIR / "logs"
    
    @classmethod
    def validate(cls):
        """Проверить конфигурацию"""
        missing = []
        
        if not cls.API_ID or cls.API_ID == "":
            missing.append("API_ID")
        if not cls.API_HASH or cls.API_HASH == "":
            missing.append("API_HASH")
        
        if missing:
            print(f"⚠️ ВНИМАНИЕ: Не установлены переменные окружения: {', '.join(missing)}")
            print("Создайте файл .env в корне проекта со следующими переменными:")
            print("API_ID=ваш_api_id_из_my.telegram.org")
            print("API_HASH=ваш_api_hash_из_my.telegram.org")
            print("ADMIN_TELEGRAM_ID=ваш_telegram_id")
            print("NOTIFICATION_BOT_TOKEN=токен_бота_для_уведомлений")
            print("\nПока что система будет работать в тестовом режиме.")
        
        return len(missing) == 0

config = Config()