import random
from .card import Card, Rank, Suit


class Deck:
    def __init__(self):
        self.cards = self._create_deck()
        self.shuffle()

    def _create_deck(self):
        return [Card(rank, suit) for suit in Suit for rank in Rank]

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self) -> Card:
        if not self.cards:
            print("--- Reshuffling the deck ---")
            self.cards = self._create_deck()
            self.shuffle()
        return self.cards.pop()

    def __len__(self):
        return len(self.cards)