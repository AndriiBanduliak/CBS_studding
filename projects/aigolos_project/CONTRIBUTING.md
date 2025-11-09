# Contributing to AIGolos

Thank you for your interest in contributing to AIGolos! This document provides guidelines and instructions for contributing.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Code Style](#code-style)
- [Documentation](#documentation)

## 🤝 Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/aigolos.git
   cd aigolos
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/original-owner/aigolos.git
   ```

## 💻 Development Setup

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**:
   ```bash
   python manage.py runserver
   ```

## ✏️ Making Changes

### Branch Naming

Use descriptive branch names:
- `feature/description` - New features
- `fix/description` - Bug fixes
- `refactor/description` - Code refactoring
- `docs/description` - Documentation updates
- `test/description` - Test additions/updates

### Commit Messages

Follow conventional commit format:
```
type(scope): subject

body (optional)

footer (optional)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test additions/updates
- `chore`: Maintenance tasks

**Examples:**
```
feat(asr): add language auto-detection
fix(llm): resolve conversation context bug
docs(readme): update installation instructions
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_services/test_asr_service.py

# Run specific test
pytest tests/test_services/test_asr_service.py::TestASRService::test_transcribe
```

### Writing Tests

- Place tests in `tests/` directory
- Follow existing test structure
- Use descriptive test names
- Test both success and failure cases
- Aim for >70% code coverage

**Example:**
```python
def test_transcribe_audio_success(api_client, user_factory):
    """Test successful audio transcription."""
    user = user_factory()
    api_client.force_authenticate(user=user)
    
    # Test implementation
    ...
```

## 📤 Submitting Changes

1. **Update your fork**:
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes** and commit:
   ```bash
   git add .
   git commit -m "feat(scope): your commit message"
   ```

4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request** on GitHub:
   - Provide clear description
   - Reference related issues
   - Include screenshots if UI changes
   - Ensure all tests pass

## 📝 Code Style

### Python

- Follow PEP 8 style guide
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use meaningful variable names
- Add docstrings to functions/classes

**Example:**
```python
def transcribe_audio(
    self,
    audio_data: bytes,
    language: Optional[str] = None
) -> Tuple[str, Optional[str]]:
    """
    Transcribe audio to text.
    
    Args:
        audio_data: Audio file bytes
        language: Optional language code
        
    Returns:
        Tuple of (transcribed_text, detected_language)
    """
    ...
```

### Django

- Follow Django best practices
- Use Django ORM (avoid raw SQL)
- Use select_related/prefetch_related for optimization
- Add indexes for frequently queried fields

### Frontend

- Use semantic HTML
- Follow BEM naming convention for CSS
- Use meaningful JavaScript variable names
- Comment complex logic

## 📚 Documentation

### Code Documentation

- Add docstrings to all public functions/classes
- Include parameter descriptions
- Include return value descriptions
- Add examples for complex functions

### API Documentation

- Update API documentation when adding endpoints
- Include request/response examples
- Document query parameters
- Document error responses

### README Updates

- Update README for significant changes
- Add new features to features list
- Update installation instructions if needed
- Add troubleshooting tips for common issues

## 🐛 Reporting Bugs

When reporting bugs, please include:

1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: Detailed steps
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**: OS, Python version, Django version
6. **Screenshots**: If applicable
7. **Logs**: Relevant error logs

## 💡 Suggesting Features

When suggesting features:

1. **Clear Description**: What the feature should do
2. **Use Case**: Why it's needed
3. **Implementation Ideas**: How it could be implemented (optional)
4. **Examples**: Similar features in other projects

## ✅ Checklist for Pull Requests

Before submitting, ensure:

- [ ] Code follows style guidelines
- [ ] Tests are added/updated
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Commit messages follow conventions
- [ ] No merge conflicts
- [ ] Code is properly commented
- [ ] Type hints are added where appropriate

## 🙏 Thank You!

Your contributions make AIGolos better for everyone. Thank you for taking the time to contribute!

