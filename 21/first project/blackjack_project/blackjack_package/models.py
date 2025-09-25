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
