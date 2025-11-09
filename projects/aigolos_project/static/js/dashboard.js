// Dashboard JavaScript

let currentConversationId = null;
let mediaRecorder = null;
let audioChunks = [];
let authToken = null;

// Make authToken globally accessible
window.authToken = null;

// Define modal functions IMMEDIATELY (before DOMContentLoaded) so they're available for onclick handlers
window.openASR = function() {
    const token = window.authToken || localStorage.getItem('token');
    if (!token) {
        alert('Please login or register to use this feature.');
        window.location.href = '/api/auth/login/';
        return;
    }
    if (typeof window.openModal === 'function') {
        window.openModal('asr-modal');
    } else {
        console.error('openModal function not found. Make sure main.js is loaded.');
    }
};

window.openChat = function() {
    const token = window.authToken || localStorage.getItem('token');
    if (!token) {
        alert('Please login or register to use this feature.');
        window.location.href = '/api/auth/login/';
        return;
    }
    if (typeof window.openModal === 'function') {
        window.openModal('chat-modal');
        // Load chat history after a short delay to ensure modal is visible
        setTimeout(() => {
            if (typeof loadChatHistory === 'function') {
                loadChatHistory();
            }
        }, 100);
    } else {
        console.error('openModal function not found. Make sure main.js is loaded.');
    }
};

window.openTTS = function() {
    const token = window.authToken || localStorage.getItem('token');
    if (!token) {
        alert('Please login or register to use this feature.');
        window.location.href = '/api/auth/login/';
        return;
    }
    if (typeof window.openModal === 'function') {
        window.openModal('tts-modal');
    } else {
        console.error('openModal function not found. Make sure main.js is loaded.');
    }
};

// Functions are already defined globally above

// Check authentication on page load
document.addEventListener('DOMContentLoaded', function() {
    // Try to get token from localStorage
    authToken = localStorage.getItem('token');
    window.authToken = authToken; // Make it globally accessible
    
    // Set up axios defaults
    if (authToken) {
        axios.defaults.headers.common['Authorization'] = 'Token ' + authToken;
    }
    
    // Check if user needs to login
    checkAuth();
    
    // Also attach event listeners as backup (in case onclick doesn't work)
    const asrBtn = document.querySelector('#asr-card .btn-feature');
    const chatBtn = document.querySelector('#llm-card .btn-feature');
    const ttsBtn = document.querySelector('#tts-card .btn-feature');
    
    if (asrBtn) {
        asrBtn.addEventListener('click', window.openASR);
    }
    if (chatBtn) {
        chatBtn.addEventListener('click', window.openChat);
    }
    if (ttsBtn) {
        ttsBtn.addEventListener('click', window.openTTS);
    }
});

function checkAuth() {
    // Auth check is now handled in individual open functions
    // This function can be used for other auth-related checks
}

// Audio preview
let audioPreview = null;

function showAudioPreview(file) {
    const audioUrl = URL.createObjectURL(file);
    const previewContainer = document.getElementById('audio-preview-container');
    if (!previewContainer) {
        // Create preview container
        const container = document.createElement('div');
        container.id = 'audio-preview-container';
        container.className = 'audio-preview';
        container.innerHTML = `
            <div class="audio-preview-info">
                <span>Preview: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)</span>
                <button class="audio-preview-remove" onclick="removeAudioPreview()">Remove</button>
            </div>
            <audio controls src="${audioUrl}"></audio>
        `;
        const audioUpload = document.querySelector('.audio-upload');
        if (audioUpload) {
            audioUpload.appendChild(container);
        }
    } else {
        const audio = previewContainer.querySelector('audio');
        if (audio) {
            audio.src = audioUrl;
        }
    }
    audioPreview = audioUrl;
}

function removeAudioPreview() {
    const previewContainer = document.getElementById('audio-preview-container');
    if (previewContainer) {
        previewContainer.remove();
    }
    if (audioPreview) {
        URL.revokeObjectURL(audioPreview);
        audioPreview = null;
    }
    const fileInput = document.getElementById('audio-file');
    if (fileInput) {
        fileInput.value = '';
    }
    document.getElementById('file-name').textContent = '';
}

// ASR Functions
document.getElementById('audio-file')?.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        // Validate file before showing name
        try {
            if (typeof errorHandler !== 'undefined') {
                errorHandler.validateFile(file, {
                    maxSize: 10 * 1024 * 1024, // 10 MB
                    allowedTypes: ['audio/wav', 'audio/mpeg', 'audio/flac', 'audio/ogg', 'audio/webm', 'audio/mp4'],
                    allowedExtensions: ['.wav', '.mp3', '.flac', '.ogg', '.webm', '.m4a']
                });
            }
            document.getElementById('file-name').textContent = `Selected: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`;
            // Show audio preview
            showAudioPreview(file);
            // Show transcribe button
            const transcribeBtn = document.getElementById('transcribe-btn');
            if (transcribeBtn) {
                transcribeBtn.style.display = 'inline-flex';
            }
        } catch (error) {
            document.getElementById('file-name').textContent = '';
            showNotification(error.message, 'error');
        }
    }
});

window.transcribeAudioFromPreview = function() {
    const fileInput = document.getElementById('audio-file');
    if (fileInput && fileInput.files.length > 0) {
        transcribeAudio(fileInput.files[0]);
    }
};

function transcribeAudio(file) {
    if (!authToken) {
        showNotification('Please login to use ASR', 'error');
        window.location.href = '/api/auth/login/';
        return;
    }
    
    // Validate file before upload
    if (typeof errorHandler !== 'undefined') {
        try {
            errorHandler.validateFile(file, {
                maxSize: 10 * 1024 * 1024, // 10 MB
                allowedTypes: ['audio/wav', 'audio/mpeg', 'audio/flac', 'audio/ogg', 'audio/webm', 'audio/mp4'],
                allowedExtensions: ['.wav', '.mp3', '.flac', '.ogg', '.webm', '.m4a']
            });
        } catch (error) {
            showNotification(error.message, 'error');
            return;
        }
    }
    
    const formData = new FormData();
    formData.append('audio', file);
    
    const resultEl = document.getElementById('transcription-result');
    const progressContainer = document.getElementById('transcription-loading');
    
    // Show progress bar
    const progress = typeof LoadingIndicator !== 'undefined' 
        ? LoadingIndicator.showProgress('transcription-loading', {
            showPercentage: true,
            indeterminate: true // ASR is long operation, use indeterminate
        })
        : null;
    
    resultEl.textContent = '';
    
    // Create request function
    const requestFn = () => {
        return axios.post('/api/asr/transcribe/', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
                'Authorization': 'Token ' + authToken
            },
            onUploadProgress: (progressEvent) => {
                if (progress && progressEvent.total) {
                    const percent = (progressEvent.loaded / progressEvent.total) * 100;
                    progress.update(percent);
                }
            }
        });
    };
    
    // Use error handler if available, otherwise direct call
    const request = typeof errorHandler !== 'undefined'
        ? errorHandler.handleRequest(requestFn)
        : requestFn();
    
    request
    .then(response => {
        if (progress) progress.hide();
        resultEl.textContent = response.data.text;
        showNotification('Transcription completed!', 'success');
        // Remove preview after successful transcription
        removeAudioPreview();
    })
    .catch(error => {
        if (progress) progress.hide();
        resultEl.textContent = '';
        if (typeof errorHandler !== 'undefined') {
            errorHandler.showError(error);
        } else {
            const errorMsg = error.response?.data?.error || 'Transcription failed';
            showNotification(errorMsg, 'error');
        }
    });
}

// Make functions globally available
window.toggleRecording = function() {
    const btn = document.getElementById('record-btn');
    const text = document.getElementById('record-text');
    
    if (!mediaRecorder || mediaRecorder.state === 'inactive') {
        startRecording();
        if (btn) {
            btn.classList.add('recording');
        }
        if (text) {
            text.textContent = 'Stop Recording';
        }
    } else {
        stopRecording();
        if (btn) {
            btn.classList.remove('recording');
        }
        if (text) {
            text.textContent = 'Start Recording';
        }
    }
};

function startRecording() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };
            
            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                transcribeAudio(audioBlob);
                stream.getTracks().forEach(track => track.stop());
            };
            
            mediaRecorder.start();
        })
        .catch(error => {
            showNotification('Microphone access denied', 'error');
        });
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
    }
}

// Chat Functions
function loadChatHistory() {
    // Load conversation history if exists
    const messagesEl = document.getElementById('chat-messages');
    messagesEl.innerHTML = '<div class="message assistant">Hello! How can I help you today?</div>';
}

window.handleChatKeyPress = function(event) {
    if (event.key === 'Enter') {
        window.sendMessage();
    }
};

window.sendMessage = function() {
    if (!authToken) {
        showNotification('Please login to use Chat', 'error');
        window.location.href = '/api/auth/login/';
        return;
    }
    
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    // Validate message
    if (typeof errorHandler !== 'undefined') {
        try {
            errorHandler.validateText(message, {
                minLength: 1,
                maxLength: 5000,
                fieldName: 'Message'
            });
        } catch (error) {
            showNotification(error.message, 'error');
            return;
        }
    }
    
    const messagesEl = document.getElementById('chat-messages');
    
    // Add user message
    // Using textContent instead of innerHTML prevents XSS attacks
    const userMsg = document.createElement('div');
    userMsg.className = 'message user';
    userMsg.textContent = message;  // Safe: textContent automatically escapes HTML
    messagesEl.appendChild(userMsg);
    
    input.value = '';
    
    // Show loading indicator
    if (typeof LoadingIndicator !== 'undefined') {
        LoadingIndicator.showSpinner('chat-loading');
    } else {
        document.getElementById('chat-loading').style.display = 'block';
    }
    messagesEl.scrollTop = messagesEl.scrollHeight;
    
    // Use error handler with retry
    const requestFn = () => {
        return axios.post('/api/llm/chat/', {
            message: message,
            conversation_id: currentConversationId
        }, {
            headers: {
                'Authorization': 'Token ' + authToken
            }
        });
    };
    
    const request = typeof errorHandler !== 'undefined'
        ? errorHandler.handleRequest(requestFn)
        : requestFn();
    
    request
    .then(response => {
        if (typeof LoadingIndicator !== 'undefined') {
            LoadingIndicator.hideSpinner('chat-loading');
        } else {
            document.getElementById('chat-loading').style.display = 'none';
        }
        
        if (!currentConversationId) {
            currentConversationId = response.data.conversation_id;
        }
        
        // Add AI message
        // Using textContent instead of innerHTML prevents XSS attacks
        const aiMsg = document.createElement('div');
        aiMsg.className = 'message assistant';
        aiMsg.textContent = response.data.ai_message.content;  // Safe: textContent automatically escapes HTML
        messagesEl.appendChild(aiMsg);
        
        messagesEl.scrollTop = messagesEl.scrollHeight;
    })
    .catch(error => {
        if (typeof LoadingIndicator !== 'undefined') {
            LoadingIndicator.hideSpinner('chat-loading');
        } else {
            document.getElementById('chat-loading').style.display = 'none';
        }
        if (typeof errorHandler !== 'undefined') {
            errorHandler.showError(error);
        } else {
            const errorMsg = error.response?.data?.error || 'Chat failed';
            showNotification(errorMsg, 'error');
        }
    });
}

// TTS Functions - Make globally available
window.synthesizeSpeech = function() {
    if (!authToken) {
        showNotification('Please login to use TTS', 'error');
        window.location.href = '/api/auth/login/';
        return;
    }
    
    const text = document.getElementById('tts-text').value.trim();
    const voice = document.getElementById('tts-voice').value;
    
    // Validate text
    if (typeof errorHandler !== 'undefined') {
        try {
            errorHandler.validateText(text, {
                minLength: 1,
                maxLength: 5000,
                fieldName: 'Text'
            });
        } catch (error) {
            showNotification(error.message, 'error');
            return;
        }
    }
    
    const audioContainer = document.getElementById('tts-audio-container');
    const audioEl = document.getElementById('tts-audio');
    
    // Show progress bar
    const progress = typeof LoadingIndicator !== 'undefined'
        ? LoadingIndicator.showProgress('tts-loading', {
            showPercentage: true,
            indeterminate: true // TTS is long operation
        })
        : null;
    
    audioContainer.style.display = 'none';
    
    // Use error handler with retry
    const requestFn = () => {
        return axios.post('/api/tts/synthesize/', {
            text: text,
            voice: voice || undefined
        }, {
            responseType: 'blob',
            headers: {
                'Authorization': 'Token ' + authToken
            },
            onDownloadProgress: (progressEvent) => {
                if (progress && progressEvent.total) {
                    const percent = (progressEvent.loaded / progressEvent.total) * 100;
                    progress.update(percent);
                }
            }
        });
    };
    
    const request = typeof errorHandler !== 'undefined'
        ? errorHandler.handleRequest(requestFn)
        : requestFn();
    
    request
    .then(response => {
        if (progress) progress.hide();
        const audioUrl = URL.createObjectURL(response.data);
        audioEl.src = audioUrl;
        audioContainer.style.display = 'block';
        showNotification('Speech synthesized successfully!', 'success');
    })
    .catch(error => {
        if (progress) progress.hide();
        if (typeof errorHandler !== 'undefined') {
            errorHandler.showError(error);
        } else {
            const errorMsg = error.response?.data?.error || 'Synthesis failed';
            showNotification(errorMsg, 'error');
        }
    });
};

// German Speaking Trainer Functions
let trainerCurrentSentence = '';
let trainerAudioBlob = null;
let trainerMediaRecorder = null;
let trainerAudioChunks = [];

window.openTrainer = function() {
    const token = window.authToken || localStorage.getItem('token');
    if (!token) {
        alert('Please login or register to use this feature.');
        window.location.href = '/api/auth/login/';
        return;
    }
    if (typeof window.openModal === 'function') {
        window.openModal('trainer-modal');
        // Reset trainer state
        trainerCurrentSentence = '';
        trainerAudioBlob = null;
        const step1 = document.getElementById('step-1');
        const step2 = document.getElementById('step-2');
        const step3 = document.getElementById('step-3');
        const playBtn = document.getElementById('play-sentence-btn');
        if (step1) step1.style.display = 'block';
        if (step2) step2.style.display = 'none';
        if (step3) step3.style.display = 'none';
        if (playBtn) playBtn.style.display = 'none';
    }
};

window.generateGermanSentence = function() {
    if (!authToken) {
        showNotification('Please login to use Trainer', 'error');
        return;
    }
    
    const textDisplay = document.getElementById('trainer-text-display');
    if (!textDisplay) return;
    
    textDisplay.innerHTML = '<div class="loading-spinner"></div><p>Generating German sentence...</p>';
    
    // Ask AI to generate a German sentence for practice
    const requestFn = () => {
        return axios.post('/api/llm/chat/', {
            message: 'Generate a simple German sentence for pronunciation practice. The sentence should be suitable for a beginner to intermediate learner. Respond ONLY with the German sentence, no explanations.',
            conversation_id: null
        }, {
            headers: {
                'Authorization': 'Token ' + authToken
            }
        });
    };
    
    const request = typeof errorHandler !== 'undefined'
        ? errorHandler.handleRequest(requestFn)
        : requestFn();
    
    request
    .then(response => {
        trainerCurrentSentence = response.data.ai_message.content.trim();
        textDisplay.innerHTML = `<p style="font-size: 1.5rem; font-weight: 600; color: var(--primary-color); margin: 1rem 0;">${trainerCurrentSentence}</p>`;
        const playBtn = document.getElementById('play-sentence-btn');
        const step2 = document.getElementById('step-2');
        if (playBtn) playBtn.style.display = 'inline-flex';
        if (step2) step2.style.display = 'block';
        showNotification('Sentence generated! Listen and then record your pronunciation.', 'success');
    })
    .catch(error => {
        textDisplay.innerHTML = '<p style="color: var(--danger-color);">Failed to generate sentence. Please try again.</p>';
        if (typeof errorHandler !== 'undefined') {
            errorHandler.showError(error);
        } else {
            showNotification('Failed to generate sentence', 'error');
        }
    });
};

window.playGermanSentence = function() {
    if (!trainerCurrentSentence) {
        showNotification('No sentence to play. Generate one first.', 'error');
        return;
    }
    
    // Use TTS to play the German sentence
    const requestFn = () => {
        return axios.post('/api/tts/synthesize/', {
            text: trainerCurrentSentence,
            voice: 'de_DE/thorsten/medium' // German voice
        }, {
            responseType: 'blob',
            headers: {
                'Authorization': 'Token ' + authToken
            }
        });
    };
    
    const request = typeof errorHandler !== 'undefined'
        ? errorHandler.handleRequest(requestFn)
        : requestFn();
    
    request
    .then(response => {
        const audioUrl = URL.createObjectURL(response.data);
        const audio = new Audio(audioUrl);
        audio.play();
        showNotification('Playing German sentence...', 'info');
        
        audio.onended = () => {
            URL.revokeObjectURL(audioUrl);
        };
    })
    .catch(error => {
        if (typeof errorHandler !== 'undefined') {
            errorHandler.showError(error);
        } else {
            showNotification('Failed to play sentence. TTS may not be available.', 'error');
        }
    });
};

window.toggleTrainerRecording = function() {
    const btn = document.getElementById('trainer-record-btn');
    const text = document.getElementById('trainer-record-text');
    const status = document.getElementById('trainer-recording-status');
    
    if (!trainerMediaRecorder || trainerMediaRecorder.state === 'inactive') {
        startTrainerRecording();
        if (btn) btn.classList.add('recording');
        if (text) text.textContent = 'Stop Recording';
        if (status) status.style.display = 'block';
    } else {
        stopTrainerRecording();
        if (btn) btn.classList.remove('recording');
        if (text) text.textContent = 'Start Recording';
        if (status) status.style.display = 'none';
    }
};

function startTrainerRecording() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            trainerMediaRecorder = new MediaRecorder(stream);
            trainerAudioChunks = [];
            
            trainerMediaRecorder.ondataavailable = event => {
                trainerAudioChunks.push(event.data);
            };
            
            trainerMediaRecorder.onstop = () => {
                trainerAudioBlob = new Blob(trainerAudioChunks, { type: 'audio/wav' });
                analyzePronunciation();
                stream.getTracks().forEach(track => track.stop());
            };
            
            trainerMediaRecorder.start();
        })
        .catch(error => {
            showNotification('Microphone access denied', 'error');
        });
}

function stopTrainerRecording() {
    if (trainerMediaRecorder && trainerMediaRecorder.state !== 'inactive') {
        trainerMediaRecorder.stop();
    }
}

function analyzePronunciation() {
    if (!trainerAudioBlob || !trainerCurrentSentence) {
        showNotification('Missing audio or sentence', 'error');
        return;
    }
    
    const step3 = document.getElementById('step-3');
    const feedbackEl = document.getElementById('trainer-feedback');
    if (!step3 || !feedbackEl) return;
    
    step3.style.display = 'block';
    feedbackEl.innerHTML = '<div class="loading-spinner"></div><p>Analyzing your pronunciation...</p>';
    
    // First, transcribe the audio
    const formData = new FormData();
    formData.append('audio', trainerAudioBlob, 'recording.wav');
    
    const transcribeRequest = axios.post('/api/asr/transcribe/', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': 'Token ' + authToken
        }
    });
    
    transcribeRequest
    .then(transcribeResponse => {
        const recognizedText = transcribeResponse.data.text;
        
        // Then ask AI to evaluate pronunciation
        const evaluationPrompt = `You are a German language teacher. A student tried to pronounce this German sentence: "${trainerCurrentSentence}"

The speech recognition system transcribed what the student said as: "${recognizedText}"

Please provide:
1. Accuracy score (0-100): How close was the pronunciation?
2. Feedback: What was good and what needs improvement?
3. Tips: Specific pronunciation tips for this sentence

Format your response as:
SCORE: [number]/100
FEEDBACK: [your feedback]
TIPS: [your tips]`;
        
        return axios.post('/api/llm/chat/', {
            message: evaluationPrompt,
            conversation_id: null
        }, {
            headers: {
                'Authorization': 'Token ' + authToken
            }
        });
    })
    .then(evalResponse => {
        const feedback = evalResponse.data.ai_message.content;
        feedbackEl.innerHTML = `
            <div style="background: var(--bg-elevated); padding: 1.5rem; border-radius: var(--radius-lg); border: 1px solid var(--border-color);">
                <h4 style="color: var(--primary-color); margin-bottom: 1rem;">Pronunciation Feedback</h4>
                <div style="color: var(--text-primary); white-space: pre-wrap; line-height: 1.8;">${feedback}</div>
                <button class="btn-feature" onclick="window.generateGermanSentence && window.generateGermanSentence()" style="margin-top: 1.5rem;">
                    <i class="fas fa-redo"></i> Try Another Sentence
                </button>
            </div>
        `;
    })
    .catch(error => {
        feedbackEl.innerHTML = `
            <div style="color: var(--danger-color);">
                <p>Failed to analyze pronunciation. Please try again.</p>
                <button class="btn-feature" onclick="window.generateGermanSentence && window.generateGermanSentence()" style="margin-top: 1rem;">
                    <i class="fas fa-redo"></i> Try Again
                </button>
            </div>
        `;
        if (typeof errorHandler !== 'undefined') {
            errorHandler.showError(error);
        }
    });
}

