"""
Racing Game - A Python Pygame Racing Game
"""

import pygame
import sys
import os

from src.car import Car
from src.track import Track
from src.camera import Camera
from src.npc_car import NPCCar
from src.data import Database
from src.ui import Menu, GameState
from src.car_stats import get_car_stats, get_car_image_name, get_random_car, CAR_COLORS
import math
import time
import random


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

        # NPC settings
        self.npc_count = 3
        self.npc_cars = []

        # Car selection (must be set before _load_track)
        self.selected_car_type = 1
        self.selected_car_color = "red"

        # Initialize game objects
        self._load_track()

        # Initialize font for UI
        self.font = pygame.font.Font(None, 48)

        # Lap counting
        self.lap_count = 0

        # Race position
        self.player_position = 1

        # Timing
        self.lap_start_time = time.time()
        self.current_lap_time = 0.0
        self.best_lap_time = None
        self.last_lap_time = None

        # Database
        db_path = os.path.join(self.base_path, "data", "racing_game.db")
        self.db = Database(db_path)
        self.player_name = "Player1"
        self.player_id = self.db.get_or_create_player(self.player_name)
        self._load_best_time()

        # Menu system
        self.menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.game_state = GameState.MENU

    def _load_track(self):
        """Load or reload the track and reset car position."""
        self.track = Track(self.assets_path, self.track_index)

        # Get starting position and create/reset player car
        start_x, start_y = self.track.get_start_position()
        start_angle = self.track.get_start_angle()

        # Get car image and stats
        car_image = get_car_image_name(self.selected_car_color, self.selected_car_type)
        self.car_image_path = os.path.join(self.assets_path, car_image)
        car_stats = get_car_stats(self.selected_car_type)

        if hasattr(self, 'player_car'):
            # Recreate car with new stats
            self.player_car = Car(start_x, start_y, self.car_image_path, car_stats)
            self.player_car.angle = start_angle
        else:
            self.player_car = Car(start_x, start_y, self.car_image_path, car_stats)
            self.player_car.angle = start_angle

        # Initialize camera
        if not hasattr(self, 'camera'):
            self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Get world size for camera bounds
        self.world_width, self.world_height = self.track.get_world_size()

        # Reset lap count and timing on track change
        self.lap_count = 0
        self.lap_start_time = time.time()
        self.current_lap_time = 0.0
        self.last_lap_time = None

        # Load best time for this track
        if hasattr(self, 'db'):
            self._load_best_time()

        # Spawn NPC cars
        self._spawn_npcs()

    def _load_best_time(self):
        """Load personal best lap time for current track."""
        track_name = "Oval" if self.track_index == 0 else "Figure-8"
        self.best_lap_time = self.db.get_best_lap_time(self.player_id, track_name)

    def _spawn_npcs(self):
        """Spawn NPC cars at staggered positions with random types."""
        self.npc_cars = []
        npc_positions = self.track.get_npc_start_positions(self.npc_count)

        for i, (x, y, wp_index) in enumerate(npc_positions):
            # Random car type and color
            color, car_type = get_random_car()
            image_path = os.path.join(self.assets_path, get_car_image_name(color, car_type))
            car_stats = get_car_stats(car_type)

            difficulty = 0.6 + (i * 0.08)  # Vary difficulty slightly
            npc = NPCCar(x, y, image_path, difficulty, car_stats)
            npc.current_waypoint = wp_index
            self.npc_cars.append(npc)

    def switch_track(self):
        """Switch to the next track."""
        self.track_index = (self.track_index + 1) % 2  # Toggle between 0 and 1
        self._load_track()

    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            # Handle menu states
            if self.game_state != GameState.PLAYING:
                if event.type == pygame.KEYDOWN:
                    new_state, actions = self.menu.handle_input(event, self.game_state)
                    self._handle_menu_actions(new_state, actions)
                return

            # Playing state - handle game input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game_state = GameState.PAUSED
                    self.menu.selected_index = 0
                elif event.key == pygame.K_t:
                    self.switch_track()
                elif event.key == pygame.K_n:
                    self.cycle_npc_count()
                elif event.key == pygame.K_r:
                    self.reset_race()

    def _handle_menu_actions(self, new_state: GameState, actions: dict):
        """Handle actions from menu system."""
        if actions.get("quit"):
            self.running = False
            return

        if actions.get("track_changed") is not None:
            self.track_index = actions["track_changed"]
            self._load_track()

        if actions.get("car_changed"):
            car_info = actions["car_changed"]
            self.selected_car_type = car_info["type"]
            self.selected_car_color = car_info["color"]
            self._update_player_car()

        if actions.get("start_race"):
            self._load_track()

        if actions.get("restart"):
            self.reset_race()

        if actions.get("save_race") and self.lap_count > 0:
            self._save_race()
            self.lap_count = 0

        self.game_state = new_state

    def _update_player_car(self):
        """Update player car with selected type and color."""
        car_image = get_car_image_name(self.selected_car_color, self.selected_car_type)
        self.car_image_path = os.path.join(self.assets_path, car_image)
        car_stats = get_car_stats(self.selected_car_type)

        if hasattr(self, 'player_car'):
            start_x, start_y = self.track.get_start_position()
            start_angle = self.track.get_start_angle()
            self.player_car = Car(start_x, start_y, self.car_image_path, car_stats)
            self.player_car.angle = start_angle

    def reset_race(self):
        """Reset the race, saving results if laps completed."""
        if self.lap_count > 0:
            self._save_race()
        self._load_track()

    def _save_race(self):
        """Save current race to database."""
        track_name = "Oval" if self.track_index == 0 else "Figure-8"
        self.db.save_race(
            player_id=self.player_id,
            track=track_name,
            laps=self.lap_count,
            best_lap_time=self.best_lap_time,
            total_time=None
        )

    def cycle_npc_count(self):
        """Cycle NPC count from 0-5."""
        self.npc_count = (self.npc_count + 1) % 6
        self._spawn_npcs()

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
        # Only update game when playing
        if self.game_state != GameState.PLAYING:
            return

        # Handle continuous input
        self.handle_input()

        # Check if car is on road
        player_x, player_y = self.player_car.get_position()
        on_road = self.track.is_on_road(player_x, player_y)

        # Update player car with surface type and world bounds
        self.player_car.update(on_road, self.world_width, self.world_height)

        # Update NPC cars
        for npc in self.npc_cars:
            npc_x, npc_y = npc.get_position()
            npc_on_road = self.track.is_on_road(npc_x, npc_y)
            npc.update(self.track.waypoints, npc_on_road)

        # Handle collisions between all cars
        self._handle_collisions()

        # Calculate race positions
        self._update_positions()

        # Update current lap time
        self.current_lap_time = time.time() - self.lap_start_time

        # Check for lap completion
        new_x, new_y = self.player_car.get_position()
        prev_x = self.player_car.get_prev_x()
        if self.track.check_finish_line(prev_x, new_x, new_y):
            self.lap_count += 1
            self.last_lap_time = self.current_lap_time

            # Update best lap time
            if self.best_lap_time is None or self.current_lap_time < self.best_lap_time:
                self.best_lap_time = self.current_lap_time

            # Reset lap timer
            self.lap_start_time = time.time()

        # Update camera to follow player
        self.camera.update(new_x, new_y, self.world_width, self.world_height)

    def _handle_collisions(self):
        """Handle collisions between all cars."""
        all_cars = [self.player_car] + self.npc_cars
        collision_radius = 25

        for i in range(len(all_cars)):
            for j in range(i + 1, len(all_cars)):
                car1 = all_cars[i]
                car2 = all_cars[j]

                x1, y1 = car1.get_position()
                x2, y2 = car2.get_position()

                dx = x2 - x1
                dy = y2 - y1
                dist = math.sqrt(dx * dx + dy * dy)

                if dist < collision_radius * 2 and dist > 0:
                    # Calculate push direction
                    overlap = (collision_radius * 2 - dist) / 2
                    push_x = (dx / dist) * overlap
                    push_y = (dy / dist) * overlap

                    # Push cars apart
                    car1.apply_collision(-push_x, -push_y)
                    car2.apply_collision(push_x, push_y)

    def _update_positions(self):
        """Calculate race positions based on progress."""
        waypoints = self.track.waypoints

        # Get player progress (use laps + waypoint progress)
        player_progress = self.lap_count * len(waypoints) + self.player_car.get_progress(waypoints)

        # Count how many NPCs are ahead
        position = 1
        for npc in self.npc_cars:
            npc_progress = npc.get_progress(waypoints)
            if npc_progress > player_progress:
                position += 1

        self.player_position = position

    def render(self):
        """Render the game."""
        # Draw menu screens
        if self.game_state in (GameState.MENU, GameState.TRACK_SELECT,
                               GameState.CAR_TYPE_SELECT, GameState.CAR_COLOR_SELECT):
            self.menu.draw(self.screen, self.game_state)
            pygame.display.flip()
            return

        # Clear screen
        self.screen.fill(BLACK)

        # Get camera offset
        camera_offset = self.camera.get_offset()

        # Draw track
        self.track.draw(self.screen, camera_offset)

        # Draw NPC cars
        for npc in self.npc_cars:
            npc.draw(self.screen, camera_offset)

        # Draw player car
        self.player_car.draw(self.screen, camera_offset)

        # Draw UI
        self._draw_ui()

        # Draw pause overlay if paused
        if self.game_state == GameState.PAUSED:
            self.menu.draw(self.screen, self.game_state)

        # Update display
        pygame.display.flip()

    def _draw_ui(self):
        """Draw the user interface elements."""
        # Lap counter
        lap_text = self.font.render(f"Lap: {self.lap_count}", True, WHITE)
        self.screen.blit(lap_text, (20, 20))

        # Position
        total_cars = 1 + len(self.npc_cars)
        pos_text = self.font.render(f"Position: {self.player_position}/{total_cars}", True, WHITE)
        self.screen.blit(pos_text, (20, 60))

        # Current lap time
        time_text = self.font.render(f"Time: {self.current_lap_time:.2f}s", True, WHITE)
        self.screen.blit(time_text, (20, 100))

        # Best lap time
        if self.best_lap_time:
            best_text = self.font.render(f"Best: {self.best_lap_time:.2f}s", True, GREEN)
        else:
            best_text = self.font.render("Best: --", True, GRAY)
        self.screen.blit(best_text, (20, 140))

        # Last lap time
        if self.last_lap_time:
            last_text = self.font.render(f"Last: {self.last_lap_time:.2f}s", True, WHITE)
            self.screen.blit(last_text, (20, 180))

        # Right side info
        track_name = "Oval" if self.track_index == 0 else "Figure-8"
        track_text = self.font.render(f"Track: {track_name}", True, WHITE)
        self.screen.blit(track_text, (SCREEN_WIDTH - 250, 20))

        npc_text = self.font.render(f"NPCs: {self.npc_count}", True, WHITE)
        self.screen.blit(npc_text, (SCREEN_WIDTH - 250, 60))

        # Controls hint
        hint_font = pygame.font.Font(None, 24)
        hint_text = hint_font.render("T: Track | N: NPCs | R: Reset | WASD: Drive | ESC: Quit", True, GRAY)
        self.screen.blit(hint_text, (20, SCREEN_HEIGHT - 30))

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)

        # Save race on exit if laps completed
        if self.lap_count > 0:
            self._save_race()

        self.db.close()
        pygame.quit()
        sys.exit()


def main():
    """Entry point."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
