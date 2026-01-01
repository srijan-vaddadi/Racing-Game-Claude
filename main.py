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
        self.car_image_path = os.path.join(self.assets_path, "cars", "car_red_1.png")

        # Track selection
        self.track_index = 0

        # Initialize game objects
        self._load_track()

        # Initialize font for UI
        self.font = pygame.font.Font(None, 48)

        # Lap counting
        self.lap_count = 0

    def _load_track(self):
        """Load or reload the track and reset car position."""
        self.track = Track(self.assets_path, self.track_index)

        # Get starting position and create/reset player car
        start_x, start_y = self.track.get_start_position()
        start_angle = self.track.get_start_angle()

        if hasattr(self, 'player_car'):
            self.player_car.reset(start_x, start_y, start_angle)
        else:
            self.player_car = Car(start_x, start_y, self.car_image_path)
            self.player_car.angle = start_angle

        # Initialize camera
        if not hasattr(self, 'camera'):
            self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Get world size for camera bounds
        self.world_width, self.world_height = self.track.get_world_size()

        # Reset lap count on track change
        self.lap_count = 0

    def switch_track(self):
        """Switch to the next track."""
        self.track_index = (self.track_index + 1) % 2  # Toggle between 0 and 1
        self._load_track()

    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_t:
                    self.switch_track()

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

        # Check if car is on road
        player_x, player_y = self.player_car.get_position()
        on_road = self.track.is_on_road(player_x, player_y)

        # Update player car with surface type and world bounds
        self.player_car.update(on_road, self.world_width, self.world_height)

        # Check for lap completion
        new_x, new_y = self.player_car.get_position()
        prev_x = self.player_car.get_prev_x()
        if self.track.check_finish_line(prev_x, new_x, new_y):
            self.lap_count += 1

        # Update camera to follow player
        self.camera.update(new_x, new_y, self.world_width, self.world_height)

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

        # Draw UI
        self._draw_ui()

        # Update display
        pygame.display.flip()

    def _draw_ui(self):
        """Draw the user interface elements."""
        # Lap counter
        lap_text = self.font.render(f"Lap: {self.lap_count}", True, WHITE)
        self.screen.blit(lap_text, (20, 20))

        # Track indicator
        track_name = "Oval" if self.track_index == 0 else "Figure-8"
        track_text = self.font.render(f"Track: {track_name}", True, WHITE)
        self.screen.blit(track_text, (20, 60))

        # Controls hint
        hint_font = pygame.font.Font(None, 24)
        hint_text = hint_font.render("T: Switch Track | WASD/Arrows: Drive | ESC: Quit", True, GRAY)
        self.screen.blit(hint_text, (20, SCREEN_HEIGHT - 30))

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
