"""
Application entry point for the Blackjack web application.
"""
from blackjack import create_app
from blackjack.logger import logger

app = create_app()

if __name__ == '__main__':
    logger.info("Starting Blackjack application")
    app.run(debug=True, host='0.0.0.0', port=5000)