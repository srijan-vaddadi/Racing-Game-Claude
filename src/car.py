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
        self.angle = 0  # Degrees, 0 = facing up
        self.velocity = 0.0

        # Physics constants
        self.max_velocity = 8.0
        self.acceleration = 0.15
        self.brake_strength = 0.3
        self.friction = 0.02
        self.rotation_speed = 3.0
        self.min_velocity_for_rotation = 0.5

        # Load and store the original image
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))

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

    def apply_friction(self):
        """Apply friction to slow down the car."""
        if self.velocity > 0:
            self.velocity -= self.friction
            if self.velocity < 0:
                self.velocity = 0
        elif self.velocity < 0:
            self.velocity += self.friction
            if self.velocity > 0:
                self.velocity = 0

    def update(self):
        """Update the car's position based on velocity and angle."""
        # Apply friction
        self.apply_friction()

        # Convert angle to radians for movement calculation
        # Sprite faces up at angle=0, pygame Y-axis is inverted
        angle_rad = math.radians(self.angle)

        # Update position based on velocity and angle
        # For up-facing sprite: dx = -sin(angle), dy = -cos(angle)
        self.x -= self.velocity * math.sin(angle_rad)
        self.y -= self.velocity * math.cos(angle_rad)

        # Rotate the image
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=(self.x, self.y))

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
