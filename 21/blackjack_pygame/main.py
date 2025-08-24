import pygame
import os
import sys

# Імпортуємо класи з наших модулів
from game_logic.deck import Deck
from game_logic.player import Player, Dealer
from ui.components import Button, Text, DARK_GREEN, WHITE, BLACK, GREEN, RED

# --- КОНСТАНТИ ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Динамічне визначення шляхів до ресурсів
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()

ASSETS_DIR = os.path.join(BASE_DIR, 'ui', 'assets')
CARD_DIR = os.path.join(ASSETS_DIR, 'cards')
OTHER_DIR = os.path.join(ASSETS_DIR, 'other') # Папка для фону
FONT_PATH = None

CARD_WIDTH, CARD_HEIGHT = 100, 150


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("BlackJack на Pygame")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = "START"

        # ** НОВЕ: Змінні для історії ігор **
        self.player_wins = 0
        self.player_losses = 0
        
        # Ініціалізація ігрових об'єктів
        self.deck = Deck()
        self.player = Player()
        self.dealer = Dealer()

        # Ресурси
        self.card_images = self._load_card_images()
        self.card_back = self._load_safe_image(os.path.join(CARD_DIR, 'card_back.png'), (CARD_WIDTH, CARD_HEIGHT))
        
        # ** НОВЕ: Завантаження фонового зображення **
        background_path = os.path.join(OTHER_DIR, 'background.jpg') # Переконайтесь, що файл існує
        try:
            self.background_image = pygame.image.load(background_path).convert()
            self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except pygame.error:
            print(f"Помилка: не вдалося завантажити фон '{background_path}'. Використовується суцільний колір.")
            self.background_image = None # Якщо фону немає, будемо використовувати колір

        # Створюємо елементи UI
        self._setup_ui()

    def _load_safe_image(self, path, size):
        """Безпечно завантажує зображення або створює заглушку."""
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, size)
        except pygame.error:
            print(f"Помилка: не вдалося завантажити '{path}'.")
            surface = pygame.Surface(size)
            surface.fill(RED)
            return surface

    def _load_card_images(self):
        images = {}
        for suit in ['clubs', 'diamonds', 'hearts', 'spades']:
            for rank in ['02', '03', '04', '05', '06', '07', '08', '09', '10', 'J', 'Q', 'K', 'A']:
                file_name = f"card_{suit}_{rank}.png"
                path = os.path.join(CARD_DIR, file_name)
                images[file_name] = self._load_safe_image(path, (CARD_WIDTH, CARD_HEIGHT))
        return images

    def _setup_ui(self):
        button_width, button_height = 180, 50
        y_pos = SCREEN_HEIGHT - 60
        x_center = SCREEN_WIDTH / 2

        self.hit_btn = Button((x_center - 200, y_pos), (button_width, button_height), GREEN, "Взяти ще (Hit)", WHITE, 24, FONT_PATH)
        self.stand_btn = Button((x_center, y_pos), (button_width, button_height), RED, "Зупинитись (Stand)", WHITE, 24, FONT_PATH)
        self.new_game_btn = Button((x_center + 200, y_pos), (button_width, button_height), DARK_GREEN, "Нова гра", WHITE, 24, FONT_PATH)
        
        self.hit_btn.disable()
        self.stand_btn.disable()
        
        self.status_text = Text("Вітаємо у BlackJack! Натисніть 'Нова гра'.", 32, WHITE, (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2), FONT_PATH)
        self.dealer_score_text = Text("Дилер: ?", 28, WHITE, (SCREEN_WIDTH / 2, 50), FONT_PATH)
        self.player_score_text = Text("Гравець: 0", 28, WHITE, (SCREEN_WIDTH / 2, SCREEN_HEIGHT - 120), FONT_PATH)

        # ** НОВЕ: Текст для історії ігор **
        self.history_text = Text(
            f"Перемоги: {self.player_wins} | Поразки: {self.player_losses}", 22, WHITE,
            (150, 30), FONT_PATH
        )

    def _start_new_round(self):
        self.player.clear_hand()
        self.dealer.clear_hand()
        
        if len(self.deck) < 15: self.deck = Deck()

        self.player.add_card(self.deck.deal())
        self.dealer.add_card(self.deck.deal())
        self.player.add_card(self.deck.deal())
        self.dealer.add_card(self.deck.deal())
        
        self.dealer.hide_first_card = True
        self.game_state = "PLAYER_TURN"
        self.status_text.update_text("Ваш хід. Взяти ще карту чи зупинитись?")
        
        self.hit_btn.enable()
        self.stand_btn.enable()
        self.new_game_btn.disable()

        if self.player.get_hand_value() == 21:
            self.game_state = "DEALER_TURN"

    def _player_hit(self):
        if self.game_state != "PLAYER_TURN": return
        self.player.add_card(self.deck.deal())
        if self.player.is_busted:
            self.game_state = "END"
            self.check_winner()

    def _player_stand(self):
        if self.game_state != "PLAYER_TURN": return
        self.game_state = "DEALER_TURN"
        self.dealer.hide_first_card = False

    def _dealer_turn(self):
        if self.dealer.should_hit():
            self.dealer.add_card(self.deck.deal())
            if self.dealer.is_busted:
                self.game_state = "END"
        else:
            self.game_state = "END"
        
        if self.game_state == "END":
            self.check_winner()

    def check_winner(self):
        self.dealer.hide_first_card = False
        player_score = self.player.get_hand_value()
        dealer_score = self.dealer.get_hand_value()
        message = ""

        if self.player.is_busted:
            message = f"Перебір! {player_score}. Ви програли."
            self.player_losses += 1 # ** ОНОВЛЕННЯ ІСТОРІЇ **
        elif self.dealer.is_busted:
            message = f"Дилер перебрав! {dealer_score}. Ви виграли!"
            self.player_wins += 1 # ** ОНОВЛЕННЯ ІСТОРІЇ **
        elif player_score > dealer_score:
            message = f"Ви виграли! {player_score} проти {dealer_score}."
            self.player_wins += 1 # ** ОНОВЛЕННЯ ІСТОРІЇ **
        elif player_score < dealer_score:
            message = f"Ви програли. {player_score} проти {dealer_score}."
            self.player_losses += 1 # ** ОНОВЛЕННЯ ІСТОРІЇ **
        else:
            message = f"Нічия! {player_score} на {player_score}."
            
        self.status_text.update_text(message)
        
        # ** ОНОВЛЕННЯ ІСТОРІЇ **
        self.history_text.update_text(f"Перемоги: {self.player_wins} | Поразки: {self.player_losses}")
        
        self.hit_btn.disable()
        self.stand_btn.disable()
        self.new_game_btn.enable()

    def _draw_hand(self, player_obj, y_pos):
        card_spacing = 40
        num_cards = len(player_obj.hand)
        hand_width = CARD_WIDTH + (num_cards - 1) * card_spacing
        start_x = (SCREEN_WIDTH - hand_width) / 2
        
        for i, card in enumerate(player_obj.hand):
            x = start_x + i * card_spacing
            if isinstance(player_obj, Dealer) and i == 0 and player_obj.hide_first_card:
                self.screen.blit(self.card_back, (x, y_pos))
            else:
                self.screen.blit(self.card_images[card.image_name], (x, y_pos))

    def _update_and_draw_scores(self):
        player_score = self.player.get_hand_value()
        self.player_score_text.update_text(f"Гравець: {player_score}")

        dealer_score = "?" if self.dealer.hide_first_card else self.dealer.get_hand_value()
        self.dealer_score_text.update_text(f"Дилер: {dealer_score}")
        
        self.dealer_score_text.draw(self.screen)
        self.player_score_text.draw(self.screen)
        
    def _draw_all(self):
        # ** ОНОВЛЕННЯ: Малюємо фон **
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            self.screen.fill(DARK_GREEN) # Залишаємо колір, якщо фон не завантажився

        self._draw_hand(self.dealer, 100)
        self._draw_hand(self.player, SCREEN_HEIGHT - 100 - CARD_HEIGHT)
        self._update_and_draw_scores()
        
        self.hit_btn.draw(self.screen)
        self.stand_btn.draw(self.screen)
        self.new_game_btn.draw(self.screen)
        self.status_text.draw(self.screen)
        self.history_text.draw(self.screen) # ** Малюємо історію **
        
        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                if self.new_game_btn.is_clicked(event) and self.game_state in ["START", "END"]: self._start_new_round()
                if self.hit_btn.is_clicked(event): self._player_hit()
                if self.stand_btn.is_clicked(event): self._player_stand()

            if self.game_state == "DEALER_TURN":
                pygame.time.wait(700)
                self._dealer_turn()
            
            self._draw_all()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()