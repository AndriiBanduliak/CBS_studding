/**
 * Keyboard shortcuts for improved UX
 */

class KeyboardShortcuts {
    constructor() {
        this.shortcuts = new Map();
        this.init();
    }

    register(key, handler, description) {
        this.shortcuts.set(key, { handler, description });
    }

    init() {
        document.addEventListener('keydown', (e) => {
            // Ignore if typing in input/textarea
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                // Allow Escape to close modals even when in input
                if (e.key === 'Escape') {
                    this.handleEscape();
                }
                return;
            }

            // Check for shortcuts
            const key = this.getKeyString(e);
            const shortcut = this.shortcuts.get(key);
            if (shortcut) {
                e.preventDefault();
                shortcut.handler();
            }
        });

        // Register default shortcuts
        this.registerDefaultShortcuts();
    }

    getKeyString(e) {
        const parts = [];
        if (e.ctrlKey || e.metaKey) parts.push('Ctrl');
        if (e.shiftKey) parts.push('Shift');
        if (e.altKey) parts.push('Alt');
        parts.push(e.key);
        return parts.join('+');
    }

    registerDefaultShortcuts() {
        // Escape - Close modal
        this.register('Escape', () => {
            const openModal = document.querySelector('.modal[style*="block"]');
            if (openModal) {
                openModal.style.display = 'none';
            }
        }, 'Close modal');

        // Ctrl/Cmd + K - Open chat
        this.register('Ctrl+k', () => {
            if (typeof openChat === 'function') {
                openChat();
            }
        }, 'Open chat');

        // Ctrl/Cmd + M - Open ASR
        this.register('Ctrl+m', () => {
            if (typeof openASR === 'function') {
                openASR();
            }
        }, 'Open speech recognition');

        // Ctrl/Cmd + T - Open TTS
        this.register('Ctrl+t', () => {
            if (typeof openTTS === 'function') {
                openTTS();
            }
        }, 'Open text-to-speech');

        // Ctrl/Cmd + / - Show shortcuts help
        this.register('Ctrl+/', () => {
            this.showShortcutsHelp();
        }, 'Show keyboard shortcuts');
    }

    handleEscape() {
        const openModal = document.querySelector('.modal[style*="block"]');
        if (openModal) {
            const modalId = openModal.id;
            if (typeof closeModal === 'function') {
                closeModal(modalId);
            } else {
                openModal.style.display = 'none';
            }
        }
    }

    showShortcutsHelp() {
        const shortcutsList = Array.from(this.shortcuts.entries())
            .map(([key, { description }]) => `<tr><td><kbd>${key}</kbd></td><td>${description}</td></tr>`)
            .join('');

        const helpHTML = `
            <div class="modal" id="shortcuts-help-modal" style="display: block;">
                <div class="modal-content">
                    <span class="close" onclick="closeModal('shortcuts-help-modal')">&times;</span>
                    <h2>Keyboard Shortcuts</h2>
                    <table style="width: 100%; margin-top: 1rem;">
                        <thead>
                            <tr>
                                <th style="text-align: left; padding: 0.5rem;">Shortcut</th>
                                <th style="text-align: left; padding: 0.5rem;">Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${shortcutsList}
                        </tbody>
                    </table>
                    <kbd style="background: var(--bg-secondary); padding: 0.25rem 0.5rem; border-radius: 4px; font-family: monospace; border: 1px solid var(--border-color);">
                        Ctrl
                    </kbd> = 
                    <span style="color: var(--text-secondary);">Ctrl on Windows/Linux, Cmd on Mac</span>
                </div>
            </div>
        `;

        // Remove existing help modal if any
        const existing = document.getElementById('shortcuts-help-modal');
        if (existing) {
            existing.remove();
        }

        document.body.insertAdjacentHTML('beforeend', helpHTML);
    }
}

// Initialize keyboard shortcuts
const keyboardShortcuts = new KeyboardShortcuts();

