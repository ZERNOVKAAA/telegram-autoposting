// Инициализация приложения
async function initApp() {
    // Показываем кнопки навигации
    updateNavigation();
    
    // Проверяем статус системы
    checkSystemStatus();
    
    // Проверяем авторизацию
    checkAuth();
}

// Обновление навигации
function updateNavigation() {
    const navButtons = document.getElementById('nav-buttons');
    
    if (!navButtons) return;
    
    if (api.isAuthenticated()) {
        const userName = api.user.username;
        const isAdmin = api.isAdmin();
        
        navButtons.innerHTML = `
            <div class="flex items-center space-x-4">
                <span class="text-gray-700">
                    <i class="fas fa-user mr-1"></i>${userName}
                </span>
                ${isAdmin ? 
                    '<span class="bg-red-100 text-red-800 text-xs px-2 py-1 rounded">Админ</span>' : 
                    ''
                }
                <a href="/dashboard.html" class="text-blue-600 hover:text-blue-800 font-medium">
                    <i class="fas fa-tachometer-alt mr-1"></i>Личный кабинет
                </a>
                ${isAdmin ? 
                    '<a href="/admin.html" class="text-purple-600 hover:text-purple-800 font-medium">' +
                    '<i class="fas fa-cogs mr-1"></i>Админка</a>' : 
                    ''
                }
                <button onclick="logout()" class="text-gray-600 hover:text-gray-800 font-medium">
                    <i class="fas fa-sign-out-alt mr-1"></i>Выйти
                </button>
            </div>
        `;
    } else {
        navButtons.innerHTML = `
            <div class="flex space-x-4">
                <a href="/login.html" class="text-blue-600 hover:text-blue-800 font-medium">
                    <i class="fas fa-sign-in-alt mr-1"></i>Войти
                </a>
                <a href="/login.html?register=true" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 font-medium">
                    <i class="fas fa-user-plus mr-1"></i>Регистрация
                </a>
            </div>
        `;
    }
}

// Проверка статуса системы
async function checkSystemStatus() {
    const statusContainer = document.getElementById('system-status');
    
    if (!statusContainer) return;
    
    try {
        const status = await api.getSystemStatus();
        
        if (status) {
            statusContainer.innerHTML = `
                <div class="text-center p-4 border-r">
                    <div class="text-green-500 text-3xl mb-2">
                        <i class="fas fa-server"></i>
                    </div>
                    <h3 class="font-bold">API Сервер</h3>
                    <p class="text-green-600 font-semibold">✅ Работает</p>
                    <p class="text-sm text-gray-500 mt-1">Порт: ${status.server?.port || 5000}</p>
                </div>
                <div class="text-center p-4 border-r">
                    <div class="text-blue-500 text-3xl mb-2">
                        <i class="fas fa-database"></i>
                    </div>
                    <h3 class="font-bold">База данных</h3>
                    <p class="${status.database?.connection === 'established' ? 'text-green-600' : 'text-red-600'} font-semibold">
                        ${status.database?.connection === 'established' ? '✅ Подключена' : '❌ Ошибка'}
                    </p>
                    <p class="text-sm text-gray-500 mt-1">
                        Пользователей: ${status.database?.users || 0}
                    </p>
                </div>
                <div class="text-center p-4">
                    <div class="text-purple-500 text-3xl mb-2">
                        <i class="fas fa-code"></i>
                    </div>
                    <h3 class="font-bold">Версия</h3>
                    <p class="text-gray-700">${status.version || '1.0.0'}</p>
                    <p class="text-sm text-gray-500 mt-1">
                        ${status.environment || 'production'}
                    </p>
                </div>
            `;
        }
    } catch (error) {
        statusContainer.innerHTML = `
            <div class="col-span-3 text-center p-4">
                <div class="text-red-500 text-3xl mb-2">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <h3 class="font-bold">Ошибка подключения</h3>
                <p class="text-red-600">Не удалось подключиться к серверу</p>
                <p class="text-sm text-gray-500 mt-1">Проверьте, запущен ли API сервер</p>
            </div>
        `;
    }
}

// Проверка авторизации
function checkAuth() {
    if (!api.isAuthenticated()) {
        // Если не на главной странице и не на логине - редирект
        const currentPage = window.location.pathname;
        if (!currentPage.includes('index.html') && !currentPage.includes('login.html') && currentPage !== '/') {
            window.location.href = '/index.html';
        }
    } else {
        // Если на логине, но уже авторизован - на дашборд
        if (window.location.pathname.includes('login.html')) {
            window.location.href = api.isAdmin() ? '/admin.html' : '/dashboard.html';
        }
    }
}

// Выход из системы
function logout() {
    if (confirm('Вы уверены, что хотите выйти?')) {
        api.logout();
        window.location.href = '/index.html';
    }
}

// Показ уведомлений
function showNotification(message, type = 'info') {
    const colors = {
        success: 'bg-green-100 border-green-500 text-green-700',
        error: 'bg-red-100 border-red-500 text-red-700',
        warning: 'bg-yellow-100 border-yellow-500 text-yellow-700',
        info: 'bg-blue-100 border-blue-500 text-blue-700'
    };
    
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 px-6 py-4 rounded-lg border-l-4 ${colors[type]} shadow-lg max-w-md transform translate-x-full transition-transform duration-300`;
    notification.innerHTML = `
        <div class="flex items-start">
            <div class="flex-shrink-0">
                ${type === 'success' ? '<i class="fas fa-check-circle text-green-500"></i>' : ''}
                ${type === 'error' ? '<i class="fas fa-exclamation-circle text-red-500"></i>' : ''}
                ${type === 'warning' ? '<i class="fas fa-exclamation-triangle text-yellow-500"></i>' : ''}
                ${type === 'info' ? '<i class="fas fa-info-circle text-blue-500"></i>' : ''}
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
    
    // Показываем
    setTimeout(() => {
        notification.classList.remove('translate-x-full');
        notification.classList.add('translate-x-0');
    }, 10);
    
    // Убираем через 5 секунд
    setTimeout(() => {
        notification.classList.remove('translate-x-0');
        notification.classList.add('translate-x-full');
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Загрузчик
function showLoader(show = true) {
    let loader = document.getElementById('global-loader');
    
    if (show && !loader) {
        loader = document.createElement('div');
        loader.id = 'global-loader';
        loader.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        loader.innerHTML = '<div class="loader"></div>';
        document.body.appendChild(loader);
    } else if (!show && loader) {
        loader.remove();
    }
}

// Экспортируем функции
window.showNotification = showNotification;
window.showLoader = showLoader;
window.logout = logout;
window.initApp = initApp;