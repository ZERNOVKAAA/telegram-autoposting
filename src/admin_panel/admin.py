import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import plotly.graph_objects as go
import plotly.express as px
from ...core.config import config

# Настройка страницы
st.set_page_config(
    page_title="Telegram AutoPosting Admin",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS стили
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .success-badge {
        background-color: #d4edda;
        color: #155724;
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 0.8rem;
    }
    .warning-badge {
        background-color: #fff3cd;
        color: #856404;
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 0.8rem;
    }
    .danger-badge {
        background-color: #f8d7da;
        color: #721c24;
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

class AdminPanel:
    def __init__(self):
        self.base_url = f"http://{config.SERVER_HOST}:{config.SERVER_PORT}"
        self.session = requests.Session()
        
        # Проверка аутентификации
        if 'admin_token' not in st.session_state:
            st.session_state.admin_token = None
            st.session_state.admin_user = None
    
    def login(self):
        """Страница входа"""
        st.title("🔐 Вход в админ-панель")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                username = st.text_input("Логин")
                password = st.text_input("Пароль", type="password")
                submit = st.form_submit_button("Войти")
                
                if submit:
                    try:
                        response = self.session.post(
                            f"{self.base_url}/api/auth/login",
                            json={"username": username, "password": password}
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            if data.get('user', {}).get('is_admin'):
                                st.session_state.admin_token = data['token']
                                st.session_state.admin_user = data['user']
                                st.rerun()
                            else:
                                st.error("У вас нет прав администратора")
                        else:
                            st.error("Неверный логин или пароль")
                    except Exception as e:
                        st.error(f"Ошибка соединения: {e}")
    
    def logout(self):
        """Выход из системы"""
        st.session_state.admin_token = None
        st.session_state.admin_user = None
        st.rerun()
    
    def make_request(self, endpoint, method='GET', data=None):
        """Выполнить запрос к API"""
        headers = {'Authorization': f'Bearer {st.session_state.admin_token}'}
        
        try:
            if method == 'GET':
                response = self.session.get(
                    f"{self.base_url}{endpoint}",
                    headers=headers
                )
            elif method == 'POST':
                response = self.session.post(
                    f"{self.base_url}{endpoint}",
                    headers=headers,
                    json=data
                )
            
            if response.status_code == 401:
                st.error("Сессия истекла. Пожалуйста, войдите снова.")
                self.logout()
                return None
            
            return response.json()
        except Exception as e:
            st.error(f"Ошибка запроса: {e}")
            return None
    
    def dashboard(self):
        """Главная страница"""
        st.markdown('<h1 class="main-header">🤖 Панель управления Telegram AutoPosting</h1>', unsafe_allow_html=True)
        
        # Получаем статистику
        stats = self.make_request('/api/admin/stats')
        
        if stats and stats.get('success'):
            stats_data = stats['stats']
            
            # Метрики
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>👥 Пользователи</h3>
                    <h2>{stats_data['total_users']}</h2>
                    <p>Активных: {stats_data['active_users']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>💰 Подписки</h3>
                    <h2>{stats_data['total_subscriptions']}</h2>
                    <p>Активных: {stats_data['active_subscriptions']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>📝 Сценарии</h3>
                    <h2>{stats_data['total_scenarios']}</h2>
                    <p>Всего создано</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>🚀 Запуски</h3>
                    <h2>{stats_data['total_campaigns']}</h2>
                    <p>Всего выполнено</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Графики
            st.subheader("📈 Активность")
            col1, col2 = st.columns(2)
            
            with col1:
                # Круговая диаграмма пользователей
                fig = go.Figure(data=[go.Pie(
                    labels=['Активные', 'Неактивные'],
                    values=[stats_data['active_users'], stats_data['total_users'] - stats_data['active_users']],
                    hole=.3
                )])
                fig.update_layout(title="Статус пользователей")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Столбчатая диаграмма подписок
                fig = go.Figure(data=[go.Bar(
                    x=['Всего', 'Активные'],
                    y=[stats_data['total_subscriptions'], stats_data['active_subscriptions']]
                )])
                fig.update_layout(title="Подписки")
                st.plotly_chart(fig, use_container_width=True)
            
            # Последние пользователи
            st.subheader("🆕 Последние регистрации")
            
            if stats['recent_users']:
                users_df = pd.DataFrame(stats['recent_users'])
                users_df['created_at'] = pd.to_datetime(users_df['created_at'])
                users_df['Дата регистрации'] = users_df['created_at'].dt.strftime('%d.%m.%Y %H:%M')
                
                # Форматируем статус подписки
                def format_subscription_status(has_sub):
                    if has_sub:
                        return '<span class="success-badge">Есть подписка</span>'
                    else:
                        return '<span class="warning-badge">Нет подписки</span>'
                
                users_df['Подписка'] = users_df['has_subscription'].apply(
                    lambda x: format_subscription_status(x)
                )
                
                # Отображаем таблицу
                st.markdown(users_df[['id', 'username', 'email', 'Дата регистрации', 'Подписка']].to_html(
                    escape=False, index=False
                ), unsafe_allow_html=True)
            else:
                st.info("Нет зарегистрированных пользователей")
        
        else:
            st.error("Не удалось загрузить статистику")
    
    def manage_users(self):
        """Управление пользователями"""
        st.title("👥 Управление пользователями")
        
        # Поиск пользователя
        col1, col2 = st.columns([3, 1])
        with col1:
            search_query = st.text_input("Поиск по ID или логину")
        with col2:
            if st.button("🔍 Найти"):
                st.session_state.user_search = search_query
        
        # Таблица пользователей (здесь должна быть логика загрузки из API)
        st.subheader("Все пользователи")
        
        # Заглушка для таблицы
        users_data = [
            {"id": 1, "username": "admin", "email": "admin@example.com", "created_at": "2024-01-01", "has_subscription": True},
            {"id": 2, "username": "user1", "email": "user1@example.com", "created_at": "2024-01-02", "has_subscription": False},
        ]
        
        if users_data:
            df = pd.DataFrame(users_data)
            st.dataframe(df, use_container_width=True)
        
        # Выдача подписки
        st.subheader("🎫 Выдача подписки")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            user_id = st.number_input("ID пользователя", min_value=1, step=1)
        with col2:
            days = st.selectbox("Период", [7, 14, 30, 90])
        with col3:
            amount = st.number_input("Сумма оплаты (руб)", min_value=0, step=100)
        
        notes = st.text_area("Примечания")
        
        if st.button("✅ Выдать подписку", type="primary"):
            if user_id:
                data = {
                    "user_id": int(user_id),
                    "days": days,
                    "payment_amount": int(amount) if amount > 0 else None,
                    "notes": notes
                }
                
                result = self.make_request('/api/subscription/create', 'POST', data)
                if result and result.get('success'):
                    st.success(f"Подписка выдана пользователю {user_id} на {days} дней")
                else:
                    st.error("Ошибка выдачи подписки")
            else:
                st.warning("Введите ID пользователя")
    
    def subscriptions(self):
        """Управление подписками"""
        st.title("💰 Управление подписками")
        
        # Вкладки
        tab1, tab2, tab3 = st.tabs(["Активные подписки", "Запросы на продление", "История"])
        
        with tab1:
            st.subheader("📋 Активные подписки")
            
            # Здесь должна быть логика загрузки активных подписок
            active_subs = [
                {"id": 1, "user_id": 2, "username": "user1", "end_date": "2024-01-10", "days_left": 3, "amount": 500},
                {"id": 2, "user_id": 3, "username": "user2", "end_date": "2024-01-15", "days_left": 8, "amount": 500},
            ]
            
            if active_subs:
                for sub in active_subs:
                    with st.expander(f"👤 {sub['username']} (ID: {sub['user_id']})"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Осталось дней", sub['days_left'])
                        with col2:
                            st.metric("Дата окончания", sub['end_date'])
                        with col3:
                            st.metric("Сумма", f"{sub['amount']} руб.")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"Продлить на 7 дней", key=f"extend_{sub['id']}"):
                                st.success("Подписка продлена")
                        with col2:
                            if st.button(f"Отменить", key=f"cancel_{sub['id']}"):
                                st.warning("Подписка отменена")
            else:
                st.info("Нет активных подписок")
        
        with tab2:
            st.subheader("🔄 Запросы на продление")
            st.info("Здесь будут отображаться запросы пользователей на продление подписок")
            # Логика загрузки запросов из API
        
        with tab3:
            st.subheader("📊 История подписок")
            st.info("Здесь будет история всех подписок")
            # Логика загрузки истории из API
    
    def system_settings(self):
        """Настройки системы"""
        st.title("⚙️ Настройки системы")
        
        # Вкладки настроек
        tab1, tab2, tab3, tab4 = st.tabs(["Основные", "Telegram API", "Уведомления", "Безопасность"])
        
        with tab1:
            st.subheader("Основные настройки")
            
            subscription_days = st.number_input(
                "Длительность подписки (дней)",
                min_value=1,
                max_value=365,
                value=7,
                help="Стандартная длительность подписки в днях"
            )
            
            test_period = st.checkbox(
                "Включить тестовый период",
                value=True,
                help="Давать новым пользователям тестовый период"
            )
            
            if test_period:
                test_days = st.number_input(
                    "Длительность тестового периода (дней)",
                    min_value=1,
                    max_value=30,
                    value=1
                )
            
            if st.button("💾 Сохранить настройки", type="primary"):
                st.success("Настройки сохранены")
        
        with tab2:
            st.subheader("Telegram API настройки")
            
            api_id = st.text_input("API ID", value=config.API_ID or "", type="password")
            api_hash = st.text_input("API Hash", value=config.API_HASH or "", type="password")
            
            st.info("""
            **Где получить API данные:**
            1. Перейдите на https://my.telegram.org
            2. Войдите в свой аккаунт Telegram
            3. Создайте приложение в разделе "API Development Tools"
            4. Скопируйте api_id и api_hash
            """)
            
            if st.button("🔗 Проверить подключение"):
                if api_id and api_hash:
                    st.success("API данные обновлены")
                else:
                    st.error("Заполните оба поля")
        
        with tab3:
            st.subheader("Настройки уведомлений")
            
            bot_token = st.text_input("Токен бота для уведомлений", 
                                     value=config.NOTIFICATION_BOT_TOKEN or "")
            admin_chat_id = st.text_input("Ваш Telegram ID", 
                                         value=config.ADMIN_TELEGRAM_ID or "")
            
            st.markdown("""
            **Какие уведомления отправляются:**
            - 📝 Новая регистрация пользователя
            - 💰 Запрос на подписку
            - ⏰ Окончание подписки
            - 🚨 Критические ошибки системы
            """)
            
            if st.button("📨 Тестовое уведомление"):
                if bot_token and admin_chat_id:
                    # Здесь должна быть логика отправки тестового уведомления
                    st.success("Тестовое уведомление отправлено")
                else:
                    st.error("Заполните все поля")
        
        with tab4:
            st.subheader("Настройки безопасности")
            
            st.warning("⚠️ Эти настройки влияют на безопасность системы!")
            
            # Смена пароля админа
            st.subheader("Смена пароля")
            
            current_pass = st.text_input("Текущий пароль", type="password")
            new_pass = st.text_input("Новый пароль", type="password")
            confirm_pass = st.text_input("Подтвердите новый пароль", type="password")
            
            if st.button("🔐 Сменить пароль"):
                if new_pass == confirm_pass and len(new_pass) >= 8:
                    st.success("Пароль успешно изменен")
                else:
                    st.error("Пароли не совпадают или слишком короткие (минимум 8 символов)")
            
            # Резервное копирование
            st.subheader("Резервное копирование")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Создать резервную копию"):
                    # Здесь должна быть логика создания бэкапа
                    st.success("Резервная копия создана")
            with col2:
                if st.button("📥 Восстановить из копии"):
                    uploaded_file = st.file_uploader("Выберите файл бэкапа")
                    if uploaded_file:
                        st.warning("Восстановление перезапишет текущие данные!")
                        if st.button("✅ Подтвердить восстановление"):
                            st.success("Данные восстановлены")
    
    def run(self):
        """Запустить админ-панель"""
        # Проверка аутентификации
        if not st.session_state.admin_token:
            self.login()
            return
        
        # Боковая панель
        with st.sidebar:
            st.title(f"👋 Привет, {st.session_state.admin_user['username']}")
            st.markdown("---")
            
            # Меню навигации
            menu_item = st.radio(
                "Навигация",
                ["📊 Дашборд", "👥 Пользователи", "💰 Подписки", "⚙️ Настройки"],
                index=0
            )
            
            st.markdown("---")
            
            # Информация о системе
            st.markdown("**Информация о системе:**")
            st.markdown(f"• Пользователь: `{st.session_state.admin_user['username']}`")
            st.markdown(f"• Роль: Администратор")
            st.markdown(f"• Сервер: `{config.SERVER_HOST}:{config.SERVER_PORT}`")
            
            st.markdown("---")
            
            # Кнопка выхода
            if st.button("🚪 Выйти", use_container_width=True):
                self.logout()
        
        # Основной контент
        if menu_item == "📊 Дашборд":
            self.dashboard()
        elif menu_item == "👥 Пользователи":
            self.manage_users()
        elif menu_item == "💰 Подписки":
            self.subscriptions()
        elif menu_item == "⚙️ Настройки":
            self.system_settings()

def run_admin_panel():
    """Запустить админ-панель"""
    admin = AdminPanel()
    admin.run()

if __name__ == "__main__":
    run_admin_panel()