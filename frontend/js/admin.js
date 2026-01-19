// Админ-панель Telegram AutoPosting

// Загрузка админ-дашборда
async function loadAdminDashboard() {
    const content = document.getElementById('admin-content');
    
    content.innerHTML = `
        <div class="mb-8">
            <h1 class="text-2xl font-bold text-gray-800 mb-2">Административная панель</h1>
            <p class="text-gray-600">Полный контроль над системой Telegram AutoPosting</p>
        </div>
        
        <!-- Карточки статистики -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div class="bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl shadow p-6">
                <div class="flex justify-between items-start">
                    <div>
                        <p class="text-blue-100">Всего пользователей</p>
                        <h3 id="total-users" class="text-3xl font-bold mt-2">0</h3>
                    </div>
                    <div class="bg-blue-400 p-3 rounded-lg">
                        <i class="fas fa-users text-xl"></i>
                    </div>
                </div>
                <p class="text-blue-100 text-sm mt-4">
                    <i class="fas fa-arrow-up mr-1"></i>
                    <span id="users-change">0</span> за сегодня
                </p>
            </div>
            
            <div class="bg-gradient-to-r from-green-500 to-green-600 text-white rounded-xl shadow p-6">
                <div class="flex justify-between items-start">
                    <div>
                        <p class="text-green-100">Активные подписки</p>
                        <h3 id="active-subs" class="text-3xl font-bold mt-2">0</h3>
                    </div>
                    <div class="bg-green-400 p-3 rounded-lg">
                        <i class="fas fa-crown text-xl"></i>
                    </div>
                </div>
                <p class="text-green-100 text-sm mt-4">
                    <i class="fas fa-clock mr-1"></i>
                    <span id="expiring-subs">0</span> истекает скоро
                </p>
            </div>
            
            <div class="bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-xl shadow p-6">
                <div class="flex justify-between items-start">
                    <div>
                        <p class="text-purple-100">Всего рассылок</p>
                        <h3 id="total-campaigns" class="text-3xl font-bold mt-2">0</h3>
                    </div>
                    <div class="bg-purple-400 p-3 rounded-lg">
                        <i class="fas fa-paper-plane text-xl"></i>
                    </div>
                </div>
                <p class="text-purple-100 text-sm mt-4">
                    <i class="fas fa-running mr-1"></i>
                    <span id="running-campaigns">0</span> запущено сейчас
                </p>
            </div>
            
            <div class="bg-gradient-to-r from-yellow-500 to-yellow-600 text-white rounded-xl shadow p-6">
                <div class="flex justify-between items-start">
                    <div>
                        <p class="text-yellow-100">Доход</p>
                        <h3 id="total-revenue" class="text-3xl font-bold mt-2">0 ₽</h3>
                    </div>
                    <div class="bg-yellow-400 p-3 rounded-lg">
                        <i class="fas fa-ruble-sign text-xl"></i>
                    </div>
                </div>
                <p class="text-yellow-100 text-sm mt-4">
                    <i class="fas fa-calendar-alt mr-1"></i>
                    <span id="today-revenue">0</span> ₽ сегодня
                </p>
            </div>
        </div>
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <!-- Последние пользователи -->
            <div class="bg-white border border-gray-200 rounded-xl shadow-sm p-6">
                <div class="flex justify-between items-center mb-6">
                    <h2 class="text-lg font-bold">Последние регистрации</h2>
                    <button onclick="loadAdminUsers()" class="text-blue-600 text-sm hover:text-blue-800">
                        Все пользователи →
                    </button>
                </div>
                <div id="recent-users" class="space-y-4">
                    <div class="text-center py-8">
                        <div class="loader mx-auto mb-2"></div>
                        <p class="text-gray-500">Загрузка...</p>
                    </div>
                </div>
            </div>
            
            <!-- Статистика по дням -->
            <div class="bg-white border border-gray-200 rounded-xl shadow-sm p-6">
                <h2 class="text-lg font-bold mb-6">Активность за 7 дней</h2>
                <div class="h-64 flex items-end space-x-2" id="activity-chart">
                    <div class="flex-1 flex flex-col items-center">
                        <div class="bg-blue-500 w-full rounded-t" style="height: 60%"></div>
                        <span class="text-xs text-gray-500 mt-2">ПН</span>
                    </div>
                    <div class="flex-1 flex flex-col items-center">
                        <div class="bg-blue-500 w-full rounded-t" style="height: 80%"></div>
                        <span class="text-xs text-gray-500 mt-2">ВТ</span>
                    </div>
                    <div class="flex-1 flex flex-col items-center">
                        <div class="bg-blue-500 w-full rounded-t" style="height: 45%"></div>
                        <span class="text-xs text-gray-500 mt-2">СР</span>
                    </div>
                    <div class="flex-1 flex flex-col items-center">
                        <div class="bg-blue-500 w-full rounded-t" style="height: 90%"></div>
                        <span class="text-xs text-gray-500 mt-2">ЧТ</span>
                    </div>
                    <div class="flex-1 flex flex-col items-center">
                        <div class="bg-blue-500 w-full rounded-t" style="height: 75%"></div>
                        <span class="text-xs text-gray-500 mt-2">ПТ</span>
                    </div>
                    <div class="flex-1 flex flex-col items-center">
                        <div class="bg-blue-500 w-full rounded-t" style="height: 40%"></div>
                        <span class="text-xs text-gray-500 mt-2">СБ</span>
                    </div>
                    <div class="flex-1 flex flex-col items-center">
                        <div class="bg-blue-500 w-full rounded-t" style="height: 30%"></div>
                        <span class="text-xs text-gray-500 mt-2">ВС</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Быстрые действия -->
        <div class="mt-8 bg-gray-50 rounded-xl p-6">
            <h2 class="text-lg font-bold mb-4">Быстрые действия</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <button onclick="openCreateUserModal()" class="bg-white border border-gray-300 rounded-lg p-4 text-left hover:bg-gray-50 transition">
                    <div class="text-blue-600 text-xl mb-2">
                        <i class="fas fa-user-plus"></i>
                    </div>
                    <p class="font-medium">Добавить пользователя</p>
                    <p class="text-sm text-gray-500">Создать нового пользователя</p>
                </button>
                
                <button onclick="openCreateSubscriptionModal()" class="bg-white border border-gray-300 rounded-lg p-4 text-left hover:bg-gray-50 transition">
                    <div class="text-green-600 text-xl mb-2">
                        <i class="fas fa-crown"></i>
                    </div>
                    <p class="font-medium">Выдать подписку</p>
                    <p class="text-sm text-gray-500">Активировать подписку</p>
                </button>
                
                <button onclick="openSystemSettingsModal()" class="bg-white border border-gray-300 rounded-lg p-4 text-left hover:bg-gray-50 transition">
                    <div class="text-purple-600 text-xl mb-2">
                        <i class="fas fa-cogs"></i>
                    </div>
                    <p class="font-medium">Настройки системы</p>
                    <p class="text-sm text-gray-500">Изменить параметры</p>
                </button>
                
                <button onclick="openBackupModal()" class="bg-white border border-gray-300 rounded-lg p-4 text-left hover:bg-gray-50 transition">
                    <div class="text-yellow-600 text-xl mb-2">
                        <i class="fas fa-download"></i>
                    </div>
                    <p class="font-medium">Резервная копия</p>
                    <p class="text-sm text-gray-500">Создать backup</p>
                </button>
            </div>
        </div>
    `;
    
    // Загружаем данные
    await loadAdminDashboardData();
}

async function loadAdminDashboardData() {
    try {
        // Заглушки - здесь должны быть реальные API запросы
        document.getElementById('total-users').textContent = '158';
        document.getElementById('users-change').textContent = '+5';
        document.getElementById('active-subs').textContent = '89';
        document.getElementById('expiring-subs').textContent = '3';
        document.getElementById('total-campaigns').textContent = '342';
        document.getElementById('running-campaigns').textContent = '12';
        document.getElementById('total-revenue').textContent = '45,600 ₽';
        document.getElementById('today-revenue').textContent = '2,400';
        
        // Заглушка для последних пользователей
        const recentUsers = document.getElementById('recent-users');
        recentUsers.innerHTML = `
            <div class="space-y-3">
                <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div class="flex items-center">
                        <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                            <i class="fas fa-user text-blue-600"></i>
                        </div>
                        <div>
                            <p class="font-medium">alexey_ivanov</p>
                            <p class="text-sm text-gray-500">10 минут назад</p>
                        </div>
                    </div>
                    <span class="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">Активен</span>
                </div>
                <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div class="flex items-center">
                        <div class="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center mr-3">
                            <i class="fas fa-user text-purple-600"></i>
                        </div>
                        <div>
                            <p class="font-medium">maria_smith</p>
                            <p class="text-sm text-gray-500">1 час назад</p>
                        </div>
                    </div>
                    <span class="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded">Тестовый</span>
                </div>
                <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div class="flex items-center">
                        <div class="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center mr-3">
                            <i class="fas fa-user text-green-600"></i>
                        </div>
                        <div>
                            <p class="font-medium">dmitry_kuznetsov</p>
                            <p class="text-sm text-gray-500">2 часа назад</p>
                        </div>
                    </div>
                    <span class="bg-red-100 text-red-800 text-xs px-2 py-1 rounded">Неактивен</span>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Ошибка загрузки дашборда:', error);
    }
}

// Управление пользователями
async function loadAdminUsers() {
    const content = document.getElementById('admin-content');
    
    content.innerHTML = `
        <div class="mb-8">
            <div class="flex justify-between items-center">
                <div>
                    <h1 class="text-2xl font-bold text-gray-800 mb-2">Управление пользователями</h1>
                    <p class="text-gray-600">Просмотр и управление всеми пользователями системы</p>
                </div>
                <button onclick="openCreateUserModal()" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                    <i class="fas fa-user-plus mr-2"></i>Добавить пользователя
                </button>
            </div>
        </div>
        
        <!-- Фильтры и поиск -->
        <div class="bg-white border border-gray-200 rounded-xl shadow-sm p-6 mb-6">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Поиск</label>
                    <input type="text" id="user-search" 
                           class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                           placeholder="ID, логин или email">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Статус</label>
                    <select id="user-status-filter" class="w-full px-4 py-2 border border-gray-300 rounded-lg">
                        <option value="">Все</option>
                        <option value="active">Активные</option>
                        <option value="inactive">Неактивные</option>
                        <option value="test">Тестовые</option>
                    </select>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Подписка</label>
                    <select id="user-subscription-filter" class="w-full px-4 py-2 border border-gray-300 rounded-lg">
                        <option value="">Все</option>
                        <option value="active">С подпиской</option>
                        <option value="expired">Без подписки</option>
                        <option value="expiring">Истекает</option>
                    </select>
                </div>
                <div class="flex items-end">
                    <button onclick="searchUsers()" class="w-full bg-gray-800 text-white px-4 py-2 rounded-lg hover:bg-gray-900">
                        <i class="fas fa-search mr-2"></i>Поиск
                    </button>
                </div>
            </div>
        </div>
        
        <!-- Таблица пользователей -->
        <div class="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Пользователь</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Контакт</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Статус</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Подписка</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Дата регистрации</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Действия</th>
                        </tr>
                    </thead>
                    <tbody id="users-table-body" class="bg-white divide-y divide-gray-200">
                        <tr>
                            <td colspan="7" class="px-6 py-8 text-center">
                                <div class="loader mx-auto mb-2"></div>
                                <p class="text-gray-500">Загрузка пользователей...</p>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <!-- Пагинация -->
            <div class="bg-gray-50 px-6 py-4 border-t border-gray-200">
                <div class="flex justify-between items-center">
                    <div class="text-sm text-gray-700">
                        Показано <span id="users-showing">0</span> из <span id="users-total">0</span>
                    </div>
                    <div class="flex space-x-2">
                        <button class="px-3 py-1 border border-gray-300 rounded text-sm">←</button>
                        <button class="px-3 py-1 bg-blue-600 text-white rounded text-sm">1</button>
                        <button class="px-3 py-1 border border-gray-300 rounded text-sm">2</button>
                        <button class="px-3 py-1 border border-gray-300 rounded text-sm">→</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Загружаем пользователей
    await loadUsersData();
}

async function loadUsersData() {
    try {
        // Заглушка - здесь должен быть API запрос к /api/admin/users
        const users = [
            { id: 1, username: 'admin', email: 'admin@example.com', phone: '+79991234567', 
              is_active: true, is_admin: true, has_subscription: true, created_at: '2024-01-01' },
            { id: 2, username: 'user1', email: 'user1@example.com', phone: '+79997654321',
              is_active: true, is_admin: false, has_subscription: true, created_at: '2024-01-02' },
            { id: 3, username: 'user2', email: 'user2@example.com', phone: '+79995556677',
              is_active: false, is_admin: false, has_subscription: false, created_at: '2024-01-03' },
            { id: 4, username: 'user3', email: 'user3@example.com', phone: '+79998887766',
              is_active: true, is_admin: false, has_subscription: true, created_at: '2024-01-04' },
            { id: 5, username: 'test_user', email: null, phone: '+79993334455',
              is_active: true, is_admin: false, has_subscription: false, created_at: '2024-01-05' }
        ];
        
        const tbody = document.getElementById('users-table-body');
        let html = '';
        
        users.forEach(user => {
            const statusBadge = user.is_active ? 
                `<span class="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">Активен</span>` :
                `<span class="bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full">Неактивен</span>`;
            
            const adminBadge = user.is_admin ? 
                `<span class="bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full ml-1">Админ</span>` : '';
            
            const subscriptionBadge = user.has_subscription ? 
                `<span class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">Есть подписка</span>` :
                `<span class="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded-full">Нет подписки</span>`;
            
            html += `
                <tr>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${user.id}</td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="flex items-center">
                            <div class="flex-shrink-0 h-10 w-10 bg-gray-100 rounded-full flex items-center justify-center">
                                <i class="fas fa-user text-gray-600"></i>
                            </div>
                            <div class="ml-4">
                                <div class="text-sm font-medium text-gray-900">${user.username}</div>
                                <div class="text-sm text-gray-500">${user.email || 'Нет email'}</div>
                            </div>
                            ${adminBadge}
                        </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <i class="fas fa-phone mr-1"></i>${user.phone}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">${statusBadge}</td>
                    <td class="px-6 py-4 whitespace-nowrap">${subscriptionBadge}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        ${user.created_at}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button onclick="openEditUserModal(${user.id})" class="text-blue-600 hover:text-blue-900 mr-3">
                            <i class="fas fa-edit"></i>
                        </button>
                        ${!user.is_admin ? `
                            <button onclick="openSubscriptionModal(${user.id})" class="text-green-600 hover:text-green-900 mr-3">
                                <i class="fas fa-crown"></i>
                            </button>
                            <button onclick="deleteUser(${user.id})" class="text-red-600 hover:text-red-900">
                                <i class="fas fa-trash"></i>
                            </button>
                        ` : ''}
                    </td>
                </tr>
            `;
        });
        
        tbody.innerHTML = html;
        document.getElementById('users-showing').textContent = users.length;
        document.getElementById('users-total').textContent = users.length;
        
    } catch (error) {
        document.getElementById('users-table-body').innerHTML = `
            <tr>
                <td colspan="7" class="px-6 py-8 text-center">
                    <div class="text-red-600">
                        <i class="fas fa-exclamation-circle mr-2"></i>
                        Ошибка загрузки: ${error.message}
                    </div>
                </td>
            </tr>
        `;
    }
}

function openCreateUserModal() {
    openAdminModal('Добавить пользователя', `
        <div class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Логин *</label>
                <input type="text" id="new-user-username" 
                       class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                       placeholder="Введите логин" required>
            </div>
            
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
                <input type="email" id="new-user-email" 
                       class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                       placeholder="email@example.com">
            </div>
            
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Телефон</label>
                <input type="tel" id="new-user-phone" 
                       class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                       placeholder="+79991234567">
            </div>
            
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Пароль *</label>
                    <input type="password" id="new-user-password" 
                           class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                           placeholder="Не менее 6 символов" required>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Подтверждение *</label>
                    <input type="password" id="new-user-password2" 
                           class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                           placeholder="Повторите пароль" required>
                </div>
            </div>
            
            <div class="flex items-center space-x-4">
                <div class="flex items-center">
                    <input type="checkbox" id="new-user-admin" class="h-4 w-4 text-blue-600 rounded">
                    <label for="new-user-admin" class="ml-2 text-sm text-gray-700">Администратор</label>
                </div>
                <div class="flex items-center">
                    <input type="checkbox" id="new-user-active" class="h-4 w-4 text-green-600 rounded" checked>
                    <label for="new-user-active" class="ml-2 text-sm text-gray-700">Активный</label>
                </div>
            </div>
            
            <div class="pt-4 border-t border-gray-200">
                <div class="flex justify-end space-x-3">
                    <button onclick="closeAdminModal()" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                        Отмена
                    </button>
                    <button onclick="createUser()" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                        Создать пользователя
                    </button>
                </div>
            </div>
        </div>
    `);
}

async function createUser() {
    // Логика создания пользователя
    closeAdminModal();
    showAdminNotification('Пользователь создан успешно', 'success');
    await loadUsersData();
}

function openSubscriptionModal(userId) {
    openAdminModal('Выдать подписку', `
        <div class="space-y-4">
            <div class="bg-blue-50 border-l-4 border-blue-500 p-4">
                <div class="flex">
                    <div class="flex-shrink-0">
                        <i class="fas fa-info-circle text-blue-500"></i>
                    </div>
                    <div class="ml-3">
                        <p class="text-sm text-blue-700">
                            Подписка дает доступ к полному функционалу системы на указанный период
                        </p>
                    </div>
                </div>
            </div>
            
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Пользователь ID</label>
                <input type="text" value="${userId}" disabled 
                       class="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50">
            </div>
            
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Период подписки *</label>
                <select id="subscription-days" class="w-full px-4 py-2 border border-gray-300 rounded-lg">
                    <option value="7">7 дней (стандарт)</option>
                    <option value="14">14 дней</option>
                    <option value="30">30 дней</option>
                    <option value="90">90 дней</option>
                    <option value="180">180 дней</option>
                    <option value="365">365 дней</option>
                </select>
            </div>
            
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Сумма оплаты (руб.)</label>
                <input type="number" id="subscription-amount" 
                       class="w-full px-4 py-2 border border-gray-300 rounded-lg"
                       placeholder="500" min="0" step="100">
            </div>
            
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Примечания</label>
                <textarea id="subscription-notes" rows="3"
                          class="w-full px-4 py-2 border border-gray-300 rounded-lg"
                          placeholder="Дополнительная информация о подписке"></textarea>
            </div>
            
            <div class="pt-4 border-t border-gray-200">
                <div class="flex justify-end space-x-3">
                    <button onclick="closeAdminModal()" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                        Отмена
                    </button>
                    <button onclick="createSubscription(${userId})" class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700">
                        <i class="fas fa-crown mr-2"></i>Выдать подписку
                    </button>
                </div>
            </div>
        </div>
    `);
}

function createSubscription(userId) {
    // Логика создания подписки
    closeAdminModal();
    showAdminNotification(`Подписка выдана пользователю ${userId}`, 'success');
}

function deleteUser(userId) {
    if (confirm(`Вы уверены, что хотите удалить пользователя ${userId}?`)) {
        // Логика удаления пользователя
        showAdminNotification('Пользователь удален', 'success');
        loadUsersData();
    }
}

// Остальные функции для других разделов (подписки, рассылки, система, логи)
// будут аналогичны

function showAdminNotification(message, type = 'info') {
    const notification = document.createElement('div');
    const colors = {
        success: 'bg-green-100 border-green-500 text-green-700',
        error: 'bg-red-100 border-red-500 text-red-700',
        warning: 'bg-yellow-100 border-yellow-500 text-yellow-700',
        info: 'bg-blue-100 border-blue-500 text-blue-700'
    };
    
    notification.className = `fixed bottom-4 right-4 z-50 px-6 py-4 rounded-lg border-l-4 ${colors[type]} shadow-lg max-w-md transform translate-x-full transition-transform duration-300`;
    
    notification.innerHTML = `
        <div class="flex items-start">
            <div class="flex-shrink-0">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
            </div>
            <div class="ml-3">
                <p class="font-medium">${message}</p>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-auto text-gray-400 hover:text-gray-600">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.remove('translate-x-full');
        notification.classList.add('translate-x-0');
    }, 10);
    
    setTimeout(() => {
        notification.classList.remove('translate-x-0');
        notification.classList.add('translate-x-full');
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Делаем функции доступными глобально
window.loadAdminDashboard = loadAdminDashboard;
window.loadAdminUsers = loadAdminUsers;
window.loadAdminSubscriptions = loadAdminSubscriptions;
window.loadAdminCampaigns = loadAdminCampaigns;
window.loadAdminSystem = loadAdminSystem;
window.loadAdminLogs = loadAdminLogs;
window.showAdminNotification = showAdminNotification;