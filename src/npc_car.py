"""
NPC Car class with AI waypoint following.
"""

import pygame
import math
from typing import Tuple, List


class NPCCar:
    """An AI-controlled car that follows waypoints."""

    def __init__(self, x: float, y: float, image_path: str, difficulty: float = 0.7):
        """
        Initialize the NPC car.

        Args:
            x: Initial x position
            y: Initial y position
            image_path: Path to the car sprite image
            difficulty: Speed multiplier (0.5 = easy, 1.0 = hard)
        """
        self.x = x
        self.y = y
        self.prev_x = x
        self.angle = 0
        self.velocity = 0.0
        self.difficulty_multiplier = difficulty

        # Physics constants (scaled by difficulty)
        self.max_velocity = 6.0 * difficulty
        self.acceleration = 0.12
        self.friction = 0.02
        self.rotation_speed = 2.5

        # Waypoint tracking
        self.current_waypoint = 0
        self.waypoint_threshold = 60  # Distance to consider waypoint reached

        # Load image
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))

        # Collision
        self.collision_radius = 20

    def update(self, waypoints: List[Tuple[float, float]], on_road: bool = True):
        """
        Update NPC position, following waypoints.

        Args:
            waypoints: List of (x, y) waypoint positions
            on_road: Whether the car is on a road tile
        """
        self.prev_x = self.x

        if not waypoints:
            return

        # Get current target waypoint
        target_x, target_y = waypoints[self.current_waypoint]

        # Calculate angle to waypoint
        dx = target_x - self.x
        dy = target_y - self.y
        target_angle = math.degrees(math.atan2(-dx, -dy))

        # Normalize angle difference
        angle_diff = (target_angle - self.angle + 180) % 360 - 180

        # Rotate toward waypoint
        if abs(angle_diff) > 2:
            if angle_diff > 0:
                self.angle += min(self.rotation_speed, angle_diff)
            else:
                self.angle -= min(self.rotation_speed, -angle_diff)

        # Accelerate (reduce speed when turning sharply)
        turn_factor = 1.0 - min(abs(angle_diff) / 90, 0.5)
        self.velocity += self.acceleration * turn_factor
        if self.velocity > self.max_velocity * turn_factor:
            self.velocity = self.max_velocity * turn_factor

        # Apply friction
        friction = self.friction if on_road else self.friction * 3
        self.velocity -= friction
        if self.velocity < 0:
            self.velocity = 0

        # Move
        angle_rad = math.radians(self.angle)
        self.x -= self.velocity * math.sin(angle_rad)
        self.y -= self.velocity * math.cos(angle_rad)

        # Check if reached waypoint
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < self.waypoint_threshold:
            self.current_waypoint = (self.current_waypoint + 1) % len(waypoints)

        # Update image rotation
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def get_position(self) -> Tuple[float, float]:
        """Return current position."""
        return (self.x, self.y)

    def get_progress(self, waypoints: List[Tuple[float, float]]) -> float:
        """
        Get race progress as a float (waypoint index + fraction to next).
        Higher = further ahead in race.
        """
        if not waypoints:
            return 0.0

        target_x, target_y = waypoints[self.current_waypoint]
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        # Progress = current waypoint + (1 - normalized distance to next)
        max_dist = 200  # Approximate max distance between waypoints
        fraction = 1.0 - min(dist / max_dist, 1.0)

        return self.current_waypoint + fraction

    def draw(self, screen: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)):
        """Draw the car on screen."""
        draw_x = self.x - camera_offset[0]
        draw_y = self.y - camera_offset[1]
        draw_rect = self.image.get_rect(center=(draw_x, draw_y))
        screen.blit(self.image, draw_rect)

    def apply_collision(self, push_x: float, push_y: float):
        """Apply collision response."""
        self.x += push_x
        self.y += push_y
        self.velocity *= 0.5
