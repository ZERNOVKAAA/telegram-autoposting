from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import logging

from ..database.database import get_db_manager
from ..database.models import User, Subscription

logger = logging.getLogger(__name__)

class SubscriptionManager:
    """Менеджер подписок"""
    
    def __init__(self, subscription_days: int = 7):
        self.subscription_days = subscription_days
        from .notification_manager import notification_manager
        self.notification_manager = notification_manager
    
    def create_subscription(self, user_id: int, days: Optional[int] = None, 
                          payment_amount: Optional[int] = None,
                          notes: Optional[str] = None) -> Optional[Subscription]:
        """Создать/продлить подписку"""
        if days is None:
            days = self.subscription_days
        
        db_manager = get_db_manager()
        
        with db_manager.get_session() as session:
            # Получаем пользователя
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                logger.error(f"Пользователь {user_id} не найден")
                return None
            
            # Получаем активную подписку (если есть)
            active_sub = None
            for sub in user.subscriptions:
                if sub.is_active and sub.end_date > datetime.now():
                    active_sub = sub
                    break
            
            start_date = datetime.now()
            
            if active_sub and active_sub.end_date > datetime.now():
                # Продление существующей подписки
                start_date = active_sub.end_date
            
            # Создаем новую подписку
            new_sub = Subscription(
                user_id=user_id,
                start_date=start_date,
                end_date=start_date + timedelta(days=days),
                is_active=True,
                payment_amount=payment_amount,
                payment_date=datetime.now() if payment_amount else None,
                notes=notes
            )
            
            session.add(new_sub)
            session.commit()
            
            # Отправляем уведомление админу
            self.notification_manager.send_subscription_created(
                user_id, user.username, days, payment_amount
            )
            
            logger.info(f"Создана подписка для пользователя {user_id} на {days} дней")
            return new_sub
    
    def check_subscription(self, user_id: int) -> Dict[str, Any]:
        """Проверить статус подписки пользователя"""
        db_manager = get_db_manager()
        
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return {"has_subscription": False, "error": "Пользователь не найден"}
            
            # Ищем активную подписку
            active_sub = None
            for sub in user.subscriptions:
                if sub.is_active and sub.end_date > datetime.now():
                    active_sub = sub
                    break
            
            if not active_sub:
                return {
                    "has_subscription": False,
                    "message": "Нет активной подписки",
                    "user": user.username
                }
            
            now = datetime.now()
            days_left = (active_sub.end_date - now).days
            hours_left = int((active_sub.end_date - now).seconds / 3600)
            
            result = {
                "has_subscription": True,
                "subscription": {
                    "id": active_sub.id,
                    "start_date": active_sub.start_date.strftime("%d.%m.%Y %H:%M"),
                    "end_date": active_sub.end_date.strftime("%d.%m.%Y %H:%M"),
                    "days_left": days_left,
                    "hours_left": hours_left,
                    "payment_amount": active_sub.payment_amount,
                    "is_active": active_sub.is_active
                },
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "is_admin": user.is_admin
                }
            }
            
            # Если подписка заканчивается сегодня - отправляем уведомление
            if days_left == 0 and hours_left < 24:
                self.notification_manager.send_subscription_expiring_soon(
                    user_id, user.username, hours_left
                )
            
            # Если подписка истекла, деактивируем ее
            if active_sub.end_date < now and active_sub.is_active:
                active_sub.is_active = False
                session.commit()
                
                # Отправляем уведомление об окончании
                self.notification_manager.send_subscription_expired(user_id, user.username)
                
                result["has_subscription"] = False
                result["message"] = "Подписка истекла"
            
            return result
    
    def get_user_subscriptions(self, user_id: int) -> List[Subscription]:
        """Получить все подписки пользователя"""
        db_manager = get_db_manager()
        
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return []
            
            # Сортируем по дате окончания (новые сверху)
            subscriptions = sorted(
                user.subscriptions,
                key=lambda x: x.end_date,
                reverse=True
            )
            
            return subscriptions
    
    def get_all_active_subscriptions(self) -> List[Dict[str, Any]]:
        """Получить все активные подписки"""
        db_manager = get_db_manager()
        
        with db_manager.get_session() as session:
            # Ищем все активные подписки
            active_subs = session.query(Subscription).filter(
                Subscription.is_active == True,
                Subscription.end_date > datetime.now()
            ).all()
            
            result = []
            for sub in active_subs:
                user = session.query(User).filter(User.id == sub.user_id).first()
                if user:
                    days_left = (sub.end_date - datetime.now()).days
                    result.append({
                        "id": sub.id,
                        "user_id": user.id,
                        "username": user.username,
                        "start_date": sub.start_date,
                        "end_date": sub.end_date,
                        "days_left": days_left,
                        "payment_amount": sub.payment_amount
                    })
            
            return result
    
    def check_expired_subscriptions(self):
        """Проверить и обработать истекшие подписки"""
        db_manager = get_db_manager()
        
        with db_manager.get_session() as session:
            # Находим подписки, которые истекли но еще помечены как активные
            expired_subs = session.query(Subscription).filter(
                Subscription.is_active == True,
                Subscription.end_date < datetime.now()
            ).all()
            
            expired_count = 0
            for sub in expired_subs:
                sub.is_active = False
                expired_count += 1
                
                # Получаем пользователя для уведомления
                user = session.query(User).filter(User.id == sub.user_id).first()
                if user:
                    self.notification_manager.send_subscription_expired(user.id, user.username)
            
            if expired_count > 0:
                session.commit()
                logger.info(f"Деактивировано {expired_count} истекших подписок")
            
            return expired_count

# Создаем глобальный экземпляр
subscription_manager = SubscriptionManager()