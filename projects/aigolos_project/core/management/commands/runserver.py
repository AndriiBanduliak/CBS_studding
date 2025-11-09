"""
Custom runserver command that logs startup message.
"""
import logging
import sys
from django.core.management.commands.runserver import Command as BaseCommand

logger = logging.getLogger('aigolos')


class Command(BaseCommand):
    """
    Custom runserver command that logs the startup message.
    """
    
    def add_arguments(self, parser):
        """Add command arguments."""
        super().add_arguments(parser)
    
    def handle(self, *args, **options):
        """Handle the command with logging."""
        # Parse address and port from args or options
        addrport = None
        if args:
            addrport = args[0]
        else:
            addrport = options.get('addrport', '8000')
        
        # Parse addrport like Django does
        if isinstance(addrport, str):
            if ':' in addrport:
                host, port = addrport.split(':', 1)
            else:
                host = '127.0.0.1'
                port = addrport
        else:
            host = '127.0.0.1'
            port = str(addrport)
        
        # Log startup message BEFORE calling parent
        protocol = 'http'
        startup_msg = f"Starting development server at {protocol}://{host}:{port}/"
        quit_msg = "Quit the server with CTRL-BREAK."
        
        # Force flush to ensure message appears immediately
        logger.info(startup_msg)
        logger.info(quit_msg)
        
        # Also print to stdout for immediate visibility (force flush)
        self.stdout.write(startup_msg)
        self.stdout.write(quit_msg)
        sys.stdout.flush()
        
        # Call parent command (it will also print to stdout)
        result = super().handle(*args, **options)
        return result

