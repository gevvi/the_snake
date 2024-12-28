from abc import abstractmethod
from random import randint
import pygame
from typing import List, Tuple, Optional

# Константы для размеров поля и сетки:
SCREEN_WIDTH: int = 640
SCREEN_HEIGHT: int = 480
GRID_SIZE: int = 20
GRID_WIDTH: int = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT: int = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP: Tuple[int, int] = (0, -1)
DOWN: Tuple[int, int] = (0, 1)
LEFT: Tuple[int, int] = (-1, 0)
RIGHT: Tuple[int, int] = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR: Tuple[int, int, int] = (0, 0, 0)

# Стандартный цвет объектов:
DEFAULT_COLOR: Tuple[int, int, int] = (255, 255, 255)

# Цвет границы ячейки
BORDER_COLOR: Tuple[int, int, int] = (93, 216, 228)

# Цвет яблока
APPLE_COLOR: Tuple[int, int, int] = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR: Tuple[int, int, int] = (0, 255, 0)

# Скорость движения змейки:
SPEED: int = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock: pygame.time.Clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для объектов."""

    def __init__(self, position: Tuple[int, int] = (0, 0),
                 body_color: Tuple[int, int, int] = DEFAULT_COLOR) -> None:
        self.position: Tuple[int, int] = position
        self.body_color: Tuple[int, int, int] = body_color

    @abstractmethod
    def draw(self) -> None:
        raise NotImplementedError(
        )


class Snake(GameObject):
    """Класс, описывающий змейку"""

    def __init__(self) -> None:
        super().__init__((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), SNAKE_COLOR)
        self.speed: int = SPEED
        self.paused: bool = False
        self.game_over: bool = False
        self.direction: Tuple[int, int] = RIGHT
        self.next_direction: Optional[Tuple[int, int]] = None
        self.length: int = 1
        self.positions: List[Tuple[int, int]] = [self.position]
        self.last: Optional[Tuple[int, int]] = None

    def update_direction(self) -> None:
        """Обновление направления после нажатия кнопки"""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def is_game_over(self, next_position: Tuple[int, int]) -> None:
        """Проверка, чтобы змейка не врезалась в свой хвост"""
        if next_position in self.positions[2:]:
            self.game_over = True

    def move(self) -> Tuple[int, int]:
        """Вычисляем новое положение змейки"""
        self.update_direction()
        x, y = self.position
        dx, dy = self.direction
        new_x = (x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_y = (y + dy * GRID_SIZE) % SCREEN_HEIGHT
        next_position = (new_x, new_y)
        return next_position

    def insert_next_position(self, next_position: Tuple[int, int]) -> None:
        """Установка змейки в новое положение"""
        self.position = next_position
        self.positions.insert(0, self.position)

    def del_last_segment(self) -> None:
        """Удаление последнего сегмента змейки из списка"""
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def reset(self) -> None:
        """Возвращение змейки в исходное состояние"""
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.last = None

    def get_head_position(self) -> Tuple[int, int]:
        """Определяем положение головы змейки"""
        return self.positions[0]

    def get_length(self) -> int:
        """Вычисляем длину змейки"""
        return len(self.positions)

    def draw(self) -> None:
        """Рисуем змейку"""
        for position in self.positions:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)
        """Отрисовка головы змейки"""
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)
        """Затирание последнего сегмента"""
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)


class Apple(GameObject):
    """Класс, описывающий яблоко"""

    def __init__(
            self,
            snake_positions: List[Tuple[int, int]] = [(0, 0)]) -> None:
        super().__init__(position=(0, 0), body_color=APPLE_COLOR)
        self.snake_positions: List[Tuple[int, int]] = snake_positions
        self.randomize_position()

    def generate_new_position(self) -> Tuple[int, int]:
        """Генерация случайной позиции не занятой змейкой"""
        while True:
            x = randint(0, GRID_WIDTH - 1)
            y = randint(0, GRID_HEIGHT - 1)
            new_position = (x * GRID_SIZE, y * GRID_SIZE)
            if new_position not in self.snake_positions:
                return new_position

    def randomize_position(self) -> None:
        """Устанавливаем новую случайную позицию"""
        self.position = self.generate_new_position()

    def draw(self) -> None:
        """Рисуем яблоко"""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


def handle_keys(snake: Snake) -> bool:
    """Processing user input."""
    direction_mapping = {
        pygame.K_UP: UP,
        pygame.K_DOWN: DOWN,
        pygame.K_LEFT: LEFT,
        pygame.K_RIGHT: RIGHT,
    }

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                snake.paused = not snake.paused
            else:
                new_direction = direction_mapping.get(event.key, None)
                if new_direction and (
                    (snake.direction == UP and new_direction != DOWN)
                    or (snake.direction == DOWN and new_direction != UP)
                    or (snake.direction == LEFT and new_direction != RIGHT)
                    or (snake.direction == RIGHT and new_direction != LEFT)
                ):
                    snake.next_direction = new_direction
    return True


def main() -> None:
    """Функция main."""
    pygame.init()
    snake = Snake()
    apple = Apple(snake.positions)
    running = True
    while running:
        clock.tick(snake.speed)
        screen.fill(BOARD_BACKGROUND_COLOR)
        running = handle_keys(snake)
        if not (snake.game_over or snake.paused):
            next_position = snake.move()
            snake.is_game_over(next_position)
            snake.insert_next_position(next_position)
            snake.del_last_segment()
            if snake.position == apple.position:
                snake.length += 1
                if snake.speed < 100:
                    snake.speed += 1
                apple.position = apple.generate_new_position()
        snake.draw()
        apple.draw()
        if snake.game_over:
            pygame.display.set_caption(
                f'Ты проиграл! | Скорость: {snake.speed} | '
                f'Длина змейки: {snake.get_length()}'
            )
        elif snake.paused:
            pygame.display.set_caption(
                f'Пауза! | Скорость: {snake.speed} | '
                f'Длина змейки: {snake.get_length()}'
            )
        else:
            pygame.display.set_caption(
                f'Змейка | Скорость:: {snake.speed} | '
                f'Длина змейки: {snake.get_length()}'
            )
        pygame.display.update()
        clock.tick(snake.speed)
    pygame.quit()


if __name__ == '__main__':
    main()