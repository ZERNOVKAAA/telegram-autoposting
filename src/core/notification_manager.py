import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class NotificationManager:
    """Менеджер уведомлений"""
    
    def __init__(self):
        from .config import config
        self.bot_token = config.NOTIFICATION_BOT_TOKEN
        self.admin_chat_id = config.ADMIN_TELEGRAM_ID
    
    def send_telegram_message(self, chat_id: str, message: str) -> bool:
        """Отправить сообщение в Telegram"""
        if not self.bot_token or not chat_id:
            logger.warning("Не настроен Telegram бот для уведомлений")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Уведомление отправлено в Telegram: {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления в Telegram: {e}")
            return False
    
    def send_subscription_created(self, user_id: int, username: str, 
                                 days: int, amount: Optional[int] = None):
        """Уведомить о создании подписки"""
        amount_text = f"{amount} руб." if amount else "сумма не указана"
        message = (
            f"🎉 <b>Новая подписка создана!</b>\n\n"
            f"👤 Пользователь: <code>{username}</code> (ID: {user_id})\n"
            f"📅 Период: {days} дней\n"
            f"💰 Сумма: {amount_text}\n"
            f"⏰ Время: {self._current_time()}"
        )
        
        return self.send_telegram_message(self.admin_chat_id, message)
    
    def send_subscription_expiring_soon(self, user_id: int, username: str, hours_left: int):
        """Уведомить о скором окончании подписки"""
        message = (
            f"⚠️ <b>Подписка скоро закончится</b>\n\n"
            f"👤 Пользователь: <code>{username}</code> (ID: {user_id})\n"
            f"⏳ Осталось: {hours_left} часов\n"
            f"⏰ Время: {self._current_time()}"
        )
        
        return self.send_telegram_message(self.admin_chat_id, message)
    
    def send_subscription_expired(self, user_id: int, username: str):
        """Уведомить об окончании подписки"""
        message = (
            f"❌ <b>Подписка закончилась</b>\n\n"
            f"👤 Пользователь: <code>{username}</code> (ID: {user_id})\n"
            f"⏰ Время: {self._current_time()}"
        )
        
        return self.send_telegram_message(self.admin_chat_id, message)
    
    def send_user_registered(self, user_id: int, username: str, email: Optional[str] = None):
        """Уведомить о новой регистрации"""
        email_text = f"📧 Email: {email}" if email else ""
        message = (
            f"👤 <b>Новый пользователь зарегистрировался</b>\n\n"
            f"🆔 ID: {user_id}\n"
            f"👨‍💻 Логин: <code>{username}</code>\n"
            f"{email_text}\n"
            f"⏰ Время: {self._current_time()}"
        )
        
        return self.send_telegram_message(self.admin_chat_id, message)
    
    def send_error_notification(self, error_message: str, context: Optional[str] = None):
        """Отправить уведомление об ошибке"""
        context_text = f"Контекст: {context}" if context else ""
        message = (
            f"🚨 <b>Произошла ошибка</b>\n\n"
            f"📝 Сообщение: {error_message}\n"
            f"{context_text}\n"
            f"⏰ Время: {self._current_time()}"
        )
        
        return self.send_telegram_message(self.admin_chat_id, message)
    
    def _current_time(self):
        """Текущее время в формате"""
        from datetime import datetime
        return datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    
    def test_notification(self):
        """Тестовое уведомление (проверка работы)"""
        message = (
            f"🔔 <b>Тестовое уведомление</b>\n\n"
            f"Система уведомлений работает корректно!\n"
            f"⏰ Время: {self._current_time()}"
        )
        
        return self.send_telegram_message(self.admin_chat_id, message)

# Создаем глобальный экземпляр
notification_manager = NotificationManager()