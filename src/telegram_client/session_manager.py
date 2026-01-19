import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from ..core.config import config
from ..database.database import get_db_manager
from ..database.models import TelegramAccount
import hashlib

logger = logging.getLogger(__name__)

class SessionManager:
    """Менеджер сессий Telegram"""
    
    def __init__(self):
        self.sessions_dir = config.SESSIONS_DIR
    
    def save_session(self, user_id: int, session_data: Dict[str, Any]) -> bool:
        """Сохранить сессию в базу данных"""
        try:
            db_manager = get_db_manager()
            
            with db_manager.get_session() as session:
                # Проверяем, нет ли уже такого аккаунта
                existing = session.query(TelegramAccount).filter(
                    TelegramAccount.user_id == user_id,
                    TelegramAccount.phone_number == session_data.get('phone_number')
                ).first()
                
                if existing:
                    # Обновляем существующий
                    existing.session_string = session_data.get('session_string')
                    existing.is_authenticated = True
                    existing.app_id = session_data.get('app_id')
                    existing.app_hash = session_data.get('app_hash')
                else:
                    # Создаем новый
                    account = TelegramAccount(
                        user_id=user_id,
                        phone_number=session_data.get('phone_number'),
                        session_string=session_data.get('session_string'),
                        app_id=session_data.get('app_id'),
                        app_hash=session_data.get('app_hash'),
                        is_authenticated=True
                    )
                    session.add(account)
                
                session.commit()
                logger.info(f"Сессия сохранена для пользователя {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка сохранения сессии: {e}")
            return False
    
    def get_user_sessions(self, user_id: int) -> List[Dict[str, Any]]:
        """Получить все сессии пользователя"""
        try:
            db_manager = get_db_manager()
            
            with db_manager.get_session() as session:
                accounts = session.query(TelegramAccount).filter(
                    TelegramAccount.user_id == user_id,
                    TelegramAccount.is_authenticated == True
                ).all()
                
                result = []
                for account in accounts:
                    # Безопасно возвращаем информацию (без session_string)
                    result.append({
                        "id": account.id,
                        "phone_number": account.phone_number,
                        "is_authenticated": account.is_authenticated,
                        "created_at": account.created_at,
                        "last_active": account.last_active
                    })
                
                return result
                
        except Exception as e:
            logger.error(f"Ошибка получения сессий: {e}")
            return []
    
    def get_session_string(self, session_id: int, user_id: int) -> Optional[str]:
        """Получить session_string для аккаунта"""
        try:
            db_manager = get_db_manager()
            
            with db_manager.get_session() as session:
                account = session.query(TelegramAccount).filter(
                    TelegramAccount.id == session_id,
                    TelegramAccount.user_id == user_id,
                    TelegramAccount.is_authenticated == True
                ).first()
                
                if account and account.session_string:
                    return account.session_string
                
                return None
                
        except Exception as e:
            logger.error(f"Ошибка получения session_string: {e}")
            return None
    
    def delete_session(self, session_id: int, user_id: int) -> bool:
        """Удалить сессию"""
        try:
            db_manager = get_db_manager()
            
            with db_manager.get_session() as session:
                account = session.query(TelegramAccount).filter(
                    TelegramAccount.id == session_id,
                    TelegramAccount.user_id == user_id
                ).first()
                
                if account:
                    session.delete(account)
                    session.commit()
                    logger.info(f"Сессия {session_id} удалена для пользователя {user_id}")
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"Ошибка удаления сессии: {e}")
            return False
    
    def validate_all_sessions(self) -> Dict[str, Any]:
        """Проверить все сессии на валидность"""
        # Здесь должна быть логика проверки сессий через Telegram API
        # Пока возвращаем заглушку
        return {
            "total": 0,
            "valid": 0,
            "invalid": 0,
            "details": []
        }
    
    def backup_sessions(self, backup_path: Optional[Path] = None) -> bool:
        """Создать резервную копию всех сессий"""
        try:
            if backup_path is None:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = self.sessions_dir / f"backup_sessions_{timestamp}.json"
            
            db_manager = get_db_manager()
            
            with db_manager.get_session() as db_session:
                accounts = db_session.query(TelegramAccount).all()
                
                backup_data = []
                for account in accounts:
                    # Не сохраняем session_string в резервной копии (безопасность)
                    backup_data.append({
                        "id": account.id,
                        "user_id": account.user_id,
                        "phone_number": account.phone_number,
                        "app_id": account.app_id,
                        "is_authenticated": account.is_authenticated,
                        "created_at": account.created_at.isoformat() if account.created_at else None,
                        "last_active": account.last_active.isoformat() if account.last_active else None
                    })
                
                with open(backup_path, 'w', encoding='utf-8') as f:
                    json.dump(backup_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"Резервная копия сессий создана: {backup_path}")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка создания резервной копии: {e}")
            return False

# Создаем глобальный экземпляр
session_manager = SessionManager()