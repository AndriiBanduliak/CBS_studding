import pygame
import random
import sys
from enum import Enum
from typing import List, Tuple, Optional

# Инициализация Pygame
pygame.init()

# Константы
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# Ретро-цвета (ограниченная палитра)
BLACK = (0, 0, 0)
DARK_GREEN = (0, 100, 0)
GREEN = (0, 200, 0)
BRIGHT_GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# Начальная скорость (миллисекунды между движениями)
INITIAL_SPEED = 150
MIN_SPEED = 50  # Максимальная скорость (минимальный интервал)

# Типы бонусов
class PowerUpType(Enum):
    SPEED_UP = "speed_up"
    SPEED_DOWN = "speed_down"
    INVINCIBILITY = "invincibility"
    DOUBLE_POINTS = "double_points"
    SHRINK = "shrink"

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class PowerUp:
    def __init__(self, x: int, y: int, power_type: PowerUpType):
        self.x = x
        self.y = y
        self.type = power_type
        self.duration = 0  # Длительность эффекта в кадрах
        self.active = False
        
    def get_color(self) -> Tuple[int, int, int]:
        """Возвращает цвет бонуса в зависимости от типа"""
        colors = {
            PowerUpType.SPEED_UP: CYAN,
            PowerUpType.SPEED_DOWN: BLUE,
            PowerUpType.INVINCIBILITY: YELLOW,
            PowerUpType.DOUBLE_POINTS: MAGENTA,
            PowerUpType.SHRINK: WHITE
        }
        return colors.get(self.type, WHITE)
    
    def get_duration(self) -> int:
        """Возвращает длительность эффекта в кадрах"""
        durations = {
            PowerUpType.SPEED_UP: 300,  # 5 секунд при 60 FPS
            PowerUpType.SPEED_DOWN: 300,
            PowerUpType.INVINCIBILITY: 600,  # 10 секунд
            PowerUpType.DOUBLE_POINTS: 180,  # 3 секунды (на 3 еды)
            PowerUpType.SHRINK: 0  # Мгновенный эффект
        }
        return durations.get(self.type, 0)

class Snake:
    def __init__(self, start_x: int, start_y: int):
        self.body = [(start_x, start_y)]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.grow_pending = False
        
    def move(self):
        """Движение змейки"""
        self.direction = self.next_direction
        dx, dy = self.direction.value
        head_x, head_y = self.body[0]
        new_head = (head_x + dx, head_y + dy)
        
        self.body.insert(0, new_head)
        
        if self.grow_pending:
            self.grow_pending = False
        else:
            self.body.pop()
    
    def grow(self):
        """Увеличить змейку"""
        self.grow_pending = True
    
    def shrink(self):
        """Уменьшить змейку (но не меньше 1 сегмента)"""
        if len(self.body) > 1:
            self.body.pop()
    
    def check_collision(self) -> bool:
        """Проверка столкновения со стенами или собой"""
        head_x, head_y = self.body[0]
        
        # Столкновение со стенами
        if head_x < 0 or head_x >= GRID_WIDTH or head_y < 0 or head_y >= GRID_HEIGHT:
            return True
        
        # Столкновение с собой
        if (head_x, head_y) in self.body[1:]:
            return True
        
        return False
    
    def get_head(self) -> Tuple[int, int]:
        """Получить позицию головы"""
        return self.body[0]

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("🐍 Snake Game - Ретро")
        self.clock = pygame.time.Clock()
        
        # Инициализация игры
        self.reset_game()
        
        # Ретро-шрифт
        try:
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 36)
            self.font_small = pygame.font.Font(None, 24)
        except:
            self.font_large = pygame.font.SysFont('courier', 48)
            self.font_medium = pygame.font.SysFont('courier', 36)
            self.font_small = pygame.font.SysFont('courier', 24)
        
        # Состояние игры
        self.game_over = False
        self.paused = False
        
    def reset_game(self):
        """Сброс игры в начальное состояние"""
        self.snake = Snake(GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self.food = self.generate_food()
        self.score = 0
        self.speed = INITIAL_SPEED
        self.last_move_time = 0
        self.game_over = False
        self.paused = False
        
        # Активные бонусы
        self.active_power_ups = {}
        self.power_up_timers = {}
        
        # Бонус на поле
        self.power_up: Optional[PowerUp] = None
        self.power_up_spawn_timer = 0
        self.power_up_spawn_interval = 3000  # Появляется каждые 3 секунды
        
        # Флаги эффектов
        self.invincible = False
        self.double_points = False
        self.double_points_count = 0
        
    def generate_food(self) -> Tuple[int, int]:
        """Генерация еды в случайной позиции"""
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in self.snake.body:
                return (x, y)
    
    def spawn_power_up(self):
        """Создание бонуса на поле"""
        if self.power_up is None:
            power_types = [
                PowerUpType.SPEED_UP,
                PowerUpType.SPEED_DOWN,
                PowerUpType.INVINCIBILITY,
                PowerUpType.DOUBLE_POINTS,
                PowerUpType.SHRINK
            ]
            power_type = random.choice(power_types)
            
            while True:
                x = random.randint(0, GRID_WIDTH - 1)
                y = random.randint(0, GRID_HEIGHT - 1)
                if (x, y) not in self.snake.body and (x, y) != self.food:
                    self.power_up = PowerUp(x, y, power_type)
                    break
    
    def apply_power_up(self, power_up: PowerUp):
        """Применение эффекта бонуса"""
        if power_up.type == PowerUpType.SPEED_UP:
            self.speed = max(MIN_SPEED, self.speed - 30)
            self.active_power_ups[PowerUpType.SPEED_UP] = power_up.get_duration()
            
        elif power_up.type == PowerUpType.SPEED_DOWN:
            self.speed = min(300, self.speed + 50)
            self.active_power_ups[PowerUpType.SPEED_DOWN] = power_up.get_duration()
            
        elif power_up.type == PowerUpType.INVINCIBILITY:
            self.invincible = True
            self.active_power_ups[PowerUpType.INVINCIBILITY] = power_up.get_duration()
            
        elif power_up.type == PowerUpType.DOUBLE_POINTS:
            self.double_points = True
            self.double_points_count = 3  # На 3 еды
            self.active_power_ups[PowerUpType.DOUBLE_POINTS] = power_up.get_duration()
            
        elif power_up.type == PowerUpType.SHRINK:
            self.snake.shrink()
            # Мгновенный эффект, не добавляем в активные
    
    def update_power_ups(self):
        """Обновление активных бонусов"""
        current_time = pygame.time.get_ticks()
        
        # Обновление таймеров бонусов
        expired = []
        for power_type, duration in self.active_power_ups.items():
            self.active_power_ups[power_type] = duration - 1
            if self.active_power_ups[power_type] <= 0:
                expired.append(power_type)
        
        # Удаление истекших бонусов
        for power_type in expired:
            del self.active_power_ups[power_type]
            
            if power_type == PowerUpType.SPEED_UP:
                # Возврат скорости к нормальной (с учетом прогрессии)
                base_speed = INITIAL_SPEED - (self.score // 10) * 5
                self.speed = max(MIN_SPEED, base_speed)
                
            elif power_type == PowerUpType.SPEED_DOWN:
                # Возврат скорости к нормальной
                base_speed = INITIAL_SPEED - (self.score // 10) * 5
                self.speed = max(MIN_SPEED, base_speed)
                
            elif power_type == PowerUpType.INVINCIBILITY:
                self.invincible = False
                
            elif power_type == PowerUpType.DOUBLE_POINTS:
                self.double_points = False
                self.double_points_count = 0
    
    def handle_input(self):
        """Обработка ввода"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                
                if event.key == pygame.K_p or event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                
                if not self.paused and not self.game_over:
                    # Управление стрелками
                    if event.key == pygame.K_UP:
                        if self.snake.direction != Direction.DOWN:
                            self.snake.next_direction = Direction.UP
                    elif event.key == pygame.K_DOWN:
                        if self.snake.direction != Direction.UP:
                            self.snake.next_direction = Direction.DOWN
                    elif event.key == pygame.K_LEFT:
                        if self.snake.direction != Direction.RIGHT:
                            self.snake.next_direction = Direction.LEFT
                    elif event.key == pygame.K_RIGHT:
                        if self.snake.direction != Direction.LEFT:
                            self.snake.next_direction = Direction.RIGHT
                    
                    # Управление WASD
                    elif event.key == pygame.K_w:
                        if self.snake.direction != Direction.DOWN:
                            self.snake.next_direction = Direction.UP
                    elif event.key == pygame.K_s:
                        if self.snake.direction != Direction.UP:
                            self.snake.next_direction = Direction.DOWN
                    elif event.key == pygame.K_a:
                        if self.snake.direction != Direction.RIGHT:
                            self.snake.next_direction = Direction.LEFT
                    elif event.key == pygame.K_d:
                        if self.snake.direction != Direction.LEFT:
                            self.snake.next_direction = Direction.RIGHT
        
        return True
    
    def update(self):
        """Обновление игровой логики"""
        if self.paused or self.game_over:
            return
        
        current_time = pygame.time.get_ticks()
        
        # Движение змейки с учетом скорости
        if current_time - self.last_move_time >= self.speed:
            self.snake.move()
            self.last_move_time = current_time
            
            # Проверка столкновений (если не неуязвим)
            if not self.invincible and self.snake.check_collision():
                self.game_over = True
                return
            
            # Проверка поедания еды
            if self.snake.get_head() == self.food:
                self.snake.grow()
                points = 10
                if self.double_points and self.double_points_count > 0:
                    points *= 2
                    self.double_points_count -= 1
                    if self.double_points_count <= 0:
                        self.double_points = False
                
                self.score += points
                
                # Нарастающая сложность: увеличение скорости каждые 10 очков
                new_speed = INITIAL_SPEED - (self.score // 10) * 5
                if PowerUpType.SPEED_UP not in self.active_power_ups and \
                   PowerUpType.SPEED_DOWN not in self.active_power_ups:
                    self.speed = max(MIN_SPEED, new_speed)
                
                self.food = self.generate_food()
            
            # Проверка поедания бонуса
            if self.power_up and self.snake.get_head() == (self.power_up.x, self.power_up.y):
                self.apply_power_up(self.power_up)
                self.power_up = None
                self.power_up_spawn_timer = 0
        
        # Обновление бонусов
        self.update_power_ups()
        
        # Спавн бонусов
        if current_time - self.power_up_spawn_timer >= self.power_up_spawn_interval:
            if self.power_up is None:
                self.spawn_power_up()
            self.power_up_spawn_timer = current_time
    
    def draw_grid(self):
        """Отрисовка сетки в ретро-стиле"""
        for x in range(0, WINDOW_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, DARK_GRAY, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, DARK_GRAY, (0, y), (WINDOW_WIDTH, y))
    
    def draw_snake(self):
        """Отрисовка змейки в ретро-стиле"""
        for i, (x, y) in enumerate(self.snake.body):
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            
            # Голова ярче
            if i == 0:
                if self.invincible:
                    # Мерцание при неуязвимости
                    if (pygame.time.get_ticks() // 100) % 2:
                        pygame.draw.rect(self.screen, YELLOW, rect)
                    else:
                        pygame.draw.rect(self.screen, BRIGHT_GREEN, rect)
                else:
                    pygame.draw.rect(self.screen, BRIGHT_GREEN, rect)
                # Глаза
                eye_size = 3
                eye_offset = 5
                pygame.draw.circle(self.screen, BLACK, 
                                 (x * GRID_SIZE + eye_offset, y * GRID_SIZE + eye_offset), 
                                 eye_size)
                pygame.draw.circle(self.screen, BLACK, 
                                 (x * GRID_SIZE + GRID_SIZE - eye_offset, 
                                  y * GRID_SIZE + eye_offset), 
                                 eye_size)
            else:
                # Тело с градиентом
                color_intensity = max(100, 200 - i * 2)
                color = (0, color_intensity, 0)
                pygame.draw.rect(self.screen, color, rect)
            
            # Ретро-граница
            pygame.draw.rect(self.screen, DARK_GREEN, rect, 1)
    
    def draw_food(self):
        """Отрисовка еды в ретро-стиле"""
        x, y = self.food
        rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(self.screen, RED, rect)
        # Ретро-эффект: внутренний квадрат
        inner_rect = pygame.Rect(x * GRID_SIZE + 4, y * GRID_SIZE + 4, 
                                GRID_SIZE - 8, GRID_SIZE - 8)
        pygame.draw.rect(self.screen, YELLOW, inner_rect)
    
    def draw_power_up(self):
        """Отрисовка бонуса"""
        if self.power_up:
            x, y = self.power_up.x, self.power_up.y
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            color = self.power_up.get_color()
            
            # Мерцание для привлечения внимания
            if (pygame.time.get_ticks() // 200) % 2:
                pygame.draw.rect(self.screen, color, rect)
            else:
                pygame.draw.rect(self.screen, BLACK, rect)
                pygame.draw.rect(self.screen, color, rect, 2)
    
    def draw_ui(self):
        """Отрисовка UI в ретро-стиле"""
        # Фон для текста
        score_text = self.font_medium.render(f"ОЧКИ: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Отображение активных бонусов
        y_offset = 50
        for power_type in self.active_power_ups:
            duration = self.active_power_ups[power_type]
            seconds = duration // 60
            
            power_names = {
                PowerUpType.SPEED_UP: "УСКОРЕНИЕ",
                PowerUpType.SPEED_DOWN: "ЗАМЕДЛЕНИЕ",
                PowerUpType.INVINCIBILITY: "НЕУЯЗВИМОСТЬ",
                PowerUpType.DOUBLE_POINTS: "x2 ОЧКИ"
            }
            
            name = power_names.get(power_type, "")
            if name:
                power_text = self.font_small.render(f"{name}: {seconds}с", True, YELLOW)
                self.screen.blit(power_text, (10, y_offset))
                y_offset += 25
        
        # Двойные очки (если активны)
        if self.double_points:
            dp_text = self.font_small.render(f"x2 ОЧКИ: {self.double_points_count} еды", True, MAGENTA)
            self.screen.blit(dp_text, (10, y_offset))
    
    def draw_game_over(self):
        """Отрисовка экрана окончания игры"""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.font_large.render("ИГРА ОКОНЧЕНА", True, RED)
        score_text = self.font_medium.render(f"Финальный счет: {self.score}", True, WHITE)
        restart_text = self.font_small.render("Нажмите R для перезапуска", True, YELLOW)
        
        text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60))
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40))
        
        self.screen.blit(game_over_text, text_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(restart_text, restart_rect)
    
    def draw_pause(self):
        """Отрисовка экрана паузы"""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(120)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.font_large.render("ПАУЗА", True, YELLOW)
        continue_text = self.font_small.render("Нажмите P или ПРОБЕЛ для продолжения", True, WHITE)
        
        text_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20))
        continue_rect = continue_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
        
        self.screen.blit(pause_text, text_rect)
        self.screen.blit(continue_text, continue_rect)
    
    def draw(self):
        """Отрисовка всего игрового экрана"""
        self.screen.fill(BLACK)
        self.draw_grid()
        self.draw_food()
        if self.power_up:
            self.draw_power_up()
        self.draw_snake()
        self.draw_ui()
        
        if self.game_over:
            self.draw_game_over()
        elif self.paused:
            self.draw_pause()
        
        pygame.display.flip()
    
    def run(self):
        """Главный игровой цикл"""
        running = True
        
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS для плавности
        
        pygame.quit()
        sys.exit()

def main():
    """Точка входа"""
    game = SnakeGame()
    game.run()

if __name__ == "__main__":
    main()

