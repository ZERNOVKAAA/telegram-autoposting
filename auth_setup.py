import asyncio
import os
import sys
from pyrogram import Client
from dotenv import load_dotenv

load_dotenv()

async def setup_telegram():
    """Настройка и авторизация Telegram"""
    print("🔐 Настройка Telegram авторизации")
    
    API_ID = int(os.getenv("API_ID"))
    API_HASH = os.getenv("API_HASH")
    PHONE = os.getenv("PHONE")
    
    if not all([API_ID, API_HASH, PHONE]):
        print("❌ Ошибка: Проверьте .env файл (API_ID, API_HASH, PHONE)")
        return
    
    print(f"📱 Используется номер: {PHONE}")
    
    # Создаем клиент с новым именем сессии
    client = Client(
        "telegram_session",  # Имя файла сессии
        api_id=API_ID,
        api_hash=API_HASH,
        phone_number=PHONE,
        device_model="Python AutoPost",
        system_version="Windows 10",
        app_version="1.0",
        lang_code="ru"
    )
    
    try:
        print("🔄 Подключаемся к Telegram...")
        await client.start()
        
        # Получаем информацию о себе
        me = await client.get_me()
        print(f"✅ Авторизация успешна!")
        print(f"👤 Имя: {me.first_name}")
        print(f"📞 Телефон: {me.phone_number}")
        print(f"🆔 ID: {me.id}")
        
        print("\n💾 Сессия сохранена как 'telegram_session.session'")
        print("✅ Теперь можно запускать основную систему")
        
    except Exception as e:
        print(f"❌ Ошибка авторизации: {e}")
    finally:
        await client.stop()

if __name__ == "__main__":
    asyncio.run(setup_telegram())
    input("\nНажмите Enter для выхода...")