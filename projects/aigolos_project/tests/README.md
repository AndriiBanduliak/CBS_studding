# Тестирование AIGolos

Этот документ описывает структуру тестов и как их запускать.

## Структура тестов

```
tests/
├── conftest.py              # Pytest конфигурация и фикстуры
├── test_services/           # Unit-тесты для сервисов
│   ├── test_asr_service.py
│   ├── test_llm_service.py
│   └── test_tts_service.py
├── test_models/             # Тесты моделей
│   ├── test_user.py
│   ├── test_transcription.py
│   ├── test_conversation.py
│   └── test_synthesis.py
├── test_middleware/         # Тесты middleware
│   └── test_logging_middleware.py
├── test_views/              # Тесты views
│   ├── test_asr_views.py
│   └── test_llm_views.py
├── test_serializers/        # Тесты serializers
│   └── test_accounts_serializers.py
└── test_integration/        # Integration тесты
    └── test_api_flow.py
```

## Установка зависимостей

```bash
pip install -r requirements.txt
```

## Запуск тестов

### Все тесты
```bash
pytest
```

### С покрытием кода
```bash
pytest --cov=. --cov-report=html
```

### Конкретный файл
```bash
pytest tests/test_services/test_asr_service.py
```

### Конкретный тест
```bash
pytest tests/test_services/test_asr_service.py::TestASRService::test_transcribe_success
```

### Verbose режим
```bash
pytest -v
```

### С выводом print
```bash
pytest -s
```

## Покрытие кода

После запуска тестов с coverage, отчет будет доступен в:
- HTML: `htmlcov/index.html`
- Терминал: автоматически выводится
- XML: `coverage.xml` (для CI/CD)

Целевое покрытие: **>70%**

## Фикстуры

Основные фикстуры определены в `conftest.py`:

- `api_client` - API клиент без аутентификации
- `user` - тестовый пользователь
- `authenticated_client` - API клиент с аутентификацией
- `admin_user` - администратор
- `authenticated_admin_client` - API клиент администратора

## Mocking

Тесты используют mocking для:
- Внешних сервисов (Ollama, faster-whisper, Piper)
- Файловых операций
- HTTP запросов

## CI/CD

Тесты автоматически запускаются в GitHub Actions при:
- Push в `main` или `develop`
- Pull Request в `main` или `develop`

См. `.github/workflows/tests.yml` для деталей.

## Добавление новых тестов

1. Создайте файл в соответствующей директории
2. Используйте существующие фикстуры из `conftest.py`
3. Следуйте naming convention: `test_*.py`
4. Используйте классы для группировки связанных тестов
5. Добавьте docstrings для описания тестов

## Пример теста

```python
def test_example(self, authenticated_client, user):
    """Test example functionality."""
    response = authenticated_client.get('/api/endpoint/')
    assert response.status_code == 200
    assert 'data' in response.data
```

