/**
 * Theme management - Dark/Light mode toggle
 */

class ThemeManager {
    constructor() {
        this.currentTheme = this.getStoredTheme() || this.getSystemTheme();
        this.applyTheme(this.currentTheme);
    }

    getSystemTheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        return 'light';
    }

    getStoredTheme() {
        return localStorage.getItem('theme');
    }

    setStoredTheme(theme) {
        localStorage.setItem('theme', theme);
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        this.currentTheme = theme;
        this.setStoredTheme(theme);
        this.updateToggleButton();
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.applyTheme(newTheme);
    }
    
    // Make toggleTheme globally available
    static getInstance() {
        if (!window._themeManagerInstance) {
            window._themeManagerInstance = new ThemeManager();
        }
        return window._themeManagerInstance;
    }

    updateToggleButton() {
        const toggleBtn = document.getElementById('theme-toggle');
        if (toggleBtn) {
            const icon = toggleBtn.querySelector('i');
            if (icon) {
                icon.className = this.currentTheme === 'dark' 
                    ? 'fas fa-sun' 
                    : 'fas fa-moon';
            }
            toggleBtn.setAttribute('aria-label', `Switch to ${this.currentTheme === 'dark' ? 'light' : 'dark'} theme`);
        }
    }

    init() {
        // Listen for system theme changes
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                if (!this.getStoredTheme()) {
                    this.applyTheme(e.matches ? 'dark' : 'light');
                }
            });
        }

        // Create toggle button - try multiple times if nav-menu not ready
        const createToggleButton = () => {
            const navMenu = document.querySelector('.nav-menu');
            if (navMenu && !document.getElementById('theme-toggle')) {
                const toggleBtn = document.createElement('button');
                toggleBtn.id = 'theme-toggle';
                toggleBtn.className = 'theme-toggle';
                toggleBtn.innerHTML = `<i class="fas fa-moon"></i>`;
                toggleBtn.setAttribute('aria-label', 'Toggle theme');
                toggleBtn.onclick = () => this.toggleTheme();
                navMenu.insertBefore(toggleBtn, navMenu.firstChild);
                this.updateToggleButton();
                return true;
            }
            return false;
        };

        // Try immediately
        if (!createToggleButton()) {
            // If not ready, try after a short delay
            setTimeout(() => {
                if (!createToggleButton()) {
                    // Last try after DOM is fully loaded
                    setTimeout(() => createToggleButton(), 500);
                }
            }, 100);
        } else {
            this.updateToggleButton();
        }
    }
}

// Initialize theme manager - make globally available
window.themeManager = new ThemeManager();
window.toggleTheme = function() {
    if (window.themeManager) {
        window.themeManager.toggleTheme();
    }
};

document.addEventListener('DOMContentLoaded', () => {
    if (window.themeManager) {
        window.themeManager.init();
    }
});

// Also try to initialize immediately (in case DOM is already loaded)
if (document.readyState === 'loading') {
    // DOM is still loading, wait for DOMContentLoaded
} else {
    // DOM is already loaded
    if (window.themeManager) {
        window.themeManager.init();
    }
}

