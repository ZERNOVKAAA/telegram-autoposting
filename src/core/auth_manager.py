import hashlib
import jwt
import datetime
from typing import Optional, Dict, Any
import logging

from ..database.database import get_db_manager
from ..database.models import User, Subscription

logger = logging.getLogger(__name__)

class AuthManager:
    """Менеджер аутентификации и авторизации"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    def hash_password(self, password: str) -> str:
        """Хешировать пароль"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверить пароль"""
        return self.hash_password(plain_password) == hashed_password
    
    def create_user(self, username: str, password: str, email: str = None, 
                   telegram_contact: str = None) -> Optional[User]:
        """Создать нового пользователя"""
        db_manager = get_db_manager()
        
        with db_manager.get_session() as session:
            # Проверяем, нет ли уже такого пользователя
            existing = session.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing:
                logger.warning(f"Пользователь {username} уже существует")
                return None
            
            # Создаем пользователя
            user = User(
                username=username,
                email=email,
                password_hash=self.hash_password(password),
                telegram_contact=telegram_contact,
                is_active=True
            )
            
            session.add(user)
            session.commit()
            logger.info(f"Создан пользователь: {username}")
            
            # Создаем тестовую подписку на 1 день
            from datetime import datetime, timedelta
            
            test_sub = Subscription(
                user_id=user.id,
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=1),
                is_active=True,
                notes="Тестовая подписка (1 день)"
            )
            session.add(test_sub)
            session.commit()
            
            return user
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Аутентификация пользователя"""
        db_manager = get_db_manager()
        
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.username == username).first()
            
            if not user:
                logger.warning(f"Попытка входа несуществующего пользователя: {username}")
                return None
            
            if not user.is_active:
                logger.warning(f"Попытка входа неактивного пользователя: {username}")
                return None
            
            if not self.verify_password(password, user.password_hash):
                logger.warning(f"Неверный пароль для пользователя: {username}")
                return None
            
            logger.info(f"Успешная аутентификация: {username}")
            return user
    
    def create_token(self, user_id: int, username: str, is_admin: bool = False) -> str:
        """Создать JWT токен"""
        payload = {
            'user_id': user_id,
            'username': username,
            'is_admin': is_admin,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Верифицировать JWT токен"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Токен истек")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Неверный токен")
            return None
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Изменить пароль пользователя"""
        db_manager = get_db_manager()
        
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                logger.error(f"Пользователь {user_id} не найден")
                return False
            
            if not self.verify_password(old_password, user.password_hash):
                logger.warning(f"Неверный старый пароль для пользователя {user_id}")
                return False
            
            user.password_hash = self.hash_password(new_password)
            session.commit()
            logger.info(f"Пароль изменен для пользователя {user_id}")
            return True
    
    def create_admin_user(self, username: str, password: str, email: str = None) -> bool:
        """Создать администратора (только для инициализации)"""
        db_manager = get_db_manager()
        
        with db_manager.get_session() as session:
            existing = session.query(User).filter(User.username == username).first()
            if existing:
                logger.error(f"Администратор {username} уже существует")
                return False
            
            admin = User(
                username=username,
                email=email,
                password_hash=self.hash_password(password),
                is_admin=True,
                is_active=True
            )
            
            session.add(admin)
            session.commit()
            logger.info(f"Создан администратор: {username}")
            return True

# ============ ВАЖНО: Создаем глобальный экземпляр ============
# Не импортируем config здесь, создаем позже
auth_manager_instance = None

def init_auth_manager():
    """Инициализировать auth_manager после загрузки конфига"""
    global auth_manager_instance
    if auth_manager_instance is None:
        from .config import config
        auth_manager_instance = AuthManager(config.SECRET_KEY)
    return auth_manager_instance

def get_auth_manager():
    """Получить глобальный экземпляр auth_manager"""
    global auth_manager_instance
    if auth_manager_instance is None:
        return init_auth_manager()
    return auth_manager_instance