/**
 * Error handling utilities for frontend
 */

class ErrorHandler {
    constructor() {
        this.retryAttempts = 3;
        this.retryDelay = 1000; // 1 second
    }

    /**
     * Handle API errors with retry mechanism
     */
    async handleRequest(requestFn, retries = this.retryAttempts) {
        for (let i = 0; i < retries; i++) {
            try {
                return await requestFn();
            } catch (error) {
                if (i === retries - 1) {
                    // Last attempt failed
                    this.showError(error);
                    throw error;
                }
                
                // Wait before retry
                await this.delay(this.retryDelay * (i + 1));
            }
        }
    }

    /**
     * Show user-friendly error message
     */
    showError(error) {
        let message = 'An error occurred. Please try again.';
        
        if (error.response) {
            // Server responded with error
            const status = error.response.status;
            const data = error.response.data;
            
            switch (status) {
                case 400:
                    message = data.error || data.message || 'Invalid request. Please check your input.';
                    break;
                case 500:
                    // Check if it's an Ollama connection error
                    if (data.error && (data.error.includes('Ollama') || data.error.includes('подключиться'))) {
                        message = data.error + '\n\nУбедитесь, что Ollama запущен:\n1. Откройте терминал\n2. Выполните: ollama serve\n3. Обновите страницу';
                    } else {
                        message = data.error || data.message || 'Server error. Please try again later.';
                    }
                    break;
                case 401:
                    message = 'Authentication required. Please login.';
                    setTimeout(() => {
                        window.location.href = '/api/auth/login/';
                    }, 2000);
                    break;
                case 403:
                    message = 'You do not have permission to perform this action.';
                    break;
                case 404:
                    message = 'Resource not found.';
                    break;
                case 429:
                    message = 'Too many requests. Please wait a moment and try again.';
                    break;
                case 500:
                    message = 'Server error. Please try again later.';
                    break;
                case 503:
                    message = 'Service temporarily unavailable. Please try again later.';
                    break;
                default:
                    message = data.error || data.message || `Error ${status}: ${error.message}`;
            }
        } else if (error.request) {
            // Request was made but no response received
            message = 'Network error. Please check your connection and try again.';
        } else {
            // Something else happened
            message = error.message || 'An unexpected error occurred.';
        }
        
        showNotification(message, 'error');
        console.error('Error details:', error);
    }

    /**
     * Delay helper for retries
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Validate file before upload
     */
    validateFile(file, options = {}) {
        const {
            maxSize = 10 * 1024 * 1024, // 10 MB default
            allowedTypes = ['audio/wav', 'audio/mpeg', 'audio/flac', 'audio/ogg', 'audio/webm', 'audio/mp4'],
            allowedExtensions = ['.wav', '.mp3', '.flac', '.ogg', '.webm', '.m4a']
        } = options;

        // Check file size
        if (file.size > maxSize) {
            throw new Error(`File too large. Maximum size: ${(maxSize / (1024 * 1024)).toFixed(0)} MB`);
        }

        // Check file type
        if (!allowedTypes.includes(file.type)) {
            throw new Error(`Unsupported file type. Allowed: ${allowedExtensions.join(', ')}`);
        }

        // Check file extension
        const fileName = file.name.toLowerCase();
        const hasValidExtension = allowedExtensions.some(ext => fileName.endsWith(ext));
        if (!hasValidExtension) {
            throw new Error(`Unsupported file extension. Allowed: ${allowedExtensions.join(', ')}`);
        }

        return true;
    }

    /**
     * Validate text input
     */
    validateText(text, options = {}) {
        const {
            minLength = 1,
            maxLength = 5000,
            fieldName = 'Text'
        } = options;

        if (!text || !text.trim()) {
            throw new Error(`${fieldName} cannot be empty.`);
        }

        if (text.length < minLength) {
            throw new Error(`${fieldName} must be at least ${minLength} characters.`);
        }

        if (text.length > maxLength) {
            throw new Error(`${fieldName} is too long. Maximum ${maxLength} characters.`);
        }

        return true;
    }
}

// Create global error handler instance
const errorHandler = new ErrorHandler();

