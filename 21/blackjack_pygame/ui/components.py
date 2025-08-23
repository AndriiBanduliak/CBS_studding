# ui/components.py

import pygame

# --- Constants ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GREEN = (0, 100, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
GREY = (128, 128, 128)


class Text:
    """Клас для створення та відображення тексту."""
    def __init__(self, text, font_size, color, position, font_path=None):
        self.text = text
        self.color = color
        self.position = position
        try:
            self.font = pygame.font.Font(font_path, font_size)
        except FileNotFoundError:
            print(f"Warning: Font file not found at {font_path}. Using default font.")
            self.font = pygame.font.Font(None, font_size)

        self.image = self.font.render(self.text, True, self.color)
        self.rect = self.image.get_rect(center=self.position)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def update_text(self, new_text):
        """Оновлює текст та перераховує позицію."""
        self.text = new_text
        self.image = self.font.render(self.text, True, self.color)
        self.rect = self.image.get_rect(center=self.position)


class Button:
    """Клас для створення кнопок з текстом."""
    def __init__(self, position, size, bg_color, text, text_color, font_size, font_path=None):
        self.rect = pygame.Rect((0, 0), size)
        self.rect.center = position
        self.bg_color = bg_color

        self.text = Text(
            text=text,
            font_size=font_size,
            color=text_color,
            position=self.rect.center,
            font_path=font_path
        )
        self.is_enabled = True

    def draw(self, surface):
        """Малює кнопку на поверхні."""
        color = self.bg_color if self.is_enabled else GREY
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        self.text.draw(surface)

    def is_clicked(self, event) -> bool:
        """Перевіряє, чи була кнопка натиснута."""
        if not self.is_enabled:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def enable(self):
        """Робить кнопку активною."""
        self.is_enabled = True

    def disable(self):
        """Робить кнопку неактивною."""
        self.is_enabled = False