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
