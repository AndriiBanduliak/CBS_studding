# 🚀 How to Run the Project for Testing

## Quick Start

### 1. Install Dependencies (if not already installed)

```bash
pip install -r requirements.txt
```

### 2. Apply Database Migrations

```bash
python manage.py migrate
```

### 3. Create Superuser (optional, for admin access)

```bash
python manage.py createsuperuser
```

### 4. Start Development Server

```bash
# Windows
python manage.py runserver

# Or use the ready script
run.bat
```

Server will start on `http://127.0.0.1:8000/`

## Functionality Verification

### 1. Open in Browser

- **Home Page:** http://127.0.0.1:8000/
- **API Documentation (Swagger):** http://127.0.0.1:8000/api/docs/
- **ReDoc Documentation:** http://127.0.0.1:8000/api/redoc/
- **Admin Panel:** http://127.0.0.1:8000/admin/

### 2. Check New Features

#### Dark Theme
- Open http://127.0.0.1:8000/app/
- Click theme toggle button in navigation (🌙/☀️)
- Verify theme persists after page reload

#### Keyboard Shortcuts
- Press `Ctrl + /` (or `Cmd + /` on Mac) - help should appear
- Press `Ctrl + K` - chat should open
- Press `Ctrl + M` - ASR should open
- Press `Ctrl + T` - TTS should open
- Press `Escape` - modal window should close

#### Drag & Drop
- Open ASR modal window
- Drag audio file to upload area
- Visual indication should appear

#### Audio Preview
- Select audio file
- Preview with player should appear
- Can listen before transcription

#### Responsive Design
- Open DevTools (F12)
- Switch to mobile device mode
- Verify interface adapts

### 3. Check API

#### User Registration
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"testpass123"}'
```

#### Login
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'
```

#### Get User Statistics
```bash
curl -X GET http://127.0.0.1:8000/api/auth/api/stats/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

### 4. Check Metrics

```python
python manage.py shell
>>> from core.metrics import MetricsCollector
>>> # After several requests
>>> metrics = MetricsCollector.get_api_metrics()
>>> print(metrics)
```

### 5. Check Logging

Logs are in `logs/` folder:
- `logs/errors.log` - errors
- `logs/info.log` - informational logs
- `logs/app.json.log` - JSON logs (in production)

Verify logs contain correlation IDs:
```bash
# Windows PowerShell
Get-Content logs\info.log -Tail 20

# Linux/Mac
tail -20 logs/info.log
```

### 6. Check Conversation Export

```bash
# First create conversation via API or web interface
# Then export
python manage.py export_conversation --conversation-id 1 --format markdown
```

## Code Quality Checks

### Code Formatting

```bash
# Windows
format_code.bat

# Linux/Mac
chmod +x format_code.sh
./format_code.sh
```

### Django Check

```bash
python manage.py check
```

### Run Tests

```bash
pytest
# or
python manage.py test
```

## Docker Verification (Optional)

If you want to check Docker version:

```bash
# Build image
docker build -t aigolos .

# Run with docker-compose
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f web
```

## Common Issues

### Issue: Port 8000 is Busy

**Solution:** Use different port:
```bash
python manage.py runserver 8001
```

### Issue: Database Not Created

**Solution:** Apply migrations:
```bash
python manage.py migrate
```

### Issue: Static Files Not Loading

**Solution:** Collect static files:
```bash
python manage.py collectstatic
```

### Issue: Ollama Not Running

**Solution:** 
- For local development: run Ollama separately
- For Docker: `docker-compose up ollama`

## Complete Verification Checklist

- [ ] Server starts without errors
- [ ] Home page opens
- [ ] API documentation accessible
- [ ] Registration/login works
- [ ] Dark theme toggles
- [ ] Keyboard shortcuts work
- [ ] Drag & drop works
- [ ] Audio preview works
- [ ] Responsive design works on mobile
- [ ] API endpoints respond
- [ ] Metrics are recorded
- [ ] Logs contain correlation IDs
- [ ] Conversation export works

## Done! 🎉

If all checks pass, project is ready to use!
