# AIGolos

<div align="center">

![Django](https://img.shields.io/badge/Django-4.2+-green.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

**Professional AI Voice Assistant Platform with Django**

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Docker](#docker) • [API Documentation](#api-documentation)

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Docker Deployment](#docker-deployment)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

AIGolos is a professional, full-featured AI voice assistant platform built with Django. It combines three powerful AI technologies:

- **ASR (Automatic Speech Recognition)**: Convert speech to text using faster-whisper
- **LLM (Large Language Model)**: Generate intelligent responses using Ollama
- **TTS (Text-to-Speech)**: Convert text to natural speech using Piper

The platform features a modern web interface, user authentication, comprehensive logging, and Docker support.

## ✨ Features

### Core Functionality
- 🎤 **Speech Recognition**: High-quality transcription using Whisper models
- 🤖 **AI Chat**: Intelligent conversations powered by Ollama LLM
- 🔊 **Text-to-Speech**: Natural voice synthesis with Piper TTS
- 👤 **User Authentication**: Secure registration and login system
- 📊 **History Tracking**: Save and manage transcriptions, conversations, and syntheses

### Technical Features
- 🚀 **Django REST Framework**: Professional API architecture
- 🎨 **Modern UI**: Beautiful, responsive web interface with animations
- 📝 **Comprehensive Logging**: Detailed error and activity logging
- 🐳 **Docker Support**: Easy deployment with Docker and docker-compose
- 🔒 **Security**: Token-based authentication, CSRF protection
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile

## 📦 Requirements

- Python 3.10 or higher
- PostgreSQL (optional, SQLite for development)
- [Ollama](https://ollama.ai) installed and running
- [Piper TTS](https://github.com/rhasspy/piper) (optional, for TTS functionality)
- [faster-whisper](https://github.com/guillaumekln/faster-whisper) (optional, for ASR functionality)

## 🚀 Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd aigolos
```

### 2. Create virtual environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install optional dependencies

```bash
# For ASR (Speech Recognition)
pip install faster-whisper

# For TTS (Text-to-Speech)
# Download Piper from: https://github.com/rhasspy/piper/releases
```

### 5. Set up environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (optional - uses SQLite by default)
DATABASE_URL=postgresql://user:password@localhost:5432/aigolos

# ASR Settings
ASR_MODEL_NAME=large-v3
ASR_DEVICE=cpu
ASR_COMPUTE_TYPE=int8

# LLM Settings
LLM_BACKEND=ollama
LLM_MODEL_NAME=qwen2.5:7b
OLLAMA_BASE_URL=http://localhost:11434
LLM_MAX_TOKENS=256
LLM_TEMPERATURE=0.7

# TTS Settings
TTS_VOICE_NAME=de_DE/thorsten/medium
TTS_MODEL_PATH=

# Session Settings
SESSION_TIMEOUT=3600
MAX_AUDIO_SIZE=10485760
```

### 6. Set up database

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 7. Collect static files

```bash
python manage.py collectstatic
```

### 8. Set up Ollama

```bash
# Install Ollama from https://ollama.ai
# Then pull a model:
ollama pull qwen2.5:7b
```

## ⚙️ Configuration

All configuration is done via environment variables. See the `.env` file example above.

### Key Settings

- **SECRET_KEY**: Django secret key (required in production)
- **DEBUG**: Set to `False` in production
- **ASR_MODEL_NAME**: Whisper model (e.g., `base`, `small`, `medium`, `large-v3`)
- **ASR_DEVICE**: `cpu` or `cuda` for GPU acceleration
- **LLM_MODEL_NAME**: Ollama model name
- **OLLAMA_BASE_URL**: Ollama API endpoint
- **TTS_VOICE_NAME**: Piper voice to use

## 💻 Usage

### Start the development server

```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

### Access points

- **Web Interface**: `http://localhost:8000/app/`
- **Admin Panel**: `http://localhost:8000/admin/`
- **API Health**: `http://localhost:8000/api/health/`
- **API Documentation (Swagger)**: `http://localhost:8000/api/docs/`
- **API Documentation (ReDoc)**: `http://localhost:8000/api/redoc/`

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Using Docker

```bash
# Build image
docker build -t aigolos .

# Run container
docker run -d -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  -e DEBUG=False \
  aigolos
```

### Docker Compose Services

- **web**: Django application
- **db**: PostgreSQL database
- **ollama**: Ollama LLM service

## 📚 API Documentation

### Interactive API Documentation

The API includes interactive documentation powered by Swagger/OpenAPI:

- **Swagger UI**: `http://localhost:8000/api/docs/` - Interactive API explorer
- **ReDoc**: `http://localhost:8000/api/redoc/` - Alternative documentation interface
- **OpenAPI Schema**: `http://localhost:8000/api/schema/` - Raw OpenAPI schema

### API Versioning

The API is versioned. Current version is **v1**:

- **v1 API**: `/api/v1/` - Current stable version
- **Legacy API**: `/api/` - Backward compatibility (redirects to v1)

### Authentication

All API endpoints (except registration and login) require authentication via token.

#### Register
```http
POST /api/auth/api/register/
Content-Type: application/json

{
  "username": "user",
  "email": "user@example.com",
  "password": "password123",
  "password_confirm": "password123"
}
```

#### Login
```http
POST /api/auth/api/login/
Content-Type: application/json

{
  "username": "user",
  "password": "password123"
}
```

#### Get Profile
```http
GET /api/auth/api/profile/
Authorization: Token <your-token>
```

#### Get User Statistics
```http
GET /api/auth/api/stats/
Authorization: Token <your-token>
```

Returns:
- `total_transcriptions` - Total number of transcriptions
- `total_conversations` - Total number of conversations
- `total_syntheses` - Total number of syntheses
- `recent_activity` - Activity summary for last 7 days

### ASR (Speech Recognition)

#### Transcribe Audio
```http
POST /api/asr/transcribe/
Authorization: Token <your-token>
Content-Type: multipart/form-data

audio: <audio_file>
language: <optional_language_code>
```

#### Get Transcription History
```http
GET /api/asr/history/
Authorization: Token <your-token>
```

**Query Parameters:**
- `search` - Search in transcription text
- `language` - Filter by language code
- `created_after` - Filter by creation date (ISO format)
- `created_before` - Filter by creation date (ISO format)
- `ordering` - Sort by field (`created_at`, `language`, `-created_at`, etc.)
- `page` - Page number for pagination

**Example:**
```http
GET /api/asr/history/?search=hello&language=en&ordering=-created_at&page=1
```

### LLM (Chat)

#### Send Message
```http
POST /api/llm/chat/
Authorization: Token <your-token>
Content-Type: application/json

{
  "message": "Hello, how are you?",
  "conversation_id": "optional-conversation-id"
}
```

#### Get Conversations
```http
GET /api/llm/conversations/
Authorization: Token <your-token>
```

**Query Parameters:**
- `search` - Search in conversation title and messages
- `title` - Filter by title (partial match)
- `created_after` - Filter by creation date (ISO format)
- `created_before` - Filter by creation date (ISO format)
- `updated_after` - Filter by update date (ISO format)
- `updated_before` - Filter by update date (ISO format)
- `ordering` - Sort by field (`created_at`, `updated_at`, `title`, etc.)
- `page` - Page number for pagination

**Example:**
```http
GET /api/llm/conversations/?search=python&ordering=-updated_at&page=1
```

### TTS (Text-to-Speech)

#### Synthesize Text
```http
POST /api/tts/synthesize/
Authorization: Token <your-token>
Content-Type: application/json

{
  "text": "Hello, this is a test",
  "voice": "optional-voice-name"
}
```

## 📁 Project Structure

```
aigolos/
├── aigolos/              # Main Django project
│   ├── settings.py       # Django settings
│   ├── urls.py          # URL configuration
│   ├── wsgi.py          # WSGI config
│   └── middleware.py    # Custom middleware
├── accounts/            # User authentication app
├── core/                # Core app (web interface)
├── asr/                 # Speech recognition app
├── llm/                 # Language model app
├── tts/                 # Text-to-speech app
├── templates/           # HTML templates
├── static/              # Static files (CSS, JS)
├── media/               # User uploaded files
├── logs/                # Application logs
├── manage.py            # Django management script
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose configuration
└── README.md            # This file
```

## 🛠️ Development

### Running tests

```bash
# Using pytest (recommended)
pytest

# With coverage
pytest --cov=. --cov-report=html

# Using Django test runner
python manage.py test
```

See [TESTING_SETUP.md](TESTING_SETUP.md) for detailed testing documentation.

### Creating migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Accessing admin panel

```bash
python manage.py createsuperuser
# Then visit http://localhost:8000/admin/
```

## 📝 Logging

Logs are stored in the `logs/` directory:

- `errors.log`: Error-level logs
- `info.log`: Info-level logs

Logging is configured in `aigolos/settings.py` with JSON formatting for errors and verbose formatting for info logs.

## 🔧 Troubleshooting

### Common Issues

**1. ModuleNotFoundError: No module named 'drf_spectacular'**
```bash
pip install -r requirements.txt
```

**2. ASR/TTS not working**
- Ensure faster-whisper is installed: `pip install faster-whisper`
- Ensure Piper TTS is installed and in PATH
- Check logs in `logs/errors.log` for detailed error messages

**3. Ollama connection errors**
- Ensure Ollama is running: `ollama serve`
- Check `OLLAMA_BASE_URL` in `.env` file
- Verify model is pulled: `ollama list`

**4. Database migration errors**
```bash
python manage.py makemigrations
python manage.py migrate
```

**5. Static files not loading**
```bash
python manage.py collectstatic --noinput
```

### Management Commands

**Export user data:**
```bash
# Export to JSON
python manage.py export_data --username user1 --output export/

# Export to CSV
python manage.py export_data --username user1 --output export/ --format csv

# Export both formats
python manage.py export_data --username user1 --output export/ --format both
```

**Clean up old data:**
```bash
# Dry run (show what would be deleted)
python manage.py cleanup_old_data --days 90 --dry-run

# Actually delete
python manage.py cleanup_old_data --days 90
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Andrii Banduliak**

---

<div align="center">

Made with ❤️ by Andrii Banduliak

**AIGolos v2.0.0** - Professional AI Voice Assistant Platform

</div>
