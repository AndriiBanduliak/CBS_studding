#!/bin/bash

# Скрипт для автоматического создания проекта "Blackjack"
# Включает создание структуры, файлов с кодом, README,
# и виртуального окружения.

# Название корневой папки проекта
PROJECT_DIR="blackjack_project"

echo "========================================="
echo "Начинаю создание проекта Blackjack..."
echo "========================================="

# 1. Создание структуры папок
echo "1. Создание структуры папок..."
mkdir -p "$PROJECT_DIR/blackjack_package"
echo "   - Папка '$PROJECT_DIR/' создана."
echo "   - Папка '$PROJECT_DIR/blackjack_package/' создана."
echo "Структура папок успешно создана."
echo

# 2. Создание файла __init__.py
echo "2. Создание файла blackjack_package/__init__.py..."
cat > "$PROJECT_DIR/blackjack_package/__init__.py" << 'EOF'
# Этот файл делает директорию 'blackjack_package' Python-пакетом.
# Он может быть пустым.
EOF
echo "   - Файл __init__.py создан."
echo

# 3. Создание файла models.py
echo "3. Создание файла blackjack_package/models.py с классами данных..."
cat > "$PROJECT_DIR/blackjack_package/models.py" << 'EOF'
# models.py
# Содержит классы, описывающие основные сущности игры: карты, колоды, руки игроков,
# а также перечисления для мастей и состояний игры.

import random
from enum import Enum, auto

class Suit(Enum):
    """Перечисление для представления мастей карт."""
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"

class GameState(Enum):
    """Перечисление для представления различных состояний игрового цикла."""
    BETTING = auto()      # Этап совершения ставки
    PLAYER_TURN = auto()  # Ход игрока
    DEALER_TURN = auto()  # Ход дилера
    GAME_OVER = auto()    # Игра завершена

class Card:
    """Представляет одну игральную карту с мастью, рангом и значением."""
    def __init__(self, suit: Suit, rank: str):
        self.suit = suit
        self.rank = rank
        if rank in ["J", "Q", "K"]: self.value = 10
        elif rank == "A": self.value = 11
        else: self.value = int(rank)
    
    def __str__(self) -> str:
        return f"{self.rank}{self.suit.value}"

class Deck:
    """Представляет колоду из 52 игральных карт."""
    def __init__(self):
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        self.cards = [Card(suit, rank) for suit in Suit for rank in ranks]
        self.shuffle()
    
    def shuffle(self) -> None:
        random.shuffle(self.cards)
    
    def deal(self) -> Card:
        if not self.cards:
            self.__init__()
        return self.cards.pop()

class Hand:
    """Представляет руку карт игрока или дилера."""
    def __init__(self):
        self.cards = []
    
    def add_card(self, card: Card) -> None:
        self.cards.append(card)
    
    @property
    def value(self) -> int:
        value = sum(card.value for card in self.cards)
        aces = sum(1 for card in self.cards if card.rank == "A")
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        return value
    
    def is_blackjack(self) -> bool:
        return len(self.cards) == 2 and self.value == 21
    
    def is_bust(self) -> bool:
        return self.value > 21
EOF
echo "   - Файл models.py создан."
echo

# 4. Создание файла game_logic.py
echo "4. Создание файла blackjack_package/game_logic.py с логикой игры..."
cat > "$PROJECT_DIR/blackjack_package/game_logic.py" << 'EOF'
# game_logic.py
# Содержит основной класс BlackjackGame, который инкапсулирует всю логику
# и правила игры в блэкджек.

from .models import Deck, Hand, GameState

class BlackjackGame:
    """Класс, управляющий игровым процессом в блэкджек."""
    def __init__(self):
        self.deck = Deck()
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.state = GameState.BETTING
        self.bet = 0
        self.balance = 1000
        self.result = ""
        self.payout = 0

    def start_new_game(self) -> None:
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.state = GameState.BETTING
        self.bet = 0
        self.result = ""
        self.payout = 0

    def place_bet(self, amount: int) -> bool:
        if self.state != GameState.BETTING or not (0 < amount <= self.balance):
            return False
        
        self.bet = amount
        self.balance -= amount
        
        self.player_hand.add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())
        self.player_hand.add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())
        
        if self.player_hand.is_blackjack():
            self._handle_blackjack()
        else:
            self.state = GameState.PLAYER_TURN
        
        return True

    def _handle_blackjack(self) -> None:
        if self.dealer_hand.is_blackjack():
            self.result = "Ничья - у обоих блэкджек"
            self.payout = self.bet
        else:
            self.result = "Вы выиграли с блэкджеком!"
            self.payout = int(self.bet * 2.5)
        
        self.balance += self.payout
        self.state = GameState.GAME_OVER

    def hit(self) -> bool:
        if self.state != GameState.PLAYER_TURN: return False
        self.player_hand.add_card(self.deck.deal())
        if self.player_hand.is_bust():
            self.result = "Перебор! Вы проиграли."
            self.payout = 0
            self.state = GameState.GAME_OVER
        return True

    def stand(self) -> bool:
        if self.state != GameState.PLAYER_TURN: return False
        self.state = GameState.DEALER_TURN
        self._dealer_play()
        return True

    def _dealer_play(self) -> None:
        while self.dealer_hand.value < 17:
            self.dealer_hand.add_card(self.deck.deal())
        
        if self.dealer_hand.is_bust():
            self.result = "Дилер перебрал! Вы выиграли."
            self.payout = self.bet * 2
        elif self.dealer_hand.value > self.player_hand.value:
            self.result = "Дилер выиграл."
            self.payout = 0
        elif self.dealer_hand.value < self.player_hand.value:
            self.result = "Вы выиграли!"
            self.payout = self.bet * 2
        else:
            self.result = "Ничья."
            self.payout = self.bet
        
        self.balance += self.payout
        self.state = GameState.GAME_OVER

    def double_down(self) -> bool:
        can_double = len(self.player_hand.cards) == 2 and self.balance >= self.bet
        if self.state != GameState.PLAYER_TURN or not can_double:
            return False
        
        self.balance -= self.bet
        self.bet *= 2
        self.player_hand.add_card(self.deck.deal())
        
        if self.player_hand.is_bust():
            self.result = "Перебор! Вы проиграли."
            self.payout = 0
            self.state = GameState.GAME_OVER
        else:
            self.stand()
        return True

    def get_hint(self) -> str:
        if self.state != GameState.PLAYER_TURN:
            return "Подсказка доступна только во время вашего хода."
        
        player_value = self.player_hand.value
        dealer_card = self.dealer_hand.cards[0]
        
        if player_value >= 17: return "Рекомендуется: Стоять"
        if player_value <= 8: return "Рекомендуется: Взять карту"
        if player_value == 9 and 3 <= dealer_card.value <= 6:
            return "Рекомендуется: Удвоить ставку (если нельзя, то взять карту)"
        if player_value in [10, 11] and dealer_card.value < 10:
             return "Рекомендуется: Удвоить ставку (если нельзя, то взять карту)"
        if 12 <= player_value <= 16 and 2 <= dealer_card.value <= 6:
            return "Рекомендуется: Стоять"
        return "Рекомендуется: Взять карту"
EOF
echo "   - Файл game_logic.py создан."
echo

# 5. Создание файла main.py
echo "5. Создание главного файла main.py для запуска игры..."
cat > "$PROJECT_DIR/main.py" << 'EOF'
# main.py
# Главный исполняемый файл игры.
# Отвечает за пользовательский интерфейс в консоли и управление игровым циклом.

from blackjack_package.game_logic import BlackjackGame
from blackjack_package.models import GameState

def play_game_in_console():
    """Запускает и управляет основным циклом игры в блэкджек в консоли."""
    game = BlackjackGame()
    print("Добро пожаловать в Blackjack!")
    
    while game.balance > 0:
        game.start_new_game()
        print(f"\n{'='*20}\nНОВЫЙ РАУНД\nВаш баланс: ${game.balance}")
        
        while True:
            try:
                bet_input = input("Введите вашу ставку (или 'q' для выхода): ")
                if bet_input.lower() == 'q':
                    print("Спасибо за игру!")
                    return
                bet = int(bet_input)
                if game.place_bet(bet): break
                else: print("Неверная ставка. Убедитесь, что она не превышает ваш баланс.")
            except ValueError:
                print("Пожалуйста, введите целое число.")
        
        print("\nВаши карты:", *[str(card) for card in game.player_hand.cards], sep=' ')
        print(f"Сумма: {game.player_hand.value}")
        print("\nКарта дилера:", str(game.dealer_hand.cards[0]), "[Скрытая карта]")
        
        while game.state == GameState.PLAYER_TURN:
            print(f"\nПодсказка: {game.get_hint()}")
            action = input("Выберите действие (1-Взять, 2-Стоять, 3-Удвоить): ").strip()
            
            if action == "1":
                game.hit()
                print("\nВаши карты:", *[str(card) for card in game.player_hand.cards], sep=' ')
                print(f"Сумма: {game.player_hand.value}")
            elif action == "2": game.stand()
            elif action == "3":
                if not game.double_down():
                    print("Удвоение сейчас невозможно.")
            else: print("Неверный ввод.")
        
        if game.state == GameState.GAME_OVER:
            print("\n--- РЕЗУЛЬТАТ РАУНДА ---")
            print("Карты дилера:", *[str(card) for card in game.dealer_hand.cards], sep=' ')
            print(f"Сумма дилера: {game.dealer_hand.value}")
            print(f"\n{game.result}")
            print(f"Итоговый баланс: ${game.balance}")
            
    print("\nУ вас закончились деньги! Игра окончена.")

if __name__ == "__main__":
    play_game_in_console()
EOF
echo "   - Файл main.py создан."
echo

# 6. Создание файла README.md
echo "6. Создание файла README.md..."
cat > "$PROJECT_DIR/README.md" << 'EOF'
# Проект "Blackjack" на Python

Это простая консольная реализация карточной игры Блэкджек, написанная на Python.

## О проекте

Данный проект является моей первой учебной работой, созданной в процессе обучения на курсе **"Python Developer"** в образовательной системе **CyberBionic Systematics Education System**.

Цель проекта — применить на практике базовые концепции ООП, разбить код на модули и создать работающее консольное приложение.

### Возможности игры

*   Стандартные правила Блэкджека.
*   Система ставок и баланса.
*   Возможность взять карту (Hit), остановиться (Stand) или удвоить ставку (Double Down).
*   Система подсказок по базовой стратегии.
*   Автоматическое перемешивание колоды, когда заканчиваются карты.

## Как запустить игру

1.  **Склонируйте или скачайте репозиторий.**

2.  **Перейдите в папку проекта:**
    ```sh
    cd blackjack_project
    ```

3.  **Создайте и активируйте виртуальное окружение.**
    *   Если окружение `venv` еще не создано:
        ```sh
        python -m venv venv
        ```
    *   **Активация на Windows (CMD/PowerShell):**
        ```sh
        .\venv\Scripts\activate
        ```
    *   **Активация на macOS/Linux:**
        ```sh
        source venv/bin/activate
        ```

4.  **Запустите главный файл игры:**
    ```sh
    python main.py
    ```

Приятной игры!
EOF
echo "   - Файл README.md создан."
echo

# 7. Создание виртуального окружения
echo "7. Создание виртуального окружения 'venv'..."
python -m venv "$PROJECT_DIR/venv"
echo "   - Виртуальное окружение создано в папке '$PROJECT_DIR/venv'."
echo

echo "========================================================================"
echo "Проект Blackjack успешно создан в папке '$PROJECT_DIR'!"
echo " "
echo "ЧТОБЫ НАЧАТЬ, ВЫПОЛНИТЕ СЛЕДУЮЩИЕ КОМАНДЫ:"
echo " "
echo "1. Перейдите в папку проекта:"
echo "   cd $PROJECT_DIR"
echo " "
echo "2. АКТИВИРУЙТЕ виртуальное окружение (КОМАНДА ДЛЯ WINDOWS):"
echo "   .\\venv\\Scripts\\activate"
echo " "
echo "3. Запустите игру:"
echo "   python main.py"
echo "========================================================================"