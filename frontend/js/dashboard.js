// Функции для личного кабинета

// Загрузка дашборда
async function loadDashboard() {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <div class="mb-8">
            <h1 class="text-2xl font-bold text-gray-800 mb-2">Мой дашборд</h1>
            <p class="text-gray-600">Обзор вашей активности и статистики</p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="bg-white rounded-xl shadow p-6">
                <div class="flex items-center">
                    <div class="bg-blue-100 p-3 rounded-lg mr-4">
                        <i class="fas fa-user text-blue-600 text-xl"></i>
                    </div>
                    <div>
                        <p class="text-gray-500 text-sm">Telegram аккаунтов</p>
                        <h3 id="accounts-count" class="text-2xl font-bold">0</h3>
                    </div>
                </div>
            </div>
            
            <div class="bg-white rounded-xl shadow p-6">
                <div class="flex items-center">
                    <div class="bg-green-100 p-3 rounded-lg mr-4">
                        <i class="fas fa-code text-green-600 text-xl"></i>
                    </div>
                    <div>
                        <p class="text-gray-500 text-sm">Сценариев</p>
                        <h3 id="scenarios-count" class="text-2xl font-bold">0</h3>
                    </div>
                </div>
            </div>
            
            <div class="bg-white rounded-xl shadow p-6">
                <div class="flex items-center">
                    <div class="bg-purple-100 p-3 rounded-lg mr-4">
                        <i class="fas fa-paper-plane text-purple-600 text-xl"></i>
                    </div>
                    <div>
                        <p class="text-gray-500 text-sm">Рассылок</p>
                        <h3 id="campaigns-count" class="text-2xl font-bold">0</h3>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <!-- Последние активности -->
            <div class="bg-white rounded-xl shadow p-6">
                <h2 class="text-lg font-bold mb-4">Последние активности</h2>
                <div id="recent-activities" class="space-y-4">
                    <div class="text-center py-4">
                        <div class="loader mx-auto mb-2"></div>
                        <p class="text-gray-500">Загрузка...</p>
                    </div>
                </div>
            </div>
            
            <!-- Быстрые действия -->
            <div class="bg-white rounded-xl shadow p-6">
                <h2 class="text-lg font-bold mb-4">Быстрые действия</h2>
                <div class="space-y-3">
                    <button onclick="loadTelegramAccounts()" class="w-full text-left p-4 border rounded-lg hover:bg-gray-50 transition">
                        <div class="flex items-center">
                            <i class="fab fa-telegram text-blue-500 text-xl mr-3"></i>
                            <div>
                                <p class="font-medium">Добавить Telegram аккаунт</p>
                                <p class="text-sm text-gray-500">Подключите новый аккаунт для рассылок</p>
                            </div>
                        </div>
                    </button>
                    
                    <button onclick="loadScenarios()" class="w-full text-left p-4 border rounded-lg hover:bg-gray-50 transition">
                        <div class="flex items-center">
                            <i class="fas fa-code text-green-500 text-xl mr-3"></i>
                            <div>
                                <p class="font-medium">Создать сценарий</p>
                                <p class="text-sm text-gray-500">Настройте последовательность сообщений</p>
                            </div>
                        </div>
                    </button>
                    
                    <button onclick="loadCampaigns()" class="w-full text-left p-4 border rounded-lg hover:bg-gray-50 transition">
                        <div class="flex items-center">
                            <i class="fas fa-paper-plane text-purple-500 text-xl mr-3"></i>
                            <div>
                                <p class="font-medium">Запустить рассылку</p>
                                <p class="text-sm text-gray-500">Отправьте сообщения в выбранную группу</p>
                            </div>
                        </div>
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Загружаем данные
    await loadDashboardData();
}

async function loadDashboardData() {
    try {
        // Заглушки - здесь должны быть реальные API запросы
        document.getElementById('accounts-count').textContent = '2';
        document.getElementById('scenarios-count').textContent = '5';
        document.getElementById('campaigns-count').textContent = '12';
        
        // Заглушка для активностей
        document.getElementById('recent-activities').innerHTML = `
            <div class="space-y-4">
                <div class="flex items-center">
                    <div class="bg-green-100 text-green-800 p-2 rounded-lg mr-3">
                        <i class="fas fa-check"></i>
                    </div>
                    <div>
                        <p class="font-medium">Рассылка успешно завершена</p>
                        <p class="text-sm text-gray-500">10 минут назад</p>
                    </div>
                </div>
                <div class="flex items-center">
                    <div class="bg-blue-100 text-blue-800 p-2 rounded-lg mr-3">
                        <i class="fas fa-plus"></i>
                    </div>
                    <div>
                        <p class="font-medium">Добавлен новый сценарий</p>
                        <p class="text-sm text-gray-500">2 часа назад</p>
                    </div>
                </div>
                <div class="flex items-center">
                    <div class="bg-yellow-100 text-yellow-800 p-2 rounded-lg mr-3">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                    <div>
                        <p class="font-medium">Недостаточно аккаунтов для рассылки</p>
                        <p class="text-sm text-gray-500">Вчера, 14:30</p>
                    </div>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Ошибка загрузки дашборда:', error);
    }
}

// Загрузка Telegram аккаунтов
async function loadTelegramAccounts() {
    const contentArea = document.getElementById('content-area');
    
    contentArea.innerHTML = `
        <div class="mb-8">
            <div class="flex justify-between items-center">
                <div>
                    <h1 class="text-2xl font-bold text-gray-800 mb-2">Telegram аккаунты</h1>
                    <p class="text-gray-600">Управление подключенными аккаунтами</p>
                </div>
                <button onclick="openAddAccountModal()" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                    <i class="fas fa-plus mr-2"></i>Добавить аккаунт
                </button>
            </div>
        </div>
        
        <div id="accounts-list" class="space-y-4">
            <div class="text-center py-12">
                <div class="loader mx-auto mb-4"></div>
                <p>Загрузка аккаунтов...</p>
            </div>
        </div>
    `;
    
    // Загружаем аккаунты
    await loadAccountsList();
}

async function loadAccountsList() {
    try {
        // Заглушка - здесь должен быть API запрос
        const accounts = [
            { id: 1, phone_number: '+79991234567', is_authenticated: true, created_at: '2024-01-15' },
            { id: 2, phone_number: '+79997654321', is_authenticated: false, created_at: '2024-01-20' }
        ];
        
        const accountsList = document.getElementById('accounts-list');
        
        if (accounts.length === 0) {
            accountsList.innerHTML = `
                <div class="text-center py-12 border-2 border-dashed border-gray-300 rounded-xl">
                    <i class="fas fa-user-plus text-4xl text-gray-400 mb-4"></i>
                    <h3 class="text-xl font-bold text-gray-600 mb-2">Нет подключенных аккаунтов</h3>
                    <p class="text-gray-500 mb-6">Добавьте свой первый Telegram аккаунт</p>
                    <button onclick="openAddAccountModal()" class="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700">
                        <i class="fas fa-plus mr-2"></i>Добавить первый аккаунт
                    </button>
                </div>
            `;
            return;
        }
        
        let html = '';
        accounts.forEach(account => {
            html += `
                <div class="bg-white rounded-xl shadow p-6">
                    <div class="flex justify-between items-start">
                        <div class="flex items-start">
                            <div class="bg-blue-100 p-3 rounded-lg mr-4">
                                <i class="fab fa-telegram text-blue-600 text-xl"></i>
                            </div>
                            <div>
                                <h3 class="font-bold text-lg">${account.phone_number}</h3>
                                <div class="flex items-center space-x-4 mt-2">
                                    <span class="inline-flex items-center">
                                        <span class="w-2 h-2 rounded-full ${account.is_authenticated ? 'bg-green-500' : 'bg-red-500'} mr-2"></span>
                                        <span class="text-sm">${account.is_authenticated ? 'Авторизован' : 'Не авторизован'}</span>
                                    </span>
                                    <span class="text-gray-500 text-sm">
                                        <i class="far fa-calendar mr-1"></i>${account.created_at}
                                    </span>
                                </div>
                            </div>
                        </div>
                        <div class="flex space-x-2">
                            ${account.is_authenticated ? 
                                '<button class="text-green-600 hover:text-green-800"><i class="fas fa-sync-alt"></i></button>' : 
                                '<button class="text-blue-600 hover:text-blue-800"><i class="fas fa-key"></i></button>'
                            }
                            <button onclick="deleteAccount(${account.id})" class="text-red-600 hover:text-red-800">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });
        
        accountsList.innerHTML = html;
        
    } catch (error) {
        document.getElementById('accounts-list').innerHTML = `
            <div class="bg-red-50 text-red-800 p-4 rounded-lg">
                <i class="fas fa-exclamation-circle mr-2"></i>
                Ошибка загрузки аккаунтов: ${error.message}
            </div>
        `;
    }
}

function openAddAccountModal() {
    openModal('Добавить Telegram аккаунт', `
        <div class="space-y-4">
            <p class="text-gray-600">Для добавления аккаунта потребуется пройти авторизацию в Telegram</p>
            
            <div class="bg-yellow-50 border-l-4 border-yellow-500 p-4">
                <div class="flex">
                    <div class="flex-shrink-0">
                        <i class="fas fa-exclamation-triangle text-yellow-500"></i>
                    </div>
                    <div class="ml-3">
                        <p class="text-sm text-yellow-700">
                            Убедитесь, что у вас есть доступ к телефону и вы можете получить SMS/звонок для подтверждения
                        </p>
                    </div>
                </div>
            </div>
            
            <div>
                <label class="block text-gray-700 text-sm font-medium mb-2">
                    Номер телефона
                </label>
                <input type="tel" id="account-phone" 
                       class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                       placeholder="+79991234567">
            </div>
            
            <div class="flex justify-end space-x-3 pt-4">
                <button onclick="closeModal()" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                    Отмена
                </button>
                <button onclick="addTelegramAccount()" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                    <i class="fas fa-plus mr-2"></i>Добавить аккаунт
                </button>
            </div>
        </div>
    `);
}

async function addTelegramAccount() {
    const phone = document.getElementById('account-phone').value.trim();
    
    if (!phone) {
        alert('Введите номер телефона');
        return;
    }
    
    // Заглушка - здесь должен быть API запрос
    closeModal();
    showNotification(`Начинаем авторизацию для ${phone}`, 'info');
    
    setTimeout(() => {
        showNotification('Проверьте Telegram для подтверждения входа', 'success');
        loadTelegramAccounts(); // Перезагружаем список
    }, 2000);
}

function deleteAccount(accountId) {
    if (confirm('Вы уверены, что хотите удалить этот аккаунт?')) {
        // Заглушка - здесь должен быть API запрос
        showNotification('Аккаунт удален', 'success');
        loadTelegramAccounts(); // Перезагружаем список
    }
}

// Остальные функции (loadScenarios, loadCampaigns, loadStats, loadSettings)
// будут аналогичны - создам их по запросу

// Вспомогательная функция для уведомлений
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed bottom-4 right-4 z-50 px-6 py-4 rounded-lg border-l-4 shadow-lg max-w-md transform translate-x-full transition-transform duration-300 ${
        type === 'success' ? 'bg-green-100 border-green-500 text-green-700' :
        type === 'error' ? 'bg-red-100 border-red-500 text-red-700' :
        'bg-blue-100 border-blue-500 text-blue-700'
    }`;
    
    notification.innerHTML = `
        <div class="flex items-start">
            <div class="flex-shrink-0">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
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
window.loadDashboard = loadDashboard;
window.loadTelegramAccounts = loadTelegramAccounts;
window.loadScenarios = loadScenarios;
window.loadCampaigns = loadCampaigns;
window.loadStats = loadStats;
window.loadSettings = loadSettings;
window.showNotification = showNotification;