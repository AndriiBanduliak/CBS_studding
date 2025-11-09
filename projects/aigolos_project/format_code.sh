#!/bin/bash
# Script for formatting code without pre-commit hooks
# Usage: ./format_code.sh

echo "Formatting code with black..."
black .

echo "Sorting imports with isort..."
isort .

echo "Checking code style with flake8..."
flake8 . --max-line-length=100 --extend-ignore=E203,W503 || echo "Flake8 found some issues (non-critical)"

echo "Running Django checks..."
python manage.py check

echo "Done!"

