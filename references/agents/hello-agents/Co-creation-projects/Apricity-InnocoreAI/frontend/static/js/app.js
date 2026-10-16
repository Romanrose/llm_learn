// 研创·智核 - 主应用JavaScript

class InnoCoreApp {
    constructor() {
        this.api = new API();
        this.router = new Router();
        this.state = new StateManager();
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupRouter();
        this.checkAuth();
    }

    setupEventListeners() {
        // 全局事件监听
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action]')) {
                this.handleAction(e.target.dataset.action, e.target);
            }
        });

        // 表单提交
        document.addEventListener('submit', (e) => {
            if (e.target.matches('.ajax-form')) {
                e.preventDefault();
                this.handleFormSubmit(e.target);
            }
        });

        // 模态框关闭
        document.addEventListener('click', (e) => {
            if (e.target.matches('.modal') || e.target.matches('.modal-close')) {
                this.closeModal(e.target.closest('.modal'));
            }
        });
    }

    setupRouter() {
        // 路由配置
        this.router.addRoute('/', () => this.showDashboard());
        this.router.addRoute('/papers', () => this.showPapers());
        this.router.addRoute('/papers/new', () => this.showNewPaper());
        this.router.addRoute('/papers/:id', (params) => this.showPaperDetail(params.id));
        this.router.addRoute('/tasks', () => this.showTasks());
        this.router.addRoute('/tasks/:id', (params) => this.showTaskDetail(params.id));
        this.router.addRoute('/analysis', () => this.showAnalysis());
        this.router.addRoute('/writing', () => this.showWriting());
        this.router.addRoute('/profile', () => this.showProfile());
    }

    async checkAuth() {
        const token = localStorage.getItem('token');
        if (token) {
            try {
                const user = await this.api.get('/auth/me');
                this.state.setUser(user);
                this.updateUI();
            } catch (error) {
                localStorage.removeItem('token');
                this.showLogin();
            }
        } else {
            this.showLogin();
        }
    }

    updateUI() {
        const user = this.state.getUser();
        if (user) {
            document.querySelector('.user-name').textContent = user.username;
            document.querySelector('.user-email').textContent = user.email;
        }
    }

    // 页面显示方法
    async showDashboard() {
        const content = document.getElementById('content');
        content.innerHTML = await this.loadTemplate('dashboard');
        
        // 加载统计数据
        const stats = await this.api.get('/dashboard/stats');
        this.renderDashboardStats(stats);
        
        // 加载最近任务
        const tasks = await this.api.get('/tasks?limit=5');
        this.renderRecentTasks(tasks);
    }

    async showPapers() {
        const content = document.getElementById('content');
        content.innerHTML = await this.loadTemplate('papers');
        
        // 加载论文列表
        const papers = await this.api.get('/papers');
        this.renderPapersList(papers);
    }

    async showNewPaper() {
        const content = document.getElementById('content');
        content.innerHTML = await this.loadTemplate('new-paper');
        
        // 初始化表单
        this.initPaperForm();
    }

    async showPaperDetail(paperId) {
        const content = document.getElementById('content');
        content.innerHTML = await this.loadTemplate('paper-detail');
        
        // 加载论文详情
        const paper = await this.api.get(`/papers/${paperId}`);
        this.renderPaperDetail(paper);
    }

    async showTasks() {
        const content = document.getElementById('content');
        content.innerHTML = await this.loadTemplate('tasks');
        
        // 加载任务列表
        const tasks = await this.api.get('/tasks');
        this.renderTasksList(tasks);
    }

    async showTaskDetail(taskId) {
        const content = document.getElementById('content');
        content.innerHTML = await this.loadTemplate('task-detail');
        
        // 加载任务详情
        const task = await this.api.get(`/tasks/${taskId}`);
        this.renderTaskDetail(task);
        
        // 如果任务正在运行，开始轮询状态
        if (task.status === 'running') {
            this.startTaskPolling(taskId);
        }
    }

    async showAnalysis() {
        const content = document.getElementById('content');
        content.innerHTML = await this.loadTemplate('analysis');
        
        // 加载分析列表
        const analyses = await this.api.get('/analysis');
        this.renderAnalysisList(analyses);
    }

    async showWriting() {
        const content = document.getElementById('content');
        content.innerHTML = await this.loadTemplate('writing');
        
        // 加载写作列表
        const writings = await this.api.get('/writing');
        this.renderWritingList(writings);
    }

    async showProfile() {
        const content = document.getElementById('content');
        content.innerHTML = await this.loadTemplate('profile');
        
        // 加载用户信息
        const user = await this.api.get('/auth/me');
        this.renderProfile(user);
    }

    async showLogin() {
        const content = document.getElementById('content');
        content.innerHTML = await this.loadTemplate('login');
        
        // 初始化登录表单
        this.initLoginForm();
    }

    // 事件处理方法
    async handleAction(action, element) {
        switch (action) {
            case 'logout':
                await this.logout();
                break;
            case 'delete-paper':
                await this.deletePaper(element.dataset.id);
                break;
            case 'delete-task':
                await this.deleteTask(element.dataset.id);
                break;
            case 'cancel-task':
                await this.cancelTask(element.dataset.id);
                break;
            case 'retry-task':
                await this.retryTask(element.dataset.id);
                break;
            case 'export-paper':
                await this.exportPaper(element.dataset.id, element.dataset.format);
                break;
            case 'show-modal':
                this.showModal(element.dataset.target);
                break;
            case 'close-modal':
                this.closeModal(element.closest('.modal'));
                break;
        }
    }

    async handleFormSubmit(form) {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        try {
            this.showLoading(form);
            
            const endpoint = form.dataset.endpoint;
            const method = form.dataset.method || 'POST';
            
            let result;
            if (method === 'POST') {
                result = await this.api.post(endpoint, data);
            } else if (method === 'PUT') {
                result = await this.api.put(endpoint, data);
            }
            
            this.showSuccess('操作成功！');
            
            // 根据结果跳转
            if (form.dataset.redirect) {
                this.router.navigate(form.dataset.redirect);
            } else if (result.id) {
                this.router.navigate(`/${form.dataset.resource}/${result.id}`);
            }
            
        } catch (error) {
            this.showError(error.message);
        } finally {
            this.hideLoading(form);
        }
    }

    // API调用方法
    async createLiteratureSearchTask(query, options = {}) {
        const data = {
            title: `文献搜索: ${query}`,
            task_type: 'literature_search',
            parameters: {
                query,
                max_papers: options.maxPapers || 20,
                year_range: options.yearRange,
                venues: options.venues || []
            }
        };
        
        const task = await this.api.post('/tasks', data);
        this.router.navigate(`/tasks/${task.id}`);
        return task;
    }

    async createAnalysisTask(paperIds, analysisType) {
        const data = {
            title: `论文分析: ${analysisType}`,
            task_type: 'analysis',
            parameters: {
                paper_ids: paperIds,
                analysis_type: analysisType
            }
        };
        
        const task = await this.api.post('/tasks', data);
        this.router.navigate(`/tasks/${task.id}`);
        return task;
    }

    async createWritingTask(paperIds, writingType, outline) {
        const data = {
            title: `学术写作: ${writingType}`,
            task_type: 'writing',
            parameters: {
                paper_ids: paperIds,
                writing_type: writingType,
                outline: outline
            }
        };
        
        const task = await this.api.post('/tasks', data);
        this.router.navigate(`/tasks/${task.id}`);
        return task;
    }

    // 渲染方法
    renderDashboardStats(stats) {
        const container = document.getElementById('stats-container');
        container.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>${stats.total_papers}</h3>
                    <p>论文总数</p>
                </div>
                <div class="stat-card">
                    <h3>${stats.total_tasks}</h3>
                    <p>任务总数</p>
                </div>
                <div class="stat-card">
                    <h3>${stats.total_analyses}</h3>
                    <p>分析报告</p>
                </div>
                <div class="stat-card">
                    <h3>${stats.total_writings}</h3>
                    <p>写作文档</p>
                </div>
            </div>
        `;
    }

    renderPapersList(papers) {
        const container = document.getElementById('papers-list');
        container.innerHTML = papers.map(paper => `
            <div class="paper-card" data-id="${paper.id}">
                <h3>${paper.title}</h3>
                <p class="authors">${paper.authors.join(', ')}</p>
                <p class="abstract">${paper.abstract || '暂无摘要'}</p>
                <div class="paper-meta">
                    <span class="badge badge-primary">${paper.publication_year || '未知年份'}</span>
                    <span class="badge badge-secondary">${paper.journal || '未知期刊'}</span>
                </div>
                <div class="paper-actions">
                    <button class="btn btn-sm btn-primary" data-action="view-paper" data-id="${paper.id}">查看</button>
                    <button class="btn btn-sm btn-outline" data-action="export-paper" data-id="${paper.id}">导出</button>
                    <button class="btn btn-sm btn-danger" data-action="delete-paper" data-id="${paper.id}">删除</button>
                </div>
            </div>
        `).join('');
    }

    renderTasksList(tasks) {
        const container = document.getElementById('tasks-list');
        container.innerHTML = tasks.map(task => `
            <div class="task-card" data-id="${task.id}">
                <h3>${task.title}</h3>
                <p class="task-description">${task.description || '暂无描述'}</p>
                <div class="task-meta">
                    <span class="badge badge-${this.getStatusClass(task.status)}">${this.getStatusText(task.status)}</span>
                    <span class="task-type">${this.getTaskTypeText(task.task_type)}</span>
                </div>
                <div class="task-progress">
                    <div class="progress">
                        <div class="progress-bar" style="width: ${task.progress}%"></div>
                    </div>
                    <span class="progress-text">${task.progress}%</span>
                </div>
                <div class="task-actions">
                    <button class="btn btn-sm btn-primary" data-action="view-task" data-id="${task.id}">查看</button>
                    ${task.status === 'running' ? `<button class="btn btn-sm btn-warning" data-action="cancel-task" data-id="${task.id}">取消</button>` : ''}
                    ${task.status === 'failed' ? `<button class="btn btn-sm btn-secondary" data-action="retry-task" data-id="${task.id}">重试</button>` : ''}
                </div>
            </div>
        `).join('');
    }

    // 工具方法
    getStatusClass(status) {
        const classes = {
            'pending': 'warning',
            'running': 'primary',
            'completed': 'success',
            'failed': 'danger'
        };
        return classes[status] || 'secondary';
    }

    getStatusText(status) {
        const texts = {
            'pending': '等待中',
            'running': '运行中',
            'completed': '已完成',
            'failed': '失败'
        };
        return texts[status] || status;
    }

    getTaskTypeText(type) {
        const texts = {
            'literature_search': '文献搜索',
            'analysis': '论文分析',
            'writing': '学术写作'
        };
        return texts[type] || type;
    }

    async loadTemplate(templateName) {
        try {
            const response = await fetch(`/templates/${templateName}.html`);
            return await response.text();
        } catch (error) {
            console.error('Failed to load template:', error);
            return '<div>模板加载失败</div>';
        }
    }

    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('show');
        }
    }

    closeModal(modal) {
        if (modal) {
            modal.classList.remove('show');
        }
    }

    showLoading(element) {
        element.disabled = true;
        element.innerHTML = '<span class="spinner"></span> 处理中...';
    }

    hideLoading(element) {
        element.disabled = false;
        element.innerHTML = element.dataset.originalText || element.textContent;
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    startTaskPolling(taskId) {
        const poll = async () => {
            try {
                const task = await this.api.get(`/tasks/${taskId}`);
                this.updateTaskStatus(task);
                
                if (task.status === 'completed' || task.status === 'failed') {
                    clearInterval(this.pollingInterval);
                }
            } catch (error) {
                console.error('Task polling error:', error);
            }
        };
        
        this.pollingInterval = setInterval(poll, 2000);
    }

    updateTaskStatus(task) {
        const progressBar = document.querySelector('.progress-bar');
        const progressText = document.querySelector('.progress-text');
        const statusBadge = document.querySelector('.task-meta .badge');
        
        if (progressBar) progressBar.style.width = `${task.progress}%`;
        if (progressText) progressText.textContent = `${task.progress}%`;
        if (statusBadge) {
            statusBadge.className = `badge badge-${this.getStatusClass(task.status)}`;
            statusBadge.textContent = this.getStatusText(task.status);
        }
    }

    async logout() {
        localStorage.removeItem('token');
        this.state.clearUser();
        this.router.navigate('/login');
    }
}

// API类
class API {
    constructor() {
        this.baseURL = '/api/v1';
    }

    async request(endpoint, options = {}) {
        const token = localStorage.getItem('token');
        const url = `${this.baseURL}${endpoint}`;
        
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...(token && { 'Authorization': `Bearer ${token}` }),
                ...options.headers
            },
            ...options
        };

        const response = await fetch(url, config);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || '请求失败');
        }

        return await response.json();
    }

    get(endpoint) {
        return this.request(endpoint);
    }

    post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE'
        });
    }
}

// 路由类
class Router {
    constructor() {
        this.routes = new Map();
        this.currentPath = window.location.pathname;
        
        window.addEventListener('popstate', () => {
            this.handleRoute();
        });
    }

    addRoute(path, handler) {
        this.routes.set(path, handler);
    }

    navigate(path) {
        window.history.pushState({}, '', path);
        this.currentPath = path;
        this.handleRoute();
    }

    handleRoute() {
        const path = window.location.pathname;
        
        for (const [route, handler] of this.routes) {
            if (this.matchRoute(route, path)) {
                const params = this.extractParams(route, path);
                handler(params);
                return;
            }
        }
        
        // 404处理
        this.show404();
    }

    matchRoute(route, path) {
        const routeParts = route.split('/');
        const pathParts = path.split('/');
        
        if (routeParts.length !== pathParts.length) {
            return false;
        }

        return routeParts.every((part, index) => {
            return part.startsWith(':') || part === pathParts[index];
        });
    }

    extractParams(route, path) {
        const routeParts = route.split('/');
        const pathParts = path.split('/');
        const params = {};

        routeParts.forEach((part, index) => {
            if (part.startsWith(':')) {
                const paramName = part.substring(1);
                params[paramName] = pathParts[index];
            }
        });

        return params;
    }

    show404() {
        document.getElementById('content').innerHTML = '<h1>页面未找到</h1>';
    }
}

// 状态管理类
class StateManager {
    constructor() {
        this.state = {
            user: null,
            currentTask: null,
            notifications: []
        };
    }

    setUser(user) {
        this.state.user = user;
    }

    getUser() {
        return this.state.user;
    }

    clearUser() {
        this.state.user = null;
    }

    setCurrentTask(task) {
        this.state.currentTask = task;
    }

    getCurrentTask() {
        return this.state.currentTask;
    }

    addNotification(notification) {
        this.state.notifications.push(notification);
    }

    getNotifications() {
        return this.state.notifications;
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.app = new InnoCoreApp();
});