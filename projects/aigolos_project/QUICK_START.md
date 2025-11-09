# 🚀 Quick Start

## Running the Project

### Easiest Way (Windows):

```bash
run.bat
```

This script automatically:
- ✅ Activates virtual environment
- ✅ Fixes encoding (UTF-8)
- ✅ Applies migrations
- ✅ Collects static files
- ✅ Starts the server

### Manually:

```bash
# 1. Activate virtual environment
venv\Scripts\activate

# 2. Install dependencies (if not already installed)
pip install -r requirements.txt

# 3. Apply migrations
python manage.py migrate

# 4. Collect static files
python manage.py collectstatic --noinput

# 5. Start the server
python manage.py runserver
```

## Open in Browser

After starting, open:
- **Home:** http://127.0.0.1:8000/
- **Web Interface:** http://127.0.0.1:8000/app/
- **API Documentation (Swagger):** http://127.0.0.1:8000/api/docs/
- **API Documentation (ReDoc):** http://127.0.0.1:8000/api/redoc/
- **Health Check:** http://127.0.0.1:8000/api/health/

**IMPORTANT:** Use `http://` (not `https://`) - development server supports only HTTP!

**If browser automatically switches to HTTPS:**
- Clear HSTS: `chrome://net-internals/#hsts` → Delete domain → `127.0.0.1`
- Or use incognito mode
- Or see `TROUBLESHOOTING.md` for detailed instructions

## Verification

### 1. Core Functionality
- ✅ **Open home page** - should load without errors
- ✅ **Try registration** - create account via http://127.0.0.1:8000/api/auth/register/
- ✅ **Login** - http://127.0.0.1:8000/api/auth/login/

### 2. New UX/UI Features
- ✅ **Dark theme** - toggle button in navigation (🌙/☀️)
- ✅ **Keyboard shortcuts:**
  - `Ctrl + /` (or `Cmd + /` on Mac) - shortcuts help
  - `Ctrl + K` - open chat
  - `Ctrl + M` - open ASR
  - `Ctrl + T` - open TTS
  - `Escape` - close modal window
- ✅ **Drag & drop** - drag audio file to ASR upload area
- ✅ **Audio preview** - select file, preview with player appears

### 3. API Features
- ✅ **API Documentation** - http://127.0.0.1:8000/api/docs/
- ✅ **Health check** - http://127.0.0.1:8000/api/health/
- ✅ **User statistics** - `/api/auth/api/stats/` (requires authentication)

### 4. Log Verification
- ✅ **Encoding errors should be absent** - if server restarted after fixes
- ✅ **HTTPS errors are filtered** - should not appear
- ✅ **Only normal requests are logged**

## If Something Doesn't Work

### Encoding Errors
- Use `run.bat` - it automatically fixes encoding
- Or see `TROUBLESHOOTING.md`

### HTTPS Errors
- This is normal! Use `http://` (not `https://`)
- See `TROUBLESHOOTING.md` for details

### Modules Not Found
```bash
pip install -r requirements.txt
```

### Database
```bash
python manage.py migrate
```

## Done! 🎉

The project should work. If there are issues, see `TROUBLESHOOTING.md` or `HOW_TO_RUN.md`.
