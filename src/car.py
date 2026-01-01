"""
Car class with arcade-style physics.
"""

import pygame
import math
from typing import Tuple


class Car:
    """A car with arcade-style physics."""

    def __init__(self, x: float, y: float, image_path: str):
        """
        Initialize the car.

        Args:
            x: Initial x position
            y: Initial y position
            image_path: Path to the car sprite image
        """
        self.x = x
        self.y = y
        self.prev_x = x  # Track previous position for lap detection
        self.angle = 0  # Degrees, 0 = facing up
        self.velocity = 0.0

        # Physics constants
        self.max_velocity = 8.0
        self.acceleration = 0.15
        self.brake_strength = 0.3
        self.friction = 0.02
        self.grass_friction = 0.08  # Higher friction on grass
        self.rotation_speed = 3.0
        self.min_velocity_for_rotation = 0.5

        # Load and store the original image
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))

        # Car dimensions for collision (approximate)
        self.collision_radius = 20

    def accelerate(self):
        """Accelerate the car forward."""
        self.velocity += self.acceleration
        if self.velocity > self.max_velocity:
            self.velocity = self.max_velocity

    def brake(self):
        """Apply brakes / reverse."""
        self.velocity -= self.brake_strength
        if self.velocity < -self.max_velocity / 2:
            self.velocity = -self.max_velocity / 2

    def rotate_left(self):
        """Rotate the car left."""
        if abs(self.velocity) > self.min_velocity_for_rotation:
            # Rotate more when moving faster
            rotation_factor = min(1.0, abs(self.velocity) / 4.0)
            self.angle += self.rotation_speed * rotation_factor
            if self.velocity < 0:
                self.angle -= self.rotation_speed * rotation_factor * 2

    def rotate_right(self):
        """Rotate the car right."""
        if abs(self.velocity) > self.min_velocity_for_rotation:
            rotation_factor = min(1.0, abs(self.velocity) / 4.0)
            self.angle -= self.rotation_speed * rotation_factor
            if self.velocity < 0:
                self.angle += self.rotation_speed * rotation_factor * 2

    def apply_friction(self, on_road: bool = True):
        """
        Apply friction to slow down the car.

        Args:
            on_road: True if car is on road, False if on grass
        """
        friction = self.friction if on_road else self.grass_friction

        if self.velocity > 0:
            self.velocity -= friction
            if self.velocity < 0:
                self.velocity = 0
        elif self.velocity < 0:
            self.velocity += friction
            if self.velocity > 0:
                self.velocity = 0

    def update(self, on_road: bool = True, world_width: int = 0, world_height: int = 0):
        """
        Update the car's position based on velocity and angle.

        Args:
            on_road: Whether the car is currently on a road tile
            world_width: Width of the game world (for boundary collision)
            world_height: Height of the game world (for boundary collision)
        """
        # Store previous position for lap detection
        self.prev_x = self.x

        # Apply friction based on surface
        self.apply_friction(on_road)

        # Reduce max speed on grass
        if not on_road and self.velocity > self.max_velocity * 0.5:
            self.velocity = self.max_velocity * 0.5

        # Convert angle to radians for movement calculation
        angle_rad = math.radians(self.angle)

        # Calculate new position
        new_x = self.x - self.velocity * math.sin(angle_rad)
        new_y = self.y - self.velocity * math.cos(angle_rad)

        # Boundary collision
        if world_width > 0 and world_height > 0:
            margin = self.collision_radius

            # Check X bounds
            if new_x < margin:
                new_x = margin
                self.velocity *= 0.5  # Reduce velocity on collision
            elif new_x > world_width - margin:
                new_x = world_width - margin
                self.velocity *= 0.5

            # Check Y bounds
            if new_y < margin:
                new_y = margin
                self.velocity *= 0.5
            elif new_y > world_height - margin:
                new_y = world_height - margin
                self.velocity *= 0.5

        # Apply new position
        self.x = new_x
        self.y = new_y

        # Rotate the image
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def reset(self, x: float, y: float, angle: float):
        """Reset car to a position and angle."""
        self.x = x
        self.y = y
        self.prev_x = x
        self.angle = angle
        self.velocity = 0.0

    def draw(self, screen: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)):
        """
        Draw the car on the screen.

        Args:
            screen: Pygame surface to draw on
            camera_offset: Tuple of (x, y) camera offset
        """
        draw_x = self.x - camera_offset[0]
        draw_y = self.y - camera_offset[1]
        draw_rect = self.image.get_rect(center=(draw_x, draw_y))
        screen.blit(self.image, draw_rect)

    def get_position(self) -> Tuple[float, float]:
        """Return the car's current position."""
        return (self.x, self.y)

    def get_prev_x(self) -> float:
        """Return the car's previous x position."""
        return self.prev_x
