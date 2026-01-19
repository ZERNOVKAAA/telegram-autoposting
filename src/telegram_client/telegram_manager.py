from pyrogram import Client
from pyrogram.errors import (
    PhoneCodeInvalid, PhoneCodeExpired, SessionPasswordNeeded,
    FloodWait, PhoneNumberInvalid, PhoneNumberUnoccupied,
    ApiIdInvalid, ApiIdPublishedFlood
)
import asyncio
import logging
from typing import Optional, Dict, Any
from pathlib import Path
import json

# ИСПРАВЛЕННЫЕ ИМПОРТЫ
from .api_config import get_config
from ..core.config import config as app_config

logger = logging.getLogger(__name__)

class TelegramManager:
    """Менеджер для работы с Telegram API"""
    
    def __init__(self):
        config_data = get_config()
        self.api_id = config_data["api_id"]
        self.api_hash = config_data["api_hash"]
        
        # Путь к папке с сессиями
        self.sessions_dir = app_config.SESSIONS_DIR
        
        # ... остальной код