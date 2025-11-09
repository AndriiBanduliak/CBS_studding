# 🔧 Troubleshooting

## Encoding Issues in Logs (Windows)

### Symptoms

Errors appear in logs:
```
UnicodeEncodeError: 'charmap' codec can't encode character '\xa8' in position 90
```

### Cause

Windows uses cp1251 encoding by default, which doesn't support all Unicode characters.

### Solution

Fixed automatically! Created `SafeStreamHandler` that safely handles Unicode characters.

If problem persists, set environment variable:

```bash
# Windows PowerShell
$env:PYTHONIOENCODING="utf-8"

# Windows CMD
set PYTHONIOENCODING=utf-8

# Linux/Mac
export PYTHONIOENCODING=utf-8
```

## Error "You're accessing the development server over HTTPS"

### Symptoms

Appears in logs:
```
ERROR: You're accessing the development server over HTTPS, but it only supports HTTP.
```

### Cause

1. Browser tries to connect via HTTPS (automatic redirect)
2. Port scanners or bots trying to connect
3. Browser extensions (e.g., HTTPS Everywhere)

### Solution

**This is normal and not critical!** Django development server supports only HTTP.

**For development:**
- Use `http://127.0.0.1:8000` (not `https://`)
- Ignore these errors - they don't affect functionality

**For production:**
- Use web server (nginx, Apache) with SSL
- Or use Django with SSL via middleware

## Bad request version errors

### Symptoms

Appears in logs:
```
code 400, message Bad request version ('...')
```

### Cause

1. Port scanners trying to connect
2. Bots looking for vulnerabilities
3. Invalid HTTP requests

### Solution

**This is normal!** These are external connection attempts that the server rejects.

**For protection:**
- Use firewall
- Don't expose port 8000 to internet
- In production use web server (nginx) as reverse proxy

## Startup Issues

### Issue: Port 8000 is Busy

```bash
# Use different port
python manage.py runserver 8001
```

### Issue: ModuleNotFoundError

```bash
# Install dependencies
pip install -r requirements.txt
```

### Issue: Database Not Created

```bash
# Apply migrations
python manage.py migrate
```

### Issue: Static Files Not Loading

```bash
# Collect static files
python manage.py collectstatic --noinput
```

## ASR/TTS Issues

### ASR Not Working

1. Install faster-whisper:
   ```bash
   pip install faster-whisper
   ```

2. Check logs: `logs/errors.log`

3. Ensure model is loaded (first request may be slow)

### TTS Not Working

1. Install Piper TTS:
   - Download from https://github.com/rhasspy/piper
   - Add to PATH

2. Or use Docker version (Piper included)

### LLM Not Working

1. Ensure Ollama is running:
   ```bash
   ollama serve
   ```

2. Check model:
   ```bash
   ollama list
   ollama pull qwen2.5:7b
   ```

3. Check `OLLAMA_BASE_URL` in settings

## Windows Console Encoding Issues

### Set UTF-8 for Console

```powershell
# PowerShell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING="utf-8"

# Or at start of each session
chcp 65001
```

### In Python Code

Add to beginning of `manage.py`:
```python
import sys
import io

# Set UTF-8 for stdout/stderr
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
```

## Functionality Verification

### Quick Check

```bash
# 1. Django check
python manage.py check

# 2. Check migrations
python manage.py showmigrations

# 3. Check static files
python manage.py collectstatic --dry-run

# 4. Test API
curl http://127.0.0.1:8000/api/health/
```

### Check Logs

```bash
# Windows PowerShell
Get-Content logs\errors.log -Tail 20 -Encoding UTF8

# Linux/Mac
tail -20 logs/errors.log
```

## Getting Help

If problem is not resolved:

1. Check logs: `logs/errors.log` and `logs/info.log`
2. Run with debug: `python manage.py runserver --verbosity 2`
3. Check versions: `pip list`
4. Check settings: `python manage.py diffsettings`

## Frequently Asked Questions

**Q: Why so many errors in logs?**  
A: Many errors are external connection attempts (scanners, bots). This is normal for development server.

**Q: Should I fix HTTPS errors?**  
A: No, this is normal for development. In production use web server with SSL.

**Q: How to disable connection error logging?**  
A: Can configure logging level in `settings.py`, but better to leave as is for security.

**Q: Why Unicode errors?**  
A: Windows uses cp1251 by default. Use UTF-8 via environment variables or SafeStreamHandler (already configured).
