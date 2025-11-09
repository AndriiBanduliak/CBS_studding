# Git and Pre-commit Hooks Setup

## Issues and Solutions

### Issue 1: Pre-commit Requires Git Repository

If you see error:
```
FatalError: git failed. Is it installed, and are you in a Git repository directory?
```

This means project is not initialized as Git repository. **This is normal** - pre-commit hooks are not required for project to work.

## Solutions

### Step 1: Install Dependencies

First ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

This will install all necessary packages, including `python-json-logger`, `black`, `flake8`, `isort`, `pre-commit`.

### Step 2: Setup Git and Pre-commit

### Option 1: Initialize Git Repository (Recommended)

If you want to use pre-commit hooks:

```bash
# 1. Initialize Git repository
git init

# 2. Add all files (or selectively)
git add .

# 3. Make first commit
git commit -m "Initial commit"

# 4. Now can install pre-commit hooks
pre-commit install
```

### Option 2: Use Tools Manually (Without Git)

If you don't want to use Git, you can run code quality tools manually:

```bash
# Code formatting
black .

# Import sorting
isort .

# Style checking
flake8 .

# Django check
python manage.py check
```

Or create script for automation:

```bash
# Create file format_code.bat (Windows) or format_code.sh (Linux/Mac)
black .
isort .
flake8 .
python manage.py check
```

## Verification

After installing pre-commit hooks:

```bash
# Check all files
pre-commit run --all-files

# Or just make commit - hooks will run automatically
git add .
git commit -m "Test commit"
```

## Note About export_conversation

The `export_conversation` command works correctly. Message "Conversation 1 not found" means there's no conversation with ID=1 in database. This is normal if:

1. Database is empty
2. Conversation with such ID doesn't exist
3. Conversation was deleted

To export existing conversation:

```bash
# First find ID of existing conversation
python manage.py shell
>>> from llm.models import Conversation
>>> Conversation.objects.all().values_list('id', 'title')
# Use real ID from result

# Then export
python manage.py export_conversation --conversation-id <real_id> --format markdown
```

## Alternative: Use Without Pre-commit

If you don't want to use Git, you can:

1. **Use tools manually** (see Option 2 above)
2. **Create IDE tasks** to run black, isort, flake8
3. **Use CI/CD** to check code on push

Pre-commit hooks are convenience, but not required for project to work.
