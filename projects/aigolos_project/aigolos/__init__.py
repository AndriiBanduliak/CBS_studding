"""
AIGolos project package initialization.
Fixes encoding issues on Windows before Django loads.
"""

import sys
import io
import os

# Fix encoding issues on Windows BEFORE Django loads
if sys.platform == 'win32':
    # Set UTF-8 encoding for stdout/stderr
    if hasattr(sys.stdout, 'buffer') and not isinstance(sys.stdout, io.TextIOWrapper):
        try:
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer,
                encoding='utf-8',
                errors='replace',
                line_buffering=True
            )
        except (AttributeError, ValueError):
            pass  # Ignore if can't wrap
    
    if hasattr(sys.stderr, 'buffer') and not isinstance(sys.stderr, io.TextIOWrapper):
        try:
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer,
                encoding='utf-8',
                errors='replace',
                line_buffering=True
            )
        except (AttributeError, ValueError):
            pass  # Ignore if can't wrap
    
    # Set console code page to UTF-8
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleOutputCP(65001)  # UTF-8
    except Exception:
        pass  # Ignore if fails
    
    # Set environment variable
    os.environ['PYTHONIOENCODING'] = 'utf-8'
