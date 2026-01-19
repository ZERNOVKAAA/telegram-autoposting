class TelegramAutoPostingAPI {
    constructor() {
        // Адрес вашего API сервера
        this.baseURL = window.location.hostname === 'localhost' 
            ? 'http://localhost:5000' 
            : window.location.origin; // Для Railway
        
        this.token = localStorage.getItem('auth_token');
        this.user = JSON.parse(localStorage.getItem('user_data') || 'null');
    }

    // Общий метод для запросов
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        // Добавляем токен, если есть
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        const config = {
            ...options,
            headers
        };
        
        try {
            const response = await fetch(url, config);
            
            // Обработка 401 (неавторизован)
            if (response.status === 401) {
                this.logout();
                window.location.href = '/login.html';
                return null;
            }
            
            // Обработка ошибок
            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new Error(error.message || `HTTP ${response.status}`);
            }
            
            return await response.json();
            
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Аутентификация
    async login(username, password) {
        const data = await this.request('/api/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
        
        if (data && data.token) {
            this.token = data.token;
            this.user = data.user;
            
            localStorage.setItem('auth_token', data.token);
            localStorage.setItem('user_data', JSON.stringify(data.user));
            
            // Сохраняем подписку
            if (data.subscription) {
                localStorage.setItem('subscription', JSON.stringify(data.subscription));
            }
        }
        
        return data;
    }

    async register(username, password, email = '', telegram = '') {
        return await this.request('/api/auth/register', {
            method: 'POST',
            body: JSON.stringify({ 
                username, 
                password, 
                email, 
                telegram_contact: telegram 
            })
        });
    }

    // Система
    async getSystemStatus() {
        return await this.request('/status');
    }

    async getHealth() {
        return await this.request('/health');
    }

    // Пользователи (админ)
    async getUsers() {
        return await this.request('/api/users');
    }

    async createUser(username, phone) {
        return await this.request('/api/users', {
            method: 'POST',
            body: JSON.stringify({ username, phone })
        });
    }

    // Рассылки
    async getCampaigns() {
        return await this.request('/api/campaigns');
    }

    async createCampaign(name, message) {
        return await this.request('/api/campaigns', {
            method: 'POST',
            body: JSON.stringify({ name, message })
        });
    }

    // Подписка
    async checkSubscription() {
        return await this.request('/api/subscription/check');
    }

    // Статистика (админ)
    async getAdminStats() {
        return await this.request('/api/admin/stats');
    }

    // Выход
    logout() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_data');
        localStorage.removeItem('subscription');
    }

    // Проверка авторизации
    isAuthenticated() {
        return !!this.token && !!this.user;
    }

    // Проверка админки
    isAdmin() {
        return this.isAuthenticated() && this.user.is_admin === true;
    }
}

// Создаем глобальный экземпляр
window.api = new TelegramAutoPostingAPI();