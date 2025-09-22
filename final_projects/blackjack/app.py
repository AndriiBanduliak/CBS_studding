from blackjack import create_app
from blackjack.logger import logger

app = create_app()

if __name__ == '__main__':
    logger.info("Запуск приложения BlackJack")
    app.run(debug=True)