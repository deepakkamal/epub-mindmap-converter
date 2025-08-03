/* ========================================
   DARK MODE TOGGLE FUNCTIONALITY
   Based on Material Design principles and best practices
   ======================================== */

(function() {
    'use strict';

    // Configuration
    const STORAGE_KEY = 'mindmap-theme-preference';
    const THEME_ATTRIBUTE = 'data-theme';
    const LIGHT_THEME = 'light';
    const DARK_THEME = 'dark';

    // DOM elements
    let toggleButton = null;
    let moonIcon = null;
    let sunIcon = null;

    // Helper functions
    function getStoredTheme() {
        try {
            return localStorage.getItem(STORAGE_KEY);
        } catch (e) {
            console.warn('localStorage not available for theme persistence');
            return null;
        }
    }

    function setStoredTheme(theme) {
        try {
            localStorage.setItem(STORAGE_KEY, theme);
        } catch (e) {
            console.warn('Could not save theme preference to localStorage');
        }
    }

    function getSystemPreference() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return DARK_THEME;
        }
        return LIGHT_THEME;
    }

    function getCurrentTheme() {
        const stored = getStoredTheme();
        if (stored) {
            return stored;
        }
        return getSystemPreference();
    }

    function applyTheme(theme) {
        document.documentElement.setAttribute(THEME_ATTRIBUTE, theme);
        updateToggleButton(theme);
        console.log(`Applied ${theme} theme`);
    }

    function updateToggleButton(theme) {
        if (!toggleButton) return;
        
        const isDark = theme === DARK_THEME;
        const buttonText = toggleButton.querySelector('.toggle-text');
        
        if (buttonText) {
            buttonText.textContent = isDark ? 'Light Mode' : 'Dark Mode';
        }
    }

    function toggleTheme() {
        const currentTheme = document.documentElement.getAttribute(THEME_ATTRIBUTE);
        const newTheme = currentTheme === DARK_THEME ? LIGHT_THEME : DARK_THEME;
        
        applyTheme(newTheme);
        setStoredTheme(newTheme);
        
        // Announce theme change for accessibility
        announceThemeChange(newTheme);
    }

    function announceThemeChange(theme) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.style.position = 'absolute';
        announcement.style.left = '-10000px';
        announcement.style.width = '1px';
        announcement.style.height = '1px';
        announcement.style.overflow = 'hidden';
        announcement.textContent = `Switched to ${theme} mode`;
        
        document.body.appendChild(announcement);
        
        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }

    function createToggleButton() {
        const button = document.createElement('button');
        button.className = 'dark-mode-toggle';
        button.setAttribute('aria-label', 'Toggle dark mode');
        button.setAttribute('title', 'Toggle between light and dark mode');
        
        button.innerHTML = `
            <svg class="icon moon-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" />
            </svg>
            <svg class="icon sun-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 7a5 5 0 100 10 5 5 0 000-10zM2 13h2a1 1 0 100-2H2a1 1 0 100 2zm18 0h2a1 1 0 100-2h-2a1 1 0 100 2zM11 2v2a1 1 0 102 0V2a1 1 0 10-2 0zm0 18v2a1 1 0 102 0v-2a1 1 0 10-2 0zM5.99 4.58a1 1 0 10-1.41 1.41l1.06 1.06a1 1 0 101.41-1.41L5.99 4.58zm12.37 12.37a1 1 0 10-1.41 1.41l1.06 1.06a1 1 0 101.41-1.41l-1.06-1.06zm1.06-10.96a1 1 0 10-1.41-1.41l-1.06 1.06a1 1 0 101.41 1.41l1.06-1.06zM7.05 18.36a1 1 0 10-1.41-1.41l-1.06 1.06a1 1 0 101.41 1.41l1.06-1.06z"/>
            </svg>
            <span class="toggle-text">Dark Mode</span>
        `;
        
        button.addEventListener('click', toggleTheme);
        
        return button;
    }

    function addToggleButton() {
        // Remove existing toggle if it exists
        const existingToggle = document.querySelector('.dark-mode-toggle');
        if (existingToggle) {
            existingToggle.remove();
        }

        toggleButton = createToggleButton();
        document.body.appendChild(toggleButton);
        
        // Update button text based on current theme
        const currentTheme = getCurrentTheme();
        updateToggleButton(currentTheme);
    }

    function initializeTheme() {
        // Apply theme immediately to prevent flash
        const theme = getCurrentTheme();
        applyTheme(theme);
        
        // Add toggle button when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', addToggleButton);
        } else {
            addToggleButton();
        }
    }

    // Listen for system theme changes
    function setupSystemThemeListener() {
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            
            const handleSystemThemeChange = (e) => {
                // Only apply system theme if user hasn't manually set a preference
                if (!getStoredTheme()) {
                    const newTheme = e.matches ? DARK_THEME : LIGHT_THEME;
                    applyTheme(newTheme);
                }
            };

            // Modern browsers
            if (mediaQuery.addEventListener) {
                mediaQuery.addEventListener('change', handleSystemThemeChange);
            } 
            // Legacy browsers
            else if (mediaQuery.addListener) {
                mediaQuery.addListener(handleSystemThemeChange);
            }
        }
    }

    // Keyboard shortcuts
    function setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Shift + L to toggle theme
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'L') {
                e.preventDefault();
                toggleTheme();
            }
        });
    }

    // Public API
    window.DarkMode = {
        toggle: toggleTheme,
        setTheme: function(theme) {
            if (theme === LIGHT_THEME || theme === DARK_THEME) {
                applyTheme(theme);
                setStoredTheme(theme);
            }
        },
        getCurrentTheme: function() {
            return document.documentElement.getAttribute(THEME_ATTRIBUTE);
        },
        resetToSystem: function() {
            try {
                localStorage.removeItem(STORAGE_KEY);
            } catch (e) {
                console.warn('Could not clear theme preference');
            }
            const systemTheme = getSystemPreference();
            applyTheme(systemTheme);
        }
    };

    // Initialize everything
    initializeTheme();
    setupSystemThemeListener();
    setupKeyboardShortcuts();

    // Debug info in console
    console.log('🌓 Dark Mode initialized successfully');
    console.log(`Current theme: ${getCurrentTheme()}`);
    console.log('Keyboard shortcut: Ctrl/Cmd + Shift + L');

})();