import pygame
import random
import sys
import uuid
import os

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
SNAKE_SPEED = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# User class
class User:
    def __init__(self, username):
        self.username = username
        self.uuid = uuid.uuid4()

    def __str__(self):
        return f"User: {self.username}, UUID: {self.uuid}"

    def __repr__(self):
        return f"User: {self.username}, UUID: {self.uuid}"

# Snake class
class Snake:
    def __init__(self):
        self.length = 1
        self.positions = [((WIDTH // 2), (HEIGHT // 2))]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.color = GREEN

    def get_head_position(self):
        return self.positions[0]

    def move(self):
        cur = self.get_head_position()
        x, y = self.direction
        new = (((cur[0] + (x * GRID_SIZE)) % WIDTH), (cur[1] + (y * GRID_SIZE)) % HEIGHT)
        if new in self.positions[2:]:
            self.reset()
        else:
            self.positions.insert(0, new)
            if len(self.positions) > self.length:
                self.positions.pop()

    def reset(self):
        self.length = 1
        self.positions = [((WIDTH // 2), (HEIGHT // 2))]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])

    def draw(self, surface):
        for p in self.positions:
            pygame.draw.rect(surface, self.color, (p[0], p[1], GRID_SIZE, GRID_SIZE))

    def handle_keys(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.turn(UP)
                elif event.key == pygame.K_DOWN:
                    self.turn(DOWN)
                elif event.key == pygame.K_LEFT:
                    self.turn(LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.turn(RIGHT)

    def turn(self, direction):
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.direction = direction

# Food class
class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = RED
        self.randomize_position()

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                         random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, 
                         (self.position[0], self.position[1], GRID_SIZE, GRID_SIZE))

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

def draw_grid(surface):
    for y in range(0, HEIGHT, GRID_SIZE):
        for x in range(0, WIDTH, GRID_SIZE):
            r = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, WHITE, r, 1)

def main():
    user = User(os.getenv("USERNAME"))
    send_event("game_started", {"user": f"{user}"})

    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)

    surface = pygame.Surface(screen.get_size())
    surface = surface.convert()

    snake = Snake()
    food = Food()

    score = 0
    font = pygame.font.SysFont("monospace", 16)

    while True:
        clock.tick(SNAKE_SPEED)
        snake.handle_keys()
        snake.move()
        
        if snake.get_head_position() == food.position:
            send_event("food_eaten", {"score": score})
            snake.length += 1
            score += 1
            food.randomize_position()
            # Here you could send an event to your API
            send_event("food_position", {"position": food.position})

        surface.fill(BLACK)
        draw_grid(surface)
        snake.draw(surface)
        food.draw(surface)
        screen.blit(surface, (0, 0))
        
        text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(text, (5, 10))
        
        pygame.display.update()

def send_event(event_type, data):
    # This function would send events to your API
    # For now, we'll just print the event
    print(f"Sending event: {event_type}, Data: {data}")

if __name__ == "__main__":
    main()
