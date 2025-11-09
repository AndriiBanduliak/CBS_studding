# ✅ Project Verification Checklist

## 🚀 Server Startup

- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Migrations applied: `python manage.py migrate`
- [ ] Static files collected: `python manage.py collectstatic --noinput`
- [ ] Server started: `python manage.py runserver`
- [ ] Server responds at http://127.0.0.1:8000/

## 🌐 Web Interface

- [ ] Home page opens: http://127.0.0.1:8000/
- [ ] Web interface works: http://127.0.0.1:8000/app/
- [ ] No errors in browser console (F12)

## 🎨 UX/UI Features

- [ ] **Dark Theme:**
  - [ ] Theme toggle button visible in navigation
  - [ ] Theme switches on click
  - [ ] Theme persists after page reload

- [ ] **Keyboard Shortcuts:**
  - [ ] `Ctrl + /` shows help
  - [ ] `Ctrl + K` opens chat
  - [ ] `Ctrl + M` opens ASR
  - [ ] `Ctrl + T` opens TTS
  - [ ] `Escape` closes modal window

- [ ] **Drag & Drop:**
  - [ ] Can drag file to ASR upload area
  - [ ] Visual indication appears on drag over

- [ ] **Audio Preview:**
  - [ ] Preview appears when file selected
  - [ ] Can listen to file before transcription
  - [ ] "Remove" button works

- [ ] **Responsive Design:**
  - [ ] Interface adapts on mobile devices
  - [ ] Modal windows display correctly on small screens

## 🔐 Authentication

- [ ] Registration works: http://127.0.0.1:8000/api/auth/register/
- [ ] Login works: http://127.0.0.1:8000/api/auth/login/
- [ ] Logout works: http://127.0.0.1:8000/api/auth/api/logout/
- [ ] Token saved in localStorage

## 📡 API

- [ ] Health check works: http://127.0.0.1:8000/api/health/
- [ ] API documentation accessible: http://127.0.0.1:8000/api/docs/
- [ ] Swagger UI loads and works
- [ ] ReDoc accessible: http://127.0.0.1:8000/api/redoc/

## 🎤 ASR (Speech Recognition)

- [ ] Can upload audio file
- [ ] File validation works (size, type)
- [ ] Audio preview works
- [ ] Progress bar shows during processing
- [ ] Transcription works (if faster-whisper installed)
- [ ] Result displays

## 💬 LLM (Chat)

- [ ] Can send message
- [ ] Text validation works (length)
- [ ] Spinner shows during processing
- [ ] Response from LLM arrives (if Ollama running)
- [ ] Message history saved

## 🔊 TTS (Text-to-Speech)

- [ ] Can enter text
- [ ] Text validation works
- [ ] Progress bar shows during synthesis
- [ ] Audio generated (if Piper installed)
- [ ] Can listen to result

## 📊 Metrics and Logging

- [ ] Logs written to `logs/` directory
- [ ] Correlation IDs present in logs
- [ ] No encoding errors in logs
- [ ] Metrics recorded (can check via MetricsCollector)

## 🐛 Error Handling

- [ ] Clear error messages on frontend
- [ ] Retry mechanism works (3 attempts)
- [ ] Client-side validation works
- [ ] Server errors handled correctly

## 📝 Additional Features

- [ ] Conversation export works: `python manage.py export_conversation --conversation-id 1 --format markdown`
- [ ] User statistics accessible: `/api/auth/api/stats/`
- [ ] Filtering and search work in transcription/conversation lists

## ✅ Summary

If all items checked - project works great! 🎉

If there are issues - see `TROUBLESHOOTING.md` or `HOW_TO_RUN.md`.
