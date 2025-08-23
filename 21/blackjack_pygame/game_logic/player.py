# game_logic/player.py (ВИПРАВЛЕНА ВЕРСІЯ)

from abc import ABC, abstractmethod
from .card import Card, Rank


class AbstractPlayer(ABC):
    # 1. Правильний конструктор __init__
    def __init__(self):
        self.hand = []
        self.is_busted = False

    # 2. Всі ці методи мають відступ, тобто вони всередині класу
    def add_card(self, card: Card):
        self.hand.append(card)
        if self.get_hand_value() > 21:
            self.is_busted = True

    def get_hand_value(self) -> int:
        value = sum(card.value for card in self.hand)
        num_aces = sum(1 for card in self.hand if card.rank == Rank.ACE)

        while value > 21 and num_aces > 0:
            value -= 10
            num_aces -= 1
        return value

    def clear_hand(self):
        self.hand = []
        self.is_busted = False

    @abstractmethod
    def __str__(self):
        pass


class Player(AbstractPlayer):
    # Правильний конструктор __init__
    def __init__(self, name="Гравець"):
        super().__init__()
        self.name = name

    # Метод з відступом
    def __str__(self):
        return self.name


class Dealer(AbstractPlayer):
    # Правильний конструктор __init__
    def __init__(self):
        super().__init__()
        self.name = "Дилер"
        self.hide_first_card = True

    # Метод з відступом
    def should_hit(self) -> bool:
        return self.get_hand_value() < 17
    
    # Метод з відступом
    def __str__(self):
        return self.name