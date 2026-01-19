# Инициализация ядра системы
from .auth_manager import AuthManager, get_auth_manager
from .subscription_manager import SubscriptionManager, subscription_manager
from .notification_manager import NotificationManager, notification_manager
from .config import config

__all__ = [
    'AuthManager', 'get_auth_manager',
    'SubscriptionManager', 'subscription_manager',
    'NotificationManager', 'notification_manager',
    'config'
]