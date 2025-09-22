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
        self.assertEqual(Card(Suit.HEARTS, "2").value, 2)
        self.assertEqual(Card(Suit.DIAMONDS, "10").value, 10)
        
        # Test face cards
        self.assertEqual(Card(Suit.CLUBS, "J").value, 10)
        self.assertEqual(Card(Suit.SPADES, "Q").value, 10)
        self.assertEqual(Card(Suit.HEARTS, "K").value, 10)
        
        # Test ace
        self.assertEqual(Card(Suit.DIAMONDS, "A").value, 11)
    
    def test_hand_value(self):
        """Test that hand values are calculated correctly"""
        # Test regular hand
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, "10"))
        hand.add_card(Card(Suit.DIAMONDS, "5"))
        self.assertEqual(hand.value, 15)
        
        # Test hand with ace counted as 11
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, "A"))
        hand.add_card(Card(Suit.DIAMONDS, "5"))
        self.assertEqual(hand.value, 16)
        
        # Test hand with ace counted as 1 to avoid bust
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, "A"))
        hand.add_card(Card(Suit.DIAMONDS, "5"))
        hand.add_card(Card(Suit.CLUBS, "10"))
        self.assertEqual(hand.value, 16)
    
    def test_blackjack(self):
        """Test blackjack detection"""
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, "A"))
        hand.add_card(Card(Suit.DIAMONDS, "K"))
        self.assertTrue(hand.is_blackjack())
        
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, "10"))
        hand.add_card(Card(Suit.DIAMONDS, "A"))
        self.assertTrue(hand.is_blackjack())
        
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, "10"))
        hand.add_card(Card(Suit.DIAMONDS, "9"))
        self.assertFalse(hand.is_blackjack())
    
    def test_bust(self):
        """Test bust detection"""
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, "10"))
        hand.add_card(Card(Suit.DIAMONDS, "10"))
        hand.add_card(Card(Suit.CLUBS, "5"))
        self.assertTrue(hand.is_bust())
        
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, "10"))
        hand.add_card(Card(Suit.DIAMONDS, "9"))
        self.assertFalse(hand.is_bust())
    
    def test_game_flow(self):
        """Test basic game flow"""
        # Start a new game
        self.game.start_new_game()
        self.assertEqual(self.game.state, GameState.BETTING)
        
        # Place a bet
        self.game.place_bet(50)
        self.assertEqual(self.game.state, GameState.PLAYER_TURN)
        self.assertEqual(len(self.game.player_hand.cards), 2)
        self.assertEqual(len(self.game.dealer_hand.cards), 2)
        
        # Player stands
        initial_player_value = self.game.player_hand.value
        self.game.stand()
        self.assertIn(self.game.state, [GameState.DEALER_TURN, GameState.GAME_OVER])
        
        # If game is over, check that results are determined
        if self.game.state == GameState.GAME_OVER:
            self.assertIsNotNone(self.game.result)

if __name__ == '__main__':
    unittest.main()