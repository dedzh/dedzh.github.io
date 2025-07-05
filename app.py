import pygame
import random
import time

# Яркие, насыщенные цвета для фигур
BRIGHT_COLORS = [
    (0, 0, 0),        # Черный (фон)
    (255, 50, 50),    # Ярко-красный
    (50, 255, 50),    # Ярко-зеленый
    (50, 50, 255),    # Ярко-синий
    (255, 255, 50),   # Ярко-желтый
    (255, 50, 255),   # Ярко-розовый
    (50, 255, 255),   # Ярко-голубой
    (255, 150, 50),   # Оранжевый
]

# Дополнительные цвета интерфейса
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GRAY = (40, 40, 60)
GRID_COLOR = (80, 80, 100)
HIGHLIGHT_COLOR = (200, 200, 220)
PANEL_COLOR = (30, 30, 40)

# Фигуры тетрамино в формате [x, y]
FIGURES = [
    # I-тетрамино
    [[(0, 1), (1, 1), (2, 1), (3, 1)], 
     [(1, 0), (1, 1), (1, 2), (1, 3)]],
    
    # Z-тетрамино
    [[(0, 0), (1, 0), (1, 1), (2, 1)], 
     [(0, 1), (0, 2), (1, 0), (1, 1)]],
    
    # S-тетрамино
    [[(0, 1), (1, 1), (1, 0), (2, 0)], 
     [(0, 0), (0, 1), (1, 1), (1, 2)]],
    
    # J-тетрамино
    [[(0, 0), (0, 1), (1, 1), (2, 1)], 
     [(1, 0), (1, 1), (1, 2), (0, 2)], 
     [(0, 1), (1, 1), (2, 1), (2, 2)], 
     [(0, 0), (1, 0), (1, 1), (1, 2)]],
    
    # L-тетрамино
    [[(0, 1), (1, 1), (2, 1), (2, 0)], 
     [(1, 0), (1, 1), (1, 2), (2, 2)], 
     [(0, 2), (0, 1), (1, 1), (2, 1)], 
     [(0, 0), (1, 0), (1, 1), (1, 2)]],
    
    # T-тетрамино
    [[(0, 1), (1, 1), (2, 1), (1, 0)], 
     [(1, 0), (1, 1), (1, 2), (0, 1)], 
     [(0, 1), (1, 1), (2, 1), (1, 2)], 
     [(1, 0), (1, 1), (1, 2), (2, 1)]],
    
    # O-тетрамино
    [[(0, 0), (0, 1), (1, 0), (1, 1)]]
]

class Figure:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.randint(0, len(FIGURES) - 1)
        self.color_idx = random.randint(1, len(BRIGHT_COLORS) - 1)
        self.rotation = 0
    
    @property
    def blocks(self):
        """Возвращает текущие координаты блоков фигуры"""
        return [(self.x + bx, self.y + by) 
                for bx, by in FIGURES[self.type][self.rotation]]
    
    def rotate(self):
        """Вращает фигуру"""
        new_rotation = (self.rotation + 1) % len(FIGURES[self.type])
        self.rotation = new_rotation

class TetrisGame:
    def __init__(self, grid_width=12, grid_height=22):  #  размер игрового поля
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.reset_game()
        
        # Параметры отрисовки
        self.zoom =25
        self.x_offset = 50  # Сдвиг влево для расширения поля
        self.y_offset = 40
        
    def reset_game(self):
        """Сбрасывает состояние игры"""
        self.level = 1
        self.score = 0
        self.lines_cleared = 0
        self.state = "playing"
        self.field = [[0 for _ in range(self.grid_width)] 
                     for _ in range(self.grid_height)]
        self.figure = self.new_figure()
        self.next_figure = self.new_figure()
        self.last_drop_time = time.time()
        self.drop_delay = 0.5  # секунд
        self.last_move_down = 0
    
    def new_figure(self):
        """Создает новую фигуру"""
        return Figure(self.grid_width // 2 - 1, 0)
    
    def is_valid_position(self, figure=None):
        """Проверяет, может ли фигура находиться в текущей позиции"""
        figure = figure or self.figure
        for x, y in figure.blocks:
            # Проверка выхода за границы
            if x < 0 or x >= self.grid_width or y >= self.grid_height:
                return False
            # Проверка столкновения с другими фигурами
            if y >= 0 and self.field[y][x]:
                return False
        return True
    
    def merge_figure(self):
        """Фиксирует фигуру на игровом поле"""
        for x, y in self.figure.blocks:
            if y >= 0:  # Игнорируем блоки выше поля
                self.field[y][x] = self.figure.color_idx
        
        self.clear_lines()
        self.figure = self.next_figure
        self.next_figure = self.new_figure()
        
        # Проверка конца игры
        if not self.is_valid_position():
            self.state = "gameover"
    
    def clear_lines(self):
        """Удаляет заполненные линии и обновляет счет"""
        lines_cleared = 0
        for y in range(self.grid_height - 1, -1, -1):
            if all(self.field[y]):
                lines_cleared += 1
                # Сдвигаем все линии выше вниз
                for y2 in range(y, 0, -1):
                    self.field[y2] = self.field[y2 - 1][:]
                self.field[0] = [0] * self.grid_width
        
        # Обновление счета
        if lines_cleared:
            self.lines_cleared += lines_cleared
            base_score = {1: 100, 2: 300, 3: 700, 4: 1500}[lines_cleared]
            self.score += base_score * self.level
            self.level = max(1, min(15, self.lines_cleared // 10 + 1))
            # Увеличиваем скорость с уровнем
            self.drop_delay = max(0.05, 0.5 - (self.level - 1) * 0.03)
    
    def move(self, dx, dy):
        """Пытается переместить фигуру"""
        new_figure = Figure(self.figure.x, self.figure.y)
        new_figure.type = self.figure.type
        new_figure.rotation = self.figure.rotation
        new_figure.x += dx
        new_figure.y += dy
        
        if self.is_valid_position(new_figure):
            self.figure.x = new_figure.x
            self.figure.y = new_figure.y
            return True
        return False
    
    def rotate_figure(self):
        """Пытается повернуть фигуру"""
        original_rotation = self.figure.rotation
        self.figure.rotate()
        if not self.is_valid_position():
            # Откат при неудаче
            self.figure.rotation = original_rotation
            return False
        return True
    
    def hard_drop(self):
        """Мгновенное падение фигуры"""
        drop_count = 0
        while self.move(0, 1):
            drop_count += 1
        
        # Бонус за ускоренное падение
        self.score += drop_count * 2
        self.merge_figure()
    
    def soft_drop(self):
        """Ускоренное падение фигуры при удержании клавиши"""
        self.move(0, 1)
        # Небольшой бонус за ускоренное падение
        self.score += 1

def draw_block(surface, color, x, y, size):
    """Рисует один блок с эффектом объема"""
    # Основной цвет
    pygame.draw.rect(surface, color, 
                    (x + 1, y + 1, size - 2, size - 2))
    
    # Светлый оттенок сверху/слева для 3D-эффекта
    pygame.draw.line(surface, 
                   (min(255, color[0] + 100), 
                    min(255, color[1] + 100), 
                    min(255, color[2] + 100)),
                   (x, y), (x + size - 1, y), 2)
    pygame.draw.line(surface, 
                   (min(255, color[0] + 100), 
                    min(255, color[1] + 100), 
                    min(255, color[2] + 100)),
                   (x, y), (x, y + size - 1), 2)
    
    # Темный оттенок снизу/справа для 3D-эффекта
    pygame.draw.line(surface, 
                   (max(0, color[0] - 80), 
                    max(0, color[1] - 80), 
                    max(0, color[2] - 80)),
                   (x, y + size - 1), (x + size - 1, y + size - 1), 2)
    pygame.draw.line(surface, 
                   (max(0, color[0] - 80), 
                    max(0, color[1] - 80), 
                    max(0, color[2] - 80)),
                   (x + size - 1, y), (x + size - 1, y + size - 1), 2)

def draw_grid(surface, game):
    """Отрисовывает игровое поле"""
    # Фон поля
    pygame.draw.rect(surface, BLACK, 
                    (game.x_offset, game.y_offset, 
                     game.zoom * game.grid_width, 
                     game.zoom * game.grid_height))
    
    # Сетка
    for y in range(game.grid_height):
        for x in range(game.grid_width):
            pygame.draw.rect(surface, GRID_COLOR, 
                            (game.x_offset + x * game.zoom, 
                             game.y_offset + y * game.zoom, 
                             game.zoom, game.zoom), 1)
            
            # Заполненные ячейки
            if game.field[y][x]:
                draw_block(surface, BRIGHT_COLORS[game.field[y][x]], 
                         game.x_offset + x * game.zoom, 
                         game.y_offset + y * game.zoom, 
                         game.zoom)
    
    # Текущая фигура
    if game.figure:
        for x, y in game.figure.blocks:
            if y >= 0:  # Не рисуем выше поля
                draw_block(surface, BRIGHT_COLORS[game.figure.color_idx], 
                         game.x_offset + x * game.zoom, 
                         game.y_offset + y * game.zoom, 
                         game.zoom)
    
    # Предварительный просмотр позиции фигуры
    if game.figure and game.state == "playing":
        ghost = Figure(game.figure.x, game.figure.y)
        ghost.type = game.figure.type
        ghost.rotation = game.figure.rotation
        ghost.color_idx = game.figure.color_idx
        
        while game.is_valid_position(ghost):
            ghost.y += 1
        ghost.y -= 1
        
        for x, y in ghost.blocks:
            if y >= 0:
                pygame.draw.rect(surface, BRIGHT_COLORS[ghost.color_idx], 
                               (game.x_offset + x * game.zoom + 3, 
                                game.y_offset + y * game.zoom + 3, 
                                game.zoom - 6, game.zoom - 6), 1)

def draw_ui(surface, game):
    """Отрисовывает интерфейс"""
    # Панель информации справа
    panel_width = 400
    panel_x = game.x_offset + game.grid_width * game.zoom + 20
    panel_height = game.grid_height * game.zoom
    
    # Рамка панели
    pygame.draw.rect(surface, PANEL_COLOR, 
                   (panel_x, game.y_offset, panel_width, panel_height))
    pygame.draw.rect(surface, HIGHLIGHT_COLOR, 
                   (panel_x, game.y_offset, panel_width, panel_height), 2)
    
    # Текст счета
    font = pygame.font.SysFont('Arial', 15, bold=True)
    font_small = pygame.font.SysFont('Arial', 10)
    
    score_text = font.render(f"SCORE", True, WHITE)
    score_value = font.render(f"{game.score}", True, (255, 215, 0))
    level_text = font.render(f"LEVEL", True, WHITE)
    level_value = font.render(f"{game.level}", True, (100, 255, 255))
    lines_text = font.render(f"LINES", True, WHITE)
    lines_value = font.render(f"{game.lines_cleared}", True, (100, 255, 100))
    
    # Размещение текста на панели
    surface.blit(score_text, [panel_x + 10, game.y_offset + 20])
    surface.blit(score_value, [panel_x + 20, game.y_offset + 50])
    surface.blit(level_text, [panel_x + 10, game.y_offset + 100])
    surface.blit(level_value, [panel_x + 20, game.y_offset + 130])
    surface.blit(lines_text, [panel_x + 10, game.y_offset + 180])
    surface.blit(lines_value, [panel_x + 20, game.y_offset + 210])
    
    # Разделительная линия
    pygame.draw.line(surface, HIGHLIGHT_COLOR, 
                   (panel_x, game.y_offset + 250), 
                   (panel_x + panel_width, game.y_offset + 250), 2)
    
    # Предварительный просмотр следующей фигуры
    next_text = font.render("NEXT", True, WHITE)
    surface.blit(next_text, [panel_x + 10, game.y_offset + 260])
    
    if game.next_figure:
        # Центрируем фигуру в панели
        min_x = min(x for x, y in game.next_figure.blocks)
        max_x = max(x for x, y in game.next_figure.blocks)
        center_x = (min_x + max_x) / 2
        
        for x, y in game.next_figure.blocks:
            # Сдвигаем фигуру в центр панели
            draw_block(surface, BRIGHT_COLORS[game.next_figure.color_idx], 
                     panel_x + 80 + (x - center_x) * game.zoom, 
                     game.y_offset + 340 + y * game.zoom, 
                     game.zoom)
    
    # Разделительная линия
    pygame.draw.line(surface, HIGHLIGHT_COLOR, 
                   (panel_x, game.y_offset + 400), 
                   (panel_x + panel_width, game.y_offset + 400), 2)
    
    # Управление
    controls_text = font.render("CONTROLS", True, WHITE)
    surface.blit(controls_text, [panel_x + 10, game.y_offset + 410])
    
    controls = [
        "← → : Move    ↑ : Rotate",
        "↓ : Soft Drop    SPACE : Hard Drop",
        "R : Restart"
    ]
    
    for i, text in enumerate(controls):
        ctrl = font_small.render(text, True, (200, 200, 255))
        surface.blit(ctrl, [panel_x + 20, game.y_offset + 450 + i * 30])
    
    # Сообщение о конце игры
    if game.state == "gameover":
        # Затемнение экрана
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        font_large = pygame.font.SysFont('Arial', 50, bold=True)
        game_over = font_large.render("GAME OVER", True, (255, 100, 100))
        restart = font.render("Press R to restart", True, WHITE)
        
        surface.blit(game_over, [game.x_offset + 20, game.y_offset + 200])
        surface.blit(restart, [game.x_offset + 70, game.y_offset + 270])

def main():
    # Инициализация игры
    pygame.init()
    # Увеличили ширину окна для информационной панели
    screen = pygame.display.set_mode((800, 650))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    
    game = TetrisGame()
    
    # Основной игровой цикл
    running = True
    fast_drop = False
    
    while running:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if game.state == "playing":
                    if event.key == pygame.K_UP:
                        game.rotate_figure()
                    elif event.key == pygame.K_LEFT:
                        game.move(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        game.move(1, 0)
                    elif event.key == pygame.K_DOWN:
                        fast_drop = True
                    elif event.key == pygame.K_SPACE:
                        game.hard_drop()
                
                # Рестарт в любое время
                if event.key == pygame.K_r:
                    game.reset_game()
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    fast_drop = False
        
        # Игровая логика
        if game.state == "playing":
            # Автоматическое падение фигуры
            current_time = time.time()
            drop_interval = game.drop_delay / 5 if fast_drop else game.drop_delay
            
            if current_time - game.last_drop_time > drop_interval:
                if fast_drop:
                    game.soft_drop()
                    game.last_drop_time = current_time
                else:
                    if not game.move(0, 1):
                        game.merge_figure()
                    game.last_drop_time = current_time
        
        # Отрисовка
        screen.fill(DARK_GRAY)
        draw_grid(screen, game)
        draw_ui(screen, game)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()