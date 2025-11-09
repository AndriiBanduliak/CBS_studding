import unittest
import sys
import os

# Add the parent directory to the path so we can import the blackjack module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from blackjack.game.blackjack import Card, Deck, Hand, BlackjackGame, Suit, GameState

class TestBlackjackGame(unittest.TestCase):
    def setUp(self):
        self.game = BlackjackGame()
    
    def test_deck_creation(self):
        """Test that a deck has 52 cards"""
        deck = Deck()
        self.assertEqual(len(deck.cards), 52)
    
    def test_card_values(self):
        """Test that card values are calculated correctly"""
        # Test number cards
        card = Card(Suit.HEARTS, 2)
        self.assertEqual(card.value, 2)
        self.assertEqual(card.get_blackjack_value(), 2)
        
        card = Card(Suit.DIAMONDS, 10)
        self.assertEqual(card.value, 10)
        self.assertEqual(card.get_blackjack_value(), 10)
        
        # Test face cards (Jack=11, Queen=12, King=13)
        card = Card(Suit.CLUBS, 11)
        self.assertEqual(card.value, 11)
        self.assertEqual(card.get_blackjack_value(), 10)
        
        card = Card(Suit.SPADES, 12)
        self.assertEqual(card.value, 12)
        self.assertEqual(card.get_blackjack_value(), 10)
        
        card = Card(Suit.HEARTS, 13)
        self.assertEqual(card.value, 13)
        self.assertEqual(card.get_blackjack_value(), 10)
        
        # Test ace
        card = Card(Suit.DIAMONDS, 1)
        self.assertEqual(card.value, 1)
        self.assertEqual(card.get_blackjack_value(), 11)
    
    def test_hand_value(self):
        """Test that hand values are calculated correctly"""
        # Test regular hand
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, 10))
        hand.add_card(Card(Suit.DIAMONDS, 5))
        self.assertEqual(hand.get_value(), 15)
        
        # Test hand with ace counted as 11
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, 1))  # Ace
        hand.add_card(Card(Suit.DIAMONDS, 5))
        self.assertEqual(hand.get_value(), 16)
        
        # Test hand with ace counted as 1 to avoid bust
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, 1))  # Ace
        hand.add_card(Card(Suit.DIAMONDS, 5))
        hand.add_card(Card(Suit.CLUBS, 10))
        self.assertEqual(hand.get_value(), 16)
    
    def test_blackjack(self):
        """Test blackjack detection"""
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, 1))  # Ace
        hand.add_card(Card(Suit.DIAMONDS, 13))  # King
        self.assertTrue(hand.is_blackjack())
        
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, 10))
        hand.add_card(Card(Suit.DIAMONDS, 1))  # Ace
        self.assertTrue(hand.is_blackjack())
        
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, 10))
        hand.add_card(Card(Suit.DIAMONDS, 9))
        self.assertFalse(hand.is_blackjack())
    
    def test_bust(self):
        """Test bust detection"""
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, 10))
        hand.add_card(Card(Suit.DIAMONDS, 10))
        hand.add_card(Card(Suit.CLUBS, 5))
        self.assertTrue(hand.is_busted())
        
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, 10))
        hand.add_card(Card(Suit.DIAMONDS, 9))
        self.assertFalse(hand.is_busted())
    
    def test_game_flow(self):
        """Test basic game flow"""
        # Check initial state
        self.assertEqual(self.game.state, GameState.BETTING)
        
        # Place a bet
        result = self.game.place_bet(50)
        self.assertTrue(result)
        self.assertEqual(self.game.state, GameState.PLAYER_TURN)
        self.assertEqual(len(self.game.player_hand.cards), 2)
        self.assertEqual(len(self.game.dealer_hand.cards), 2)
        
        # Player stands
        self.game.stand()
        self.assertEqual(self.game.state, GameState.GAME_OVER)
        self.assertIsNotNone(self.game.result)

if __name__ == '__main__':
    unittest.main()