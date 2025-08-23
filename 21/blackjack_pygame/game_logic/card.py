from enum import Enum
from collections import namedtuple

CardData = namedtuple("CardData", ["rank", "suit", "value"])


class Suit(Enum):
    # Використовуємо маленькі літери, щоб відповідати іменам файлів
    HEARTS = "hearts"
    DIAMONDS = "diamonds"
    CLUBS = "clubs"
    SPADES = "spades"


class Rank(Enum):
    # Значення відповідають частині імені файлу
    TWO = "02"
    THREE = "03"
    FOUR = "04"
    FIVE = "05"
    SIX = "06"
    SEVEN = "07"
    EIGHT = "08"
    NINE = "09"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"


class Card:
    VALUES = {
        Rank.TWO: 2, Rank.THREE: 3, Rank.FOUR: 4, Rank.FIVE: 5, Rank.SIX: 6,
        Rank.SEVEN: 7, Rank.EIGHT: 8, Rank.NINE: 9, Rank.TEN: 10,
        Rank.JACK: 10, Rank.QUEEN: 10, Rank.KING: 10, Rank.ACE: 11
    }

    def __init__(self, rank: Rank, suit: Suit):
        if not isinstance(rank, Rank) or not isinstance(suit, Suit):
            raise TypeError("Invalid type for rank or suit")

        self.rank = rank
        self.suit = suit
        self.value = self.VALUES[rank]
        
        # Нова логіка для генерації імені файлу, що відповідає вашим ассетам
        # Приклад: card_ + hearts + _ + K + .png -> card_hearts_K.png
        self.image_name = f"card_{self.suit.value}_{self.rank.value}.png"

    def __str__(self):
        # Цей текст для виводу в консоль, можна залишити як є
        full_rank_name = self.rank.name.title()
        return f"{full_rank_name} of {self.suit.value.title()}"

    def __repr__(self):
        return self.__str__()