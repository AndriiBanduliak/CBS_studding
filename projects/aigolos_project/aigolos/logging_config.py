"""
Custom logging configuration to handle encoding issues on Windows.
"""

import sys
import logging
from logging import StreamHandler
import io


class SafeStreamHandler(StreamHandler):
    """
    StreamHandler that safely handles encoding errors.
    Handles Unicode characters that can't be encoded in Windows cp1251.
    """
    
    def __init__(self, stream=None):
        """Initialize handler with safe encoding."""
        if stream is None:
            stream = sys.stdout
        # Wrap stream to handle encoding
        if hasattr(stream, 'buffer') and not isinstance(stream, io.TextIOWrapper):
            # Create UTF-8 wrapper
            stream = io.TextIOWrapper(
                stream.buffer,
                encoding='utf-8',
                errors='replace',
                line_buffering=True
            )
        super().__init__(stream)
    
    def emit(self, record):
        """Emit a record, handling encoding errors gracefully."""
        try:
            msg = self.format(record)
            stream = self.stream
            
            # Try to write normally
            try:
                stream.write(msg)
                stream.write(self.terminator)
                self.flush()
            except (UnicodeEncodeError, UnicodeDecodeError):
                # If encoding fails, use safe encoding
                if hasattr(stream, 'buffer'):
                    # Write directly to buffer with UTF-8
                    safe_msg = msg.encode('utf-8', errors='replace')
                    terminator = self.terminator.encode('utf-8', errors='replace')
                    stream.buffer.write(safe_msg)
                    stream.buffer.write(terminator)
                    stream.buffer.flush()
                else:
                    # Fallback: replace problematic characters
                    safe_msg = msg.encode('ascii', errors='replace').decode('ascii')
                    stream.write(safe_msg)
                    stream.write(self.terminator)
                    self.flush()
        except Exception:
            # Last resort: ignore the log entry to prevent infinite loops
            try:
                self.handleError(record)
            except Exception:
                pass  # Completely ignore if even error handling fails

