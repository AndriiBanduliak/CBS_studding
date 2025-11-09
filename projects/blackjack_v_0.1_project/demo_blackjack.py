import random
from enum import Enum, auto

class Suit(Enum):
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"

class GameState(Enum):
    BETTING = auto()
    PLAYER_TURN = auto()
    DEALER_TURN = auto()
    GAME_OVER = auto()

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        
        if rank in ["J", "Q", "K"]:
            self.value = 10
        elif rank == "A":
            self.value = 11
        else:
            self.value = int(rank)
    
    def __str__(self):
        return f"{self.rank}{self.suit.value}"

class Deck:
    def __init__(self):
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        self.cards = [Card(suit, rank) for suit in Suit for rank in ranks]
        self.shuffle()
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def deal(self):
        if not self.cards:
            self.__init__()
        return self.cards.pop()

class Hand:
    def __init__(self):
        self.cards = []
    
    def add_card(self, card):
        self.cards.append(card)
    
    @property
    def value(self):
        value = sum(card.value for card in self.cards)
        # Если сумма больше 21 и есть тузы, считаем их за 1
        aces = sum(1 for card in self.cards if card.rank == "A")
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        return value
    
    def is_blackjack(self):
        return len(self.cards) == 2 and self.value == 21
    
    def is_bust(self):
        return self.value > 21

class BlackjackGame:
    def __init__(self):
        self.deck = Deck()
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.state = GameState.BETTING
        self.bet = 0
        self.balance = 1000
        self.result = None
        self.payout = 0
    
    def start_new_game(self):
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.state = GameState.BETTING
        self.bet = 0
        self.result = None
        self.payout = 0
    
    def place_bet(self, amount):
        if self.state != GameState.BETTING:
            return False
        
        if amount > self.balance:
            return False
        
        self.bet = amount
        self.balance -= amount
        
        # Раздаем начальные карты
        self.player_hand.add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())
        self.player_hand.add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())
        
        # Проверяем на блэкджек
        if self.player_hand.is_blackjack():
            if self.dealer_hand.is_blackjack():
                self.result = "Ничья - у обоих блэкджек"
                self.payout = self.bet
                self.balance += self.payout
            else:
                self.result = "Вы выиграли с блэкджеком!"
                self.payout = int(self.bet * 2.5)
                self.balance += self.payout
            self.state = GameState.GAME_OVER
        else:
            self.state = GameState.PLAYER_TURN
        
        return True
    
    def hit(self):
        if self.state != GameState.PLAYER_TURN:
            return False
        
        self.player_hand.add_card(self.deck.deal())
        
        if self.player_hand.is_bust():
            self.result = "Перебор! Вы проиграли."
            self.payout = 0
            self.state = GameState.GAME_OVER
        
        return True
    
    def stand(self):
        if self.state != GameState.PLAYER_TURN:
            return False
        
        self.state = GameState.DEALER_TURN
        
        # Дилер берет карты, пока не наберет 17 или больше
        while self.dealer_hand.value < 17:
            self.dealer_hand.add_card(self.deck.deal())
        
        # Определяем результат
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
        return True
    
    def double_down(self):
        if self.state != GameState.PLAYER_TURN or len(self.player_hand.cards) > 2:
            return False
        
        if self.bet > self.balance:
            return False
        
        self.balance -= self.bet
        self.bet *= 2
        
        # Берем одну карту и завершаем ход
        self.player_hand.add_card(self.deck.deal())
        
        if self.player_hand.is_bust():
            self.result = "Перебор! Вы проиграли."
            self.payout = 0
            self.state = GameState.GAME_OVER
        else:
            self.stand()
        
        return True
    
    def get_hint(self):
        if self.state != GameState.PLAYER_TURN:
            return "Ожидайте следующую игру"
        
        player_value = self.player_hand.value
        dealer_card = self.dealer_hand.cards[0]
        
        # Базовая стратегия
        if player_value >= 17:
            return "Рекомендуется: Стоять"
        elif player_value <= 8:
            return "Рекомендуется: Взять карту"
        elif player_value == 9:
            if dealer_card.value >= 3 and dealer_card.value <= 6:
                return "Рекомендуется: Удвоить ставку (если нельзя, то взять карту)"
            else:
                return "Рекомендуется: Взять карту"
        elif player_value == 10 or player_value == 11:
            if dealer_card.value < 10:
                return "Рекомендуется: Удвоить ставку (если нельзя, то взять карту)"
            else:
                return "Рекомендуется: Взять карту"
        elif player_value >= 12 and player_value <= 16:
            if dealer_card.value >= 2 and dealer_card.value <= 6:
                return "Рекомендуется: Стоять"
            else:
                return "Рекомендуется: Взять карту"
        
        return "Рекомендуется: Взять карту"

def play_demo_game():
    game = BlackjackGame()
    print("Добро пожаловать в Blackjack!")
    print(f"Ваш баланс: ${game.balance}")
    
    while True:
        game.start_new_game()
        
        # Делаем ставку
        while True:
            try:
                bet = int(input(f"\nВаш баланс: ${game.balance}. Введите вашу ставку (0 для выхода): "))
                if bet == 0:
                    print("Спасибо за игру!")
                    return
                if game.place_bet(bet):
                    break
                else:
                    print("Неверная ставка. Попробуйте снова.")
            except ValueError:
                print("Пожалуйста, введите число.")
        
        # Показываем начальные карты
        print("\nВаши карты:")
        for card in game.player_hand.cards:
            print(f"  {card}")
        print(f"Сумма: {game.player_hand.value}")
        
        print("\nКарта дилера:")
        print(f"  {game.dealer_hand.cards[0]}")
        print(f"  [Скрытая карта]")
        
        # Если игра не закончилась сразу (блэкджек)
        while game.state == GameState.PLAYER_TURN:
            hint = game.get_hint()
            print(f"\n{hint}")
            
            action = input("\nВыберите действие (1-Взять карту, 2-Стоять, 3-Удвоить ставку, 4-Подсказка): ")
            
            if action == "1":
                game.hit()
                print("\nВаши карты:")
                for card in game.player_hand.cards:
                    print(f"  {card}")
                print(f"Сумма: {game.player_hand.value}")
            elif action == "2":
                game.stand()
            elif action == "3":
                if game.double_down():
                    print("\nСтавка удвоена!")
                    print("\nВаши карты:")
                    for card in game.player_hand.cards:
                        print(f"  {card}")
                    print(f"Сумма: {game.player_hand.value}")
                else:
                    print("Удвоение невозможно.")
            elif action == "4":
                print(f"\n{hint}")
            else:
                print("Неверный ввод. Попробуйте снова.")
        
        # Показываем карты дилера и результат
        if game.state == GameState.GAME_OVER:
            print("\nКарты дилера:")
            for card in game.dealer_hand.cards:
                print(f"  {card}")
            print(f"Сумма: {game.dealer_hand.value}")
            
            print(f"\n{game.result}")
            print(f"Выигрыш: ${game.payout}")
            print(f"Новый баланс: ${game.balance}")
            
            if game.balance <= 0:
                print("\nУ вас закончились деньги! Игра окончена.")
                return
            
            play_again = input("\nСыграть еще раз? (y/n): ")
            if play_again.lower() != "y":
                print("Спасибо за игру!")
                return

if __name__ == "__main__":
    play_demo_game()