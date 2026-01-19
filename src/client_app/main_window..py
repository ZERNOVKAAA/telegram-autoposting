import sys
import json
import requests
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTabWidget, QTableWidget,
    QTableWidgetItem, QTextEdit, QComboBox, QSpinBox, QMessageBox,
    QGroupBox, QFormLayout, QHeaderView, QDialog, QListWidget,
    QListWidgetItem, QCheckBox, QProgressBar, QSplitter, QFrame
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QDateTime
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette
from datetime import datetime, timedelta
import asyncio
import threading

class WorkerThread(QThread):
    """Поток для выполнения асинхронных задач"""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    
    def __init__(self, coroutine):
        super().__init__()
        self.coroutine = coroutine
    
    def run(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.coroutine)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class LoginDialog(QDialog):
    """Диалог входа/регистрации"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Telegram AutoPosting - Вход")
        self.setFixedSize(400, 300)
        
        self.token = None
        self.user_info = None
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("🤖 Telegram AutoPosting")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Вкладки
        self.tabs = QTabWidget()
        
        # Вкладка входа
        login_tab = QWidget()
        login_layout = QVBoxLayout()
        
        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Логин")
        login_layout.addWidget(QLabel("Логин:"))
        login_layout.addWidget(self.login_username)
        
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Пароль")
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        login_layout.addWidget(QLabel("Пароль:"))
        login_layout.addWidget(self.login_password)
        
        self.login_btn = QPushButton("Войти")
        self.login_btn.clicked.connect(self.login)
        login_layout.addWidget(self.login_btn)
        
        login_tab.setLayout(login_layout)
        
        # Вкладка регистрации
        register_tab = QWidget()
        register_layout = QVBoxLayout()
        
        self.reg_username = QLineEdit()
        self.reg_username.setPlaceholderText("Логин")
        register_layout.addWidget(QLabel("Логин:"))
        register_layout.addWidget(self.reg_username)
        
        self.reg_password = QLineEdit()
        self.reg_password.setPlaceholderText("Пароль")
        self.reg_password.setEchoMode(QLineEdit.EchoMode.Password)
        register_layout.addWidget(QLabel("Пароль:"))
        register_layout.addWidget(self.reg_password)
        
        self.reg_confirm = QLineEdit()
        self.reg_confirm.setPlaceholderText("Подтвердите пароль")
        self.reg_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        register_layout.addWidget(QLabel("Подтверждение:"))
        register_layout.addWidget(self.reg_confirm)
        
        self.reg_email = QLineEdit()
        self.reg_email.setPlaceholderText("Email (необязательно)")
        register_layout.addWidget(QLabel("Email:"))
        register_layout.addWidget(self.reg_email)
        
        self.reg_telegram = QLineEdit()
        self.reg_telegram.setPlaceholderText("@username (необязательно)")
        register_layout.addWidget(QLabel("Telegram:"))
        register_layout.addWidget(self.reg_telegram)
        
        self.register_btn = QPushButton("Зарегистрироваться")
        self.register_btn.clicked.connect(self.register)
        register_layout.addWidget(self.register_btn)
        
        register_tab.setLayout(register_layout)
        
        self.tabs.addTab(login_tab, "Вход")
        self.tabs.addTab(register_tab, "Регистрация")
        
        layout.addWidget(self.tabs)
        
        # Сообщение об ошибке
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setWordWrap(True)
        layout.addWidget(self.error_label)
        
        self.setLayout(layout)
    
    def login(self):
        username = self.login_username.text()
        password = self.login_password.text()
        
        if not username or not password:
            self.error_label.setText("Заполните все поля")
            return
        
        try:
            response = requests.post(
                "http://127.0.0.1:5000/api/auth/login",
                json={"username": username, "password": password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data['token']
                self.user_info = data['user']
                
                # Проверяем подписку
                if not data['subscription']['has_subscription']:
                    self.show_subscription_required(data['subscription']['message'])
                else:
                    self.accept()
            else:
                self.error_label.setText("Неверный логин или пароль")
                
        except requests.exceptions.ConnectionError:
            self.error_label.setText("Не удалось подключиться к серверу")
        except Exception as e:
            self.error_label.setText(f"Ошибка: {str(e)}")
    
    def register(self):
        username = self.reg_username.text()
        password = self.reg_password.text()
        confirm = self.reg_confirm.text()
        email = self.reg_email.text()
        telegram = self.reg_telegram.text()
        
        if not username or not password:
            self.error_label.setText("Заполните обязательные поля")
            return
        
        if password != confirm:
            self.error_label.setText("Пароли не совпадают")
            return
        
        try:
            response = requests.post(
                "http://127.0.0.1:5000/api/auth/register",
                json={
                    "username": username,
                    "password": password,
                    "email": email if email else None,
                    "telegram_contact": telegram if telegram else None
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data['token']
                self.user_info = data['user']
                self.accept()
            else:
                error_data = response.json()
                self.error_label.setText(error_data.get('detail', 'Ошибка регистрации'))
                
        except requests.exceptions.ConnectionError:
            self.error_label.setText("Не удалось подключиться к серверу")
        except Exception as e:
            self.error_label.setText(f"Ошибка: {str(e)}")
    
    def show_subscription_required(self, message):
        """Показать окно с предложением купить подписку"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Требуется подписка")
        dialog.setFixedSize(400, 200)
        
        layout = QVBoxLayout()
        
        label = QLabel(f"<h3>⚠️ {message}</h3>")
        label.setWordWrap(True)
        layout.addWidget(label)
        
        info = QLabel(
            "Для использования функционала требуется активная подписка.\n\n"
            "Свяжитесь с администратором в Telegram:\n"
            "<b>@ваш_админ_ник</b>\n\n"
            "После оплаты вам будет выдана подписка на 7 дней."
        )
        info.setWordWrap(True)
        layout.addWidget(info)
        
        btn = QPushButton("Закрыть")
        btn.clicked.connect(dialog.reject)
        layout.addWidget(btn)
        
        dialog.setLayout(layout)
        dialog.exec()

class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        self.token = None
        self.user_info = None
        self.telegram_accounts = []
        self.scenarios = []
        
        self.init_ui()
        
        # Таймер для проверки подписки
        self.subscription_timer = QTimer()
        self.subscription_timer.timeout.connect(self.check_subscription)
        self.subscription_timer.start(60000)  # Каждую минуту
    
    def init_ui(self):
        self.setWindowTitle("Telegram AutoPosting")
        self.setGeometry(100, 100, 1200, 800)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Верхняя панель
        top_panel = QWidget()
        top_layout = QHBoxLayout()
        
        self.user_label = QLabel("Не авторизован")
        self.user_label.setFont(QFont("Arial", 10))
        top_layout.addWidget(self.user_label)
        
        top_layout.addStretch()
        
        self.subscription_label = QLabel("Подписка: ❌ Нет")
        self.subscription_label.setStyleSheet("color: red; font-weight: bold;")
        top_layout.addWidget(self.subscription_label)
        
        self.logout_btn = QPushButton("Выйти")
        self.logout_btn.clicked.connect(self.logout)
        top_layout.addWidget(self.logout_btn)
        
        top_panel.setLayout(top_layout)
        main_layout.addWidget(top_panel)
        
        # Вкладки
        self.tabs = QTabWidget()
        
        # Вкладка аккаунтов
        self.accounts_tab = self.create_accounts_tab()
        self.tabs.addTab(self.accounts_tab, "👤 Аккаунты Telegram")
        
        # Вкладка сценариев
        self.scenarios_tab = self.create_scenarios_tab()
        self.tabs.addTab(self.scenarios_tab, "📝 Сценарии")
        
        # Вкладка запуска
        self.run_tab = self.create_run_tab()
        self.tabs.addTab(self.run_tab, "🚀 Запуск")
        
        # Вкладка статистики
        self.stats_tab = self.create_stats_tab()
        self.tabs.addTab(self.stats_tab, "📊 Статистика")
        
        main_layout.addWidget(self.tabs)
    
    def create_accounts_tab(self):
        """Создать вкладку управления аккаунтами"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Панель добавления аккаунта
        add_group = QGroupBox("Добавить аккаунт Telegram")
        add_layout = QFormLayout()
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("+79123456789")
        add_layout.addRow("Номер телефона:", self.phone_input)
        
        self.add_btn = QPushButton("Добавить")
        self.add_btn.clicked.connect(self.add_telegram_account)
        add_layout.addRow("", self.add_btn)
        
        add_group.setLayout(add_layout)
        layout.addWidget(add_group)
        
        # Список аккаунтов
        accounts_group = QGroupBox("Мои аккаунты")
        accounts_layout = QVBoxLayout()
        
        self.accounts_table = QTableWidget()
        self.accounts_table.setColumnCount(4)
        self.accounts_table.setHorizontalHeaderLabels([
            "ID", "Номер телефона", "Статус", "Действия"
        ])
        self.accounts_table.horizontalHeader().setStretchLastSection(True)
        
        accounts_layout.addWidget(self.accounts_table)
        accounts_group.setLayout(accounts_layout)
        
        layout.addWidget(accounts_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_scenarios_tab(self):
        """Создать вкладку сценариев"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Панель создания сценария
        create_group = QGroupBox("Создать сценарий")
        create_layout = QVBoxLayout()
        
        # Название сценария
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Название:"))
        self.scenario_name = QLineEdit()
        self.scenario_name.setPlaceholderText("Мой сценарий прописей")
        name_layout.addWidget(self.scenario_name)
        create_layout.addLayout(name_layout)
        
        # Описание
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("Описание:"))
        self.scenario_desc = QTextEdit()
        self.scenario_desc.setMaximumHeight(60)
        desc_layout.addWidget(self.scenario_desc)
        create_layout.addLayout(desc_layout)
        
        # Шаги сценария
        steps_group = QGroupBox("Шаги сценария")
        steps_layout = QVBoxLayout()
        
        # Таблица шагов
        self.steps_table = QTableWidget()
        self.steps_table.setColumnCount(5)
        self.steps_table.setHorizontalHeaderLabels([
            "№", "Текст сообщения", "Аккаунт", "Задержка (сек)", "Действия"
        ])
        
        # Кнопки управления шагами
        steps_btn_layout = QHBoxLayout()
        
        self.add_step_btn = QPushButton("➕ Добавить шаг")
        self.add_step_btn.clicked.connect(self.add_scenario_step)
        steps_btn_layout.addWidget(self.add_step_btn)
        
        self.clear_steps_btn = QPushButton("🗑️ Очистить")
        self.clear_steps_btn.clicked.connect(self.clear_scenario_steps)
        steps_btn_layout.addWidget(self.clear_steps_btn)
        
        steps_btn_layout.addStretch()
        
        steps_layout.addWidget(self.steps_table)
        steps_layout.addLayout(steps_btn_layout)
        steps_group.setLayout(steps_layout)
        
        create_layout.addWidget(steps_group)
        
        # Кнопка сохранения
        self.save_scenario_btn = QPushButton("💾 Сохранить сценарий")
        self.save_scenario_btn.clicked.connect(self.save_scenario)
        create_layout.addWidget(self.save_scenario_btn)
        
        create_group.setLayout(create_layout)
        layout.addWidget(create_group)
        
        # Список сохраненных сценариев
        saved_group = QGroupBox("Мои сценарии")
        saved_layout = QVBoxLayout()
        
        self.scenarios_table = QTableWidget()
        self.scenarios_table.setColumnCount(4)
        self.scenarios_table.setHorizontalHeaderLabels([
            "ID", "Название", "Шагов", "Действия"
        ])
        
        saved_layout.addWidget(self.scenarios_table)
        saved_group.setLayout(saved_layout)
        
        layout.addWidget(saved_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_run_tab(self):
        """Создать вкладку запуска"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Выбор сценария
        scenario_group = QGroupBox("Выбор сценария")
        scenario_layout = QFormLayout()
        
        self.scenario_combo = QComboBox()
        scenario_layout.addRow("Сценарий:", self.scenario_combo)
        
        self.refresh_scenarios_btn = QPushButton("🔄 Обновить список")
        self.refresh_scenarios_btn.clicked.connect(self.load_scenarios)
        scenario_layout.addRow("", self.refresh_scenarios_btn)
        
        scenario_group.setLayout(scenario_layout)
        layout.addWidget(scenario_group)
        
        # Настройки запуска
        settings_group = QGroupBox("Настройки запуска")
        settings_layout = QFormLayout()
        
        self.group_link = QLineEdit()
        self.group_link.setPlaceholderText("https://t.me/group_username или @group_username")
        settings_layout.addRow("Ссылка на группу:", self.group_link)
        
        self.delay_start = QSpinBox()
        self.delay_start.setRange(0, 3600)
        self.delay_start.setValue(5)
        self.delay_start.setSuffix(" сек")
        settings_layout.addRow("Задержка перед стартом:", self.delay_start)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Прогресс выполнения
        progress_group = QGroupBox("Выполнение")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        progress_layout.addWidget(self.log_text)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶️ Запустить")
        self.start_btn.clicked.connect(self.start_scenario)
        self.start_btn.setStyleSheet("font-size: 14px; padding: 10px;")
        btn_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹️ Остановить")
        self.stop_btn.clicked.connect(self.stop_scenario)
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_btn)
        
        self.clear_log_btn = QPushButton("🗑️ Очистить лог")
        self.clear_log_btn.clicked.connect(self.clear_log)
        btn_layout.addWidget(self.clear_log_btn)
        
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_stats_tab(self):
        """Создать вкладку статистики"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Информация о подписке
        subscription_group = QGroupBox("Моя подписка")
        subscription_layout = QFormLayout()
        
        self.subscription_status = QLabel("❌ Не активна")
        self.subscription_status.setStyleSheet("font-weight: bold; color: red;")
        subscription_layout.addRow("Статус:", self.subscription_status)
        
        self.subscription_end = QLabel("Нет данных")
        subscription_layout.addRow("Окончание:", self.subscription_end)
        
        self.days_left = QLabel("0")
        subscription_layout.addRow("Дней осталось:", self.days_left)
        
        subscription_group.setLayout(subscription_layout)
        layout.addWidget(subscription_group)
        
        # Статистика использования
        stats_group = QGroupBox("Статистика")
        stats_layout = QFormLayout()
        
        self.total_scenarios = QLabel("0")
        stats_layout.addRow("Сценариев создано:", self.total_scenarios)
        
        self.total_campaigns = QLabel("0")
        stats_layout.addRow("Запусков выполнено:", self.total_campaigns)
        
        self.total_messages = QLabel("0")
        stats_layout.addRow("Сообщений отправлено:", self.total_messages)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Кнопка обновления
        refresh_btn = QPushButton("🔄 Обновить статистику")
        refresh_btn.clicked.connect(self.update_stats)
        layout.addWidget(refresh_btn)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def add_telegram_account(self):
        """Добавить аккаунт Telegram"""
        phone = self.phone_input.text().strip()
        if not phone:
            QMessageBox.warning(self, "Ошибка", "Введите номер телефона")
            return
        
        # Здесь должна быть логика начала авторизации через API
        QMessageBox.information(self, "Информация", f"Начата авторизация для {phone}")
    
    def add_scenario_step(self):
        """Добавить шаг в сценарий"""
        row = self.steps_table.rowCount()
        self.steps_table.insertRow(row)
        
        # Номер шага
        step_num = QTableWidgetItem(str(row + 1))
        step_num.setFlags(step_num.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.steps_table.setItem(row, 0, step_num)
        
        # Текст сообщения
        text_item = QTableWidgetItem("Введите текст сообщения...")
        self.steps_table.setItem(row, 1, text_item)
        
        # Выбор аккаунта
        account_combo = QComboBox()
        account_combo.addItem("Выберите аккаунт...")
        for acc in self.telegram_accounts:
            account_combo.addItem(f"{acc['phone_number']} (ID: {acc['id']})", acc['id'])
        self.steps_table.setCellWidget(row, 2, account_combo)
        
        # Задержка
        delay_spin = QSpinBox()
        delay_spin.setRange(0, 3600)
        delay_spin.setValue(5)
        delay_spin.setSuffix(" сек")
        self.steps_table.setCellWidget(row, 3, delay_spin)
        
        # Кнопка удаления
        delete_btn = QPushButton("🗑️")
        delete_btn.clicked.connect(lambda: self.delete_scenario_step(row))
        self.steps_table.setCellWidget(row, 4, delete_btn)
    
    def delete_scenario_step(self, row):
        """Удалить шаг из сценария"""
        self.steps_table.removeRow(row)
        
        # Обновляем номера шагов
        for i in range(self.steps_table.rowCount()):
            self.steps_table.item(i, 0).setText(str(i + 1))
    
    def clear_scenario_steps(self):
        """Очистить все шаги сценария"""
        self.steps_table.setRowCount(0)
    
    def save_scenario(self):
        """Сохранить сценарий"""
        name = self.scenario_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название сценария")
            return
        
        if self.steps_table.rowCount() == 0:
            QMessageBox.warning(self, "Ошибка", "Добавьте хотя бы один шаг")
            return
        
        # Собираем шаги
        steps = []
        for row in range(self.steps_table.rowCount()):
            step_text = self.steps_table.item(row, 1).text()
            account_combo = self.steps_table.cellWidget(row, 2)
            delay_spin = self.steps_table.cellWidget(row, 3)
            
            account_id = account_combo.currentData()
            
            steps.append({
                "step_number": row + 1,
                "message": step_text,
                "account_id": account_id if account_id else None,
                "delay": delay_spin.value()
            })
        
        # Здесь должна быть логика сохранения через API
        QMessageBox.information(self, "Успех", f"Сценарий '{name}' сохранен")
        
        # Очищаем форму
        self.scenario_name.clear()
        self.scenario_desc.clear()
        self.clear_scenario_steps()
    
    def load_scenarios(self):
        """Загрузить список сценариев"""
        # Здесь должна быть логика загрузки через API
        pass
    
    def start_scenario(self):
        """Запустить сценарий"""
        if self.scenario_combo.count() == 0:
            QMessageBox.warning(self, "Ошибка", "Нет доступных сценариев")
            return
        
        group_link = self.group_link.text().strip()
        if not group_link:
            QMessageBox.warning(self, "Ошибка", "Введите ссылку на группу")
            return
        
        # Здесь должна быть логика запуска через API
        self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Запуск сценария...")
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
    
    def stop_scenario(self):
        """Остановить сценарий"""
        self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Остановка...")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    
    def clear_log(self):
        """Очистить лог"""
        self.log_text.clear()
    
    def check_subscription(self):
        """Проверить статус подписки"""
        if not self.token:
            return
        
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(
                "http://127.0.0.1:5000/api/subscription/check",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data['has_subscription']:
                    sub = data['subscription']
                    end_date = datetime.strptime(sub['end_date'], '%d.%m.%Y %H:%M')
                    
                    self.subscription_label.setText(
                        f"Подписка: ✅ Активна (осталось {sub['days_left']} д.)"
                    )
                    self.subscription_label.setStyleSheet("color: green; font-weight: bold;")
                    
                    # Обновляем информацию в статистике
                    self.subscription_status.setText("✅ Активна")
                    self.subscription_status.setStyleSheet("color: green; font-weight: bold;")
                    self.subscription_end.setText(sub['end_date'])
                    self.days_left.setText(str(sub['days_left']))
                    
                    # Включаем функционал
                    self.enable_functionality(True)
                else:
                    self.subscription_label.setText("Подписка: ❌ Нет")
                    self.subscription_label.setStyleSheet("color: red; font-weight: bold;")
                    
                    # Обновляем информацию в статистике
                    self.subscription_status.setText("❌ Не активна")
                    self.subscription_status.setStyleSheet("color: red; font-weight: bold;")
                    self.subscription_end.setText("Нет данных")
                    self.days_left.setText("0")
                    
                    # Отключаем функционал
                    self.enable_functionality(False)
                    
                    # Показываем предупреждение если функционал используется
                    if self.tabs.currentIndex() > 0:  # Не на вкладке аккаунтов
                        QMessageBox.warning(
                            self,
                            "Подписка истекла",
                            "Ваша подписка истекла. Для продолжения работы свяжитесь с администратором."
                        )
            
        except Exception as e:
            print(f"Ошибка проверки подписки: {e}")
    
    def enable_functionality(self, enabled):
        """Включить/отключить функционал"""
        # Вкладка аккаунтов
        self.phone_input.setEnabled(enabled)
        self.add_btn.setEnabled(enabled)
        
        # Вкладка сценариев
        self.scenario_name.setEnabled(enabled)
        self.scenario_desc.setEnabled(enabled)
        self.add_step_btn.setEnabled(enabled)
        self.clear_steps_btn.setEnabled(enabled)
        self.save_scenario_btn.setEnabled(enabled)
        
        # Вкладка запуска
        self.scenario_combo.setEnabled(enabled)
        self.group_link.setEnabled(enabled)
        self.delay_start.setEnabled(enabled)
        self.start_btn.setEnabled(enabled)
        self.refresh_scenarios_btn.setEnabled(enabled)
    
    def update_stats(self):
        """Обновить статистику"""
        # Здесь должна быть логика загрузки статистики через API
        pass
    
    def logout(self):
        """Выйти из системы"""
        self.token = None
        self.user_info = None
        self.close()
    
    def set_user_info(self, token, user_info):
        """Установить информацию о пользователе"""
        self.token = token
        self.user_info = user_info
        self.user_label.setText(f"👤 {user_info['username']} (ID: {user_info['id']})")
        
        # Проверяем подписку сразу
        self.check_subscription()
        
        # Загружаем данные
        self.load_telegram_accounts()
        self.load_scenarios()
        self.update_stats()
    
    def load_telegram_accounts(self):
        """Загрузить Telegram аккаунты пользователя"""
        if not self.token:
            return
        
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(
                "http://127.0.0.1:5000/api/telegram/accounts",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    self.telegram_accounts = data['accounts']
                    
                    # Обновляем таблицу
                    self.accounts_table.setRowCount(len(self.telegram_accounts))
                    
                    for i, account in enumerate(self.telegram_accounts):
                        self.accounts_table.setItem(i, 0, QTableWidgetItem(str(account['id'])))
                        self.accounts_table.setItem(i, 1, QTableWidgetItem(account['phone_number'] or ""))
                        
                        status = "✅ Авторизован" if account['is_authenticated'] else "❌ Не авторизован"
                        self.accounts_table.setItem(i, 2, QTableWidgetItem(status))
                        
                        # Кнопка удаления
                        delete_btn = QPushButton("🗑️ Удалить")
                        delete_btn.clicked.connect(lambda: self.delete_telegram_account(account['id']))
                        self.accounts_table.setCellWidget(i, 3, delete_btn)
        
        except Exception as e:
            print(f"Ошибка загрузки аккаунтов: {e}")
    
    def delete_telegram_account(self, account_id):
        """Удалить Telegram аккаунт"""
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите удалить этот аккаунт?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Здесь должна быть логика удаления через API
            self.load_telegram_accounts()

def run_client():
    """Запустить клиентское приложение"""
    app = QApplication(sys.argv)
    
    # Показываем диалог входа
    login_dialog = LoginDialog()
    if login_dialog.exec() == QDialog.DialogCode.Accepted:
        # Запускаем главное окно
        window = MainWindow()
        window.set_user_info(login_dialog.token, login_dialog.user_info)
        window.show()
        
        sys.exit(app.exec())
    else:
        sys.exit(0)

if __name__ == "__main__":
    run_client()