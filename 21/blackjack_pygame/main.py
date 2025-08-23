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

# Динамічне визначення шляхів до ресурсів, щоб скрипт працював з будь-якого місця
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()

ASSETS_DIR = os.path.join(BASE_DIR, 'ui', 'assets')
CARD_DIR = os.path.join(ASSETS_DIR, 'cards')
FONT_PATH = None  # Використовуємо стандартний шрифт Pygame

CARD_WIDTH, CARD_HEIGHT = 100, 150 # Розміри карт


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("BlackJack на Pygame")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = "START"  # Можливі стани: START, PLAYER_TURN, DEALER_TURN, END
        
        # Ініціалізація ігрових об'єктів (Композиція)
        self.deck = Deck()
        self.player = Player()
        self.dealer = Dealer()

        # Ресурси
        self.card_images = self._load_card_images()
        try:
            self.card_back = pygame.image.load(os.path.join(CARD_DIR, 'card_back.png')).convert_alpha()
            self.card_back = pygame.transform.scale(self.card_back, (CARD_WIDTH, CARD_HEIGHT))
        except pygame.error:
            print("Помилка: не вдалося завантажити 'card_back.png'. Перевірте шлях та файл.")
            self.card_back = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
            self.card_back.fill(RED) # Заглушка, якщо зображення відсутнє

        # Створюємо елементи UI
        self._setup_ui()

    def _load_card_images(self):
        """Завантажує та масштабує всі зображення карт."""
        images = {}
        # Проходимо по всіх можливих іменах файлів, які генерує наш клас Card
        for suit in ['clubs', 'diamonds', 'hearts', 'spades']:
            for rank in ['02', '03', '04', '05', '06', '07', '08', '09', '10', 'J', 'Q', 'K', 'A']:
                file_name = f"card_{suit}_{rank}.png"
                try:
                    path = os.path.join(CARD_DIR, file_name)
                    img = pygame.image.load(path).convert_alpha()
                    img = pygame.transform.scale(img, (CARD_WIDTH, CARD_HEIGHT))
                    images[file_name] = img
                except pygame.error:
                    print(f"Помилка: не вдалося завантажити зображення '{file_name}'")
        return images

    def _setup_ui(self):
        """Створює кнопки та текстові елементи для гри."""
        button_width, button_height = 180, 50
        y_pos = SCREEN_HEIGHT - 60
        x_center = SCREEN_WIDTH / 2

        self.hit_btn = Button(
            (x_center - 200, y_pos), (button_width, button_height), GREEN, 
            "Взяти ще (Hit)", WHITE, 24, FONT_PATH
        )
        self.stand_btn = Button(
            (x_center, y_pos), (button_width, button_height), RED, 
            "Зупинитись (Stand)", WHITE, 24, FONT_PATH
        )
        self.new_game_btn = Button(
            (x_center + 200, y_pos), (button_width, button_height), DARK_GREEN, 
            "Нова гра", WHITE, 24, FONT_PATH
        )
        
        # --- Налаштування початкового стану кнопок ---
        self.hit_btn.disable()
        self.stand_btn.disable()
        # Кнопка "New Game" активна на старті, щоб почати гру
        
        self.status_text = Text(
            "Вітаємо у BlackJack! Натисніть 'Нова гра' для початку.", 32, WHITE, 
            (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2), FONT_PATH
        )
        
        self.dealer_score_text = Text("Дилер: ?", 28, WHITE, (SCREEN_WIDTH / 2, 50), FONT_PATH)
        self.player_score_text = Text("Гравець: 0", 28, WHITE, (SCREEN_WIDTH / 2, SCREEN_HEIGHT - 120), FONT_PATH)

    def _start_new_round(self):
        """Скидає стан гри та роздає початкові карти."""
        self.player.clear_hand()
        self.dealer.clear_hand()
        
        # Якщо в колоді мало карт, створюємо нову
        if len(self.deck) < 15:
            self.deck = Deck()

        # Початкова роздача: по 2 карти гравцю та дилеру
        self.player.add_card(self.deck.deal())
        self.dealer.add_card(self.deck.deal())
        self.player.add_card(self.deck.deal())
        self.dealer.add_card(self.deck.deal())
        
        self.dealer.hide_first_card = True
        self.game_state = "PLAYER_TURN"
        self.status_text.update_text("Ваш хід. Взяти ще карту чи зупинитись?")
        
        # Оновлюємо стан кнопок для гри
        self.hit_btn.enable()
        self.stand_btn.enable()
        self.new_game_btn.disable()

        # Миттєва перевірка на BlackJack у гравця
        if self.player.get_hand_value() == 21:
            self.game_state = "DEALER_TURN" # Переходимо одразу до ходу дилера

    def _player_hit(self):
        """Гравець бере карту."""
        if self.game_state != "PLAYER_TURN": return
        
        self.player.add_card(self.deck.deal())
        
        if self.player.is_busted:
            self.game_state = "END"
            self.check_winner()

    def _player_stand(self):
        """Гравець зупиняється, хід переходить до дилера."""
        if self.game_state != "PLAYER_TURN": return
        
        self.game_state = "DEALER_TURN"
        self.dealer.hide_first_card = False

    def _dealer_turn(self):
        """Логіка ходу дилера."""
        if self.dealer.should_hit():
            self.dealer.add_card(self.deck.deal())
            # Якщо дилер перебрав, гра закінчується
            if self.dealer.is_busted:
                self.game_state = "END"
        else:
            # Дилер зупиняється
            self.game_state = "END"
        
        # Після кожного ходу дилера перевіряємо, чи не закінчилась гра
        if self.game_state == "END":
            self.check_winner()

    def check_winner(self):
        """Визначає переможця та оновлює повідомлення."""
        self.dealer.hide_first_card = False # Показуємо карту дилера в кінці
        player_score = self.player.get_hand_value()
        dealer_score = self.dealer.get_hand_value()
        message = ""

        if self.player.is_busted:
            message = f"Перебір! {player_score}. Ви програли."
        elif self.dealer.is_busted:
            message = f"Дилер перебрав! {dealer_score}. Ви виграли!"
        elif player_score > dealer_score:
            message = f"Ви виграли! {player_score} проти {dealer_score}."
        elif player_score < dealer_score:
            message = f"Ви програли. {player_score} проти {dealer_score}."
        else:
            message = f"Нічия! {player_score} на {player_score}."
            
        self.status_text.update_text(message)
        
        # Готуємо UI до нової гри
        self.hit_btn.disable()
        self.stand_btn.disable()
        self.new_game_btn.enable()

    def _draw_hand(self, player_obj, y_pos):
        """Малює карти для вказаного гравця."""
        card_spacing = 40
        num_cards = len(player_obj.hand)
        hand_width = CARD_WIDTH + (num_cards - 1) * card_spacing
        start_x = (SCREEN_WIDTH - hand_width) / 2
        
        for i, card in enumerate(player_obj.hand):
            x = start_x + i * card_spacing
            
            if isinstance(player_obj, Dealer) and i == 0 and player_obj.hide_first_card:
                self.screen.blit(self.card_back, (x, y_pos))
            else:
                card_img = self.card_images.get(card.image_name)
                if card_img:
                    self.screen.blit(card_img, (x, y_pos))

    def _update_and_draw_scores(self):
        """Оновлює та малює рахунки гравців."""
        player_score = self.player.get_hand_value()
        self.player_score_text.update_text(f"Гравець: {player_score}")

        if self.dealer.hide_first_card:
            dealer_score = "?"
        else:
            dealer_score = self.dealer.get_hand_value()
        self.dealer_score_text.update_text(f"Дилер: {dealer_score}")
        
        self.dealer_score_text.draw(self.screen)
        self.player_score_text.draw(self.screen)
        
    def _draw_all(self):
        """Малює всі елементи на екрані."""
        self.screen.fill(DARK_GREEN)
        self._draw_hand(self.dealer, 100)
        self._draw_hand(self.player, SCREEN_HEIGHT - 100 - CARD_HEIGHT)
        self._update_and_draw_scores()
        
        # Малюємо кнопки та статусний текст
        self.hit_btn.draw(self.screen)
        self.stand_btn.draw(self.screen)
        self.new_game_btn.draw(self.screen)
        self.status_text.draw(self.screen)
        
        pygame.display.flip()

    def run(self):
        """Головний цикл гри."""
        while self.running:
            self.clock.tick(FPS)
            
            # --- Обробка подій ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                # Обробка кліків по кнопках залежно від стану гри
                if self.new_game_btn.is_clicked(event):
                    if self.game_state in ["START", "END"]:
                        self._start_new_round()
                
                if self.hit_btn.is_clicked(event):
                    self._player_hit()

                if self.stand_btn.is_clicked(event):
                    self._player_stand()

            # --- Ігрова логіка, що залежить від стану ---
            if self.game_state == "DEALER_TURN":
                pygame.time.wait(700) # Штучна затримка для імітації "роздумів" дилера
                self._dealer_turn()
            
            # --- Рендеринг ---
            self._draw_all()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()