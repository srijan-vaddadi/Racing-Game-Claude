"""
Racing Game - A Python Pygame Racing Game
"""

import pygame
import sys
import os

from src.car import Car
from src.track import Track
from src.camera import Camera


# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)


class Game:
    """Main game class."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Racing Game")
        self.clock = pygame.time.Clock()
        self.running = True

        # Get the base path for assets
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.assets_path = os.path.join(self.base_path, "assets")

        # Initialize game objects
        self.track = Track(self.assets_path)

        # Get starting position and create player car
        start_x, start_y = self.track.get_start_position()
        car_image_path = os.path.join(self.assets_path, "cars", "car_red_1.png")
        self.player_car = Car(start_x, start_y, car_image_path)
        self.player_car.angle = 90  # Face right (along the bottom straight)

        # Initialize camera
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Get world size for camera bounds
        self.world_width, self.world_height = self.track.get_world_size()

    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def handle_input(self):
        """Handle continuous keyboard input for car controls."""
        keys = pygame.key.get_pressed()

        # WASD controls
        if keys[pygame.K_w]:
            self.player_car.accelerate()
        if keys[pygame.K_s]:
            self.player_car.brake()
        if keys[pygame.K_a]:
            self.player_car.rotate_left()
        if keys[pygame.K_d]:
            self.player_car.rotate_right()

        # Arrow key controls (same functions)
        if keys[pygame.K_UP]:
            self.player_car.accelerate()
        if keys[pygame.K_DOWN]:
            self.player_car.brake()
        if keys[pygame.K_LEFT]:
            self.player_car.rotate_left()
        if keys[pygame.K_RIGHT]:
            self.player_car.rotate_right()

    def update(self):
        """Update game state."""
        # Handle continuous input
        self.handle_input()

        # Update player car
        self.player_car.update()

        # Update camera to follow player
        player_x, player_y = self.player_car.get_position()
        self.camera.update(player_x, player_y, self.world_width, self.world_height)

    def render(self):
        """Render the game."""
        # Clear screen
        self.screen.fill(BLACK)

        # Get camera offset
        camera_offset = self.camera.get_offset()

        # Draw track
        self.track.draw(self.screen, camera_offset)

        # Draw player car
        self.player_car.draw(self.screen, camera_offset)

        # Update display
        pygame.display.flip()

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


def main():
    """Entry point."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
