from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime, timedelta
import os

Base = declarative_base()

class User(Base):
    """Модель пользователя системы"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    telegram_contact = Column(String(100), nullable=True)  # Для связи
    created_at = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)  # Админ или нет
    
    # Связи
    subscriptions = relationship("Subscription", back_populates="user")
    telegram_accounts = relationship("TelegramAccount", back_populates="user")
    scenarios = relationship("Scenario", back_populates="user")
    campaigns = relationship("Campaign", back_populates="user")
    
    def get_active_subscription(self):
        """Получить активную подписку пользователя"""
        for sub in self.subscriptions:
            if sub.is_active and sub.end_date > datetime.now():
                return sub
        return None
    
    def has_active_subscription(self):
        """Проверить наличие активной подписки"""
        sub = self.get_active_subscription()
        return sub is not None

class Subscription(Base):
    """Модель подписки (7 дней)"""
    __tablename__ = 'subscriptions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    start_date = Column(DateTime, default=datetime.now)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    payment_amount = Column(Integer, nullable=True)  # Сумма оплаты
    payment_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # Связи
    user = relationship("User", back_populates="subscriptions")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Автоматически устанавливаем end_date на 7 дней вперед
        if not self.end_date:
            self.end_date = datetime.now() + timedelta(days=7)

class TelegramAccount(Base):
    """Модель Telegram аккаунта"""
    __tablename__ = 'telegram_accounts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    phone_number = Column(String(20), nullable=True)
    session_string = Column(Text, nullable=True)  # Сессия в строковом формате
    app_id = Column(Integer, nullable=True)
    app_hash = Column(String(100), nullable=True)
    is_authenticated = Column(Boolean, default=False)
    last_active = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # Связи
    user = relationship("User", back_populates="telegram_accounts")

class ScenarioStep(Base):
    """Шаг сценария (вложенная структура)"""
    __tablename__ = 'scenario_steps'
    
    id = Column(Integer, primary_key=True)
    scenario_id = Column(Integer, ForeignKey('scenarios.id'))
    step_number = Column(Integer, nullable=False)
    message_text = Column(Text, nullable=False)
    telegram_account_id = Column(Integer, nullable=True)  # Кто отправляет
    delay_seconds = Column(Integer, default=5)  # Задержка после предыдущего шага

class Scenario(Base):
    """Модель сценария прописей"""
    __tablename__ = 'scenarios'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    steps_data = Column(JSON, nullable=False)  # JSON с шагами: [{"text": "...", "account_id": 1, "delay": 5}]
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Связи
    user = relationship("User", back_populates="scenarios")
    campaigns = relationship("Campaign", back_populates="scenario")

class Campaign(Base):
    """Кампания (запущенный сценарий)"""
    __tablename__ = 'campaigns'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    scenario_id = Column(Integer, ForeignKey('scenarios.id'), nullable=False)
    group_link = Column(String(500), nullable=False)  # Ссылка на группу
    group_id = Column(Integer, nullable=True)  # ID группы (после парсинга)
    status = Column(String(20), default='pending')  # pending, running, completed, failed
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    messages_sent = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    
    # Связи
    user = relationship("User", back_populates="campaigns")
    scenario = relationship("Scenario", back_populates="campaigns")