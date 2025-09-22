import random
from enum import Enum

class Suit(Enum):
    HEARTS = "hearts"
    DIAMONDS = "diamonds"
    CLUBS = "clubs"
    SPADES = "spades"

class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        self.is_face_up = True
    
    def __repr__(self):
        return f"{self.value} of {self.suit.value}"
    
    def get_display_value(self):
        if not self.is_face_up:
            return "Hidden"
        if self.value == 1:
            return "Ace"
        elif self.value == 11:
            return "Jack"
        elif self.value == 12:
            return "Queen"
        elif self.value == 13:
            return "King"
        else:
            return str(self.value)
    
    def get_blackjack_value(self):
        if not self.is_face_up:
            return 0
        if self.value == 1:
            return 11  # Ace is initially 11, can be reduced to 1 if needed
        elif self.value >= 10:
            return 10  # Face cards are worth 10
        else:
            return self.value
    
    def flip(self):
        self.is_face_up = not self.is_face_up
        return self

class Deck:
    def __init__(self):
        self.cards = []
        self.reset()
    
    def reset(self):
        self.cards = []
        for suit in Suit:
            for value in range(1, 14):  # 1=Ace, 11=Jack, 12=Queen, 13=King
                self.cards.append(Card(suit, value))
        self.shuffle()
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def deal(self):
        if not self.cards:
            self.reset()
        return self.cards.pop()

class Hand:
    def __init__(self):
        self.cards = []
    
    def add_card(self, card):
        self.cards.append(card)
        return self
    
    def get_value(self):
        value = 0
        aces = 0
        
        for card in self.cards:
            card_value = card.get_blackjack_value()
            if card_value == 11:
                aces += 1
            value += card_value
        
        # Adjust for aces if needed
        while value > 21 and aces > 0:
            value -= 10  # Convert an ace from 11 to 1
            aces -= 1
            
        return value
    
    def is_blackjack(self):
        return len(self.cards) == 2 and self.get_value() == 21
    
    def is_busted(self):
        return self.get_value() > 21
    
    def clear(self):
        self.cards = []

class GameState(Enum):
    BETTING = "betting"
    PLAYER_TURN = "player_turn"
    DEALER_TURN = "dealer_turn"
    GAME_OVER = "game_over"

class BlackjackGame:
    def __init__(self):
        self.deck = Deck()
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.state = GameState.BETTING
        self.bet = 0
        self.result = None
        self.payout = 0
    
    def place_bet(self, amount):
        if self.state != GameState.BETTING:
            return False
        
        self.bet = amount
        self.deal_initial_cards()
        self.state = GameState.PLAYER_TURN
        
        # Check for blackjack
        if self.player_hand.is_blackjack():
            return self.end_round()
        
        return True
    
    def deal_initial_cards(self):
        self.player_hand.clear()
        self.dealer_hand.clear()
        
        # Deal two cards to player and dealer
        self.player_hand.add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())
        self.player_hand.add_card(self.deck.deal())
        
        # Dealer's second card is face down
        dealer_card = self.deck.deal()
        dealer_card.is_face_up = False
        self.dealer_hand.add_card(dealer_card)
    
    def hit(self):
        if self.state != GameState.PLAYER_TURN:
            return False
        
        self.player_hand.add_card(self.deck.deal())
        
        if self.player_hand.is_busted():
            return self.end_round()
        
        return True
    
    def stand(self):
        if self.state != GameState.PLAYER_TURN:
            return False
        
        self.state = GameState.DEALER_TURN
        
        # Flip dealer's face-down card
        for card in self.dealer_hand.cards:
            card.is_face_up = True
        
        # Dealer hits until 17 or higher
        while self.dealer_hand.get_value() < 17:
            self.dealer_hand.add_card(self.deck.deal())
        
        return self.end_round()
    
    def double_down(self):
        if self.state != GameState.PLAYER_TURN or len(self.player_hand.cards) != 2:
            return False
        
        self.bet *= 2
        self.player_hand.add_card(self.deck.deal())
        
        if self.player_hand.is_busted():
            return self.end_round()
        
        return self.stand()
    
    def split(self):
        # Not implemented for simplicity
        # Would create a second hand and split the cards
        pass
    
    def end_round(self):
        self.state = GameState.GAME_OVER
        
        player_value = self.player_hand.get_value()
        dealer_value = self.dealer_hand.get_value()
        
        # Determine the result
        if self.player_hand.is_busted():
            self.result = "Player busts"
            self.payout = -self.bet
        elif self.player_hand.is_blackjack() and not self.dealer_hand.is_blackjack():
            self.result = "Blackjack!"
            self.payout = int(self.bet * 1.5)  # Blackjack pays 3:2
        elif self.dealer_hand.is_busted():
            self.result = "Dealer busts"
            self.payout = self.bet
        elif self.dealer_hand.is_blackjack() and not self.player_hand.is_blackjack():
            self.result = "Dealer blackjack"
            self.payout = -self.bet
        elif player_value > dealer_value:
            self.result = "Player wins"
            self.payout = self.bet
        elif dealer_value > player_value:
            self.result = "Dealer wins"
            self.payout = -self.bet
        else:
            self.result = "Push"
            self.payout = 0
        
        return True
    
    def get_hint(self):
        """
        Provides a hint based on basic blackjack strategy.
        """
        if self.state != GameState.PLAYER_TURN:
            return None
        
        player_value = self.player_hand.get_value()
        dealer_upcard_value = self.dealer_hand.cards[0].get_blackjack_value()
        
        # Check for pairs
        if len(self.player_hand.cards) == 2 and self.player_hand.cards[0].get_blackjack_value() == self.player_hand.cards[1].get_blackjack_value():
            card_value = self.player_hand.cards[0].get_blackjack_value()
            
            # Pair strategy
            if card_value in [8, 11]:  # Aces or 8s
                return "Split"
            elif card_value in [10, 5]:  # 10s or 5s
                return "Stand"
            elif card_value == 9 and dealer_upcard_value not in [7, 10, 11]:
                return "Split"
            elif card_value in [2, 3, 7] and dealer_upcard_value <= 7:
                return "Split"
            elif card_value in [4, 6] and dealer_upcard_value in [2, 3, 4, 5, 6]:
                return "Split"
        
        # Check for soft hands (hand with an Ace counted as 11)
        has_ace = any(card.value == 1 for card in self.player_hand.cards)
        if has_ace and player_value <= 21:
            # Soft hand strategy
            if player_value >= 19:
                return "Stand"
            elif player_value == 18:
                if dealer_upcard_value in [2, 7, 8]:
                    return "Stand"
                elif dealer_upcard_value in [9, 10, 11]:
                    return "Hit"
                else:  # 3-6
                    return "Double down if possible, otherwise stand"
            elif player_value == 17:
                if dealer_upcard_value in [3, 4, 5, 6]:
                    return "Double down if possible, otherwise hit"
                else:
                    return "Hit"
            else:  # Soft 13-16
                if dealer_upcard_value in [4, 5, 6]:
                    return "Double down if possible, otherwise hit"
                else:
                    return "Hit"
        
        # Hard hand strategy
        if player_value >= 17:
            return "Stand"
        elif player_value >= 13:
            if dealer_upcard_value in [2, 3, 4, 5, 6]:
                return "Stand"
            else:
                return "Hit"
        elif player_value == 12:
            if dealer_upcard_value in [4, 5, 6]:
                return "Stand"
            else:
                return "Hit"
        elif player_value == 11:
            return "Double down if possible, otherwise hit"
        elif player_value == 10:
            if dealer_upcard_value in [2, 3, 4, 5, 6, 7, 8, 9]:
                return "Double down if possible, otherwise hit"
            else:
                return "Hit"
        elif player_value == 9:
            if dealer_upcard_value in [3, 4, 5, 6]:
                return "Double down if possible, otherwise hit"
            else:
                return "Hit"
        else:  # 5-8
            return "Hit"
    
    def reset(self):
        self.player_hand.clear()
        self.dealer_hand.clear()
        self.state = GameState.BETTING
        self.bet = 0
        self.result = None
        self.payout = 0