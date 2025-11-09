#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# Force Python UTF-8 mode for all operations including C extensions
os.environ['PYTHONUTF8'] = '1'

# Fix for Windows encoding issues with PostgreSQL (must be set before Django loads)
os.environ.setdefault('PGPASSFILE', 'nul')
os.environ.setdefault('PGSERVICEFILE', 'nul')
os.environ.setdefault('PGSYSCONFDIR', 'nul')
os.environ['PGCLIENTENCODING'] = 'UTF8'

# Temporarily override APPDATA to prevent libpq from reading from user profile with non-ASCII chars
# Store original for later restoration if needed
_original_appdata = os.environ.get('APPDATA')
os.environ['APPDATA'] = os.environ.get('TEMP', 'C:\\Windows\\Temp')


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'law_crm.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

