"""
Camera class for following the player.
"""

from typing import Tuple


class Camera:
    """A camera that follows a target."""

    def __init__(self, screen_width: int, screen_height: int):
        """
        Initialize the camera.

        Args:
            screen_width: Width of the screen
            screen_height: Height of the screen
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = 0.0
        self.y = 0.0
        self.smoothing = 0.1  # Lower = smoother camera, higher = more responsive

    def update(self, target_x: float, target_y: float, world_width: int, world_height: int):
        """
        Update the camera position to follow a target.

        Args:
            target_x: Target x position to follow
            target_y: Target y position to follow
            world_width: Width of the game world
            world_height: Height of the game world
        """
        # Calculate desired camera position (center target on screen)
        desired_x = target_x - self.screen_width // 2
        desired_y = target_y - self.screen_height // 2

        # Smooth camera movement
        self.x += (desired_x - self.x) * self.smoothing
        self.y += (desired_y - self.y) * self.smoothing

        # Clamp camera to world bounds
        self.x = max(0, min(self.x, world_width - self.screen_width))
        self.y = max(0, min(self.y, world_height - self.screen_height))

    def get_offset(self) -> Tuple[float, float]:
        """Return the camera offset for rendering."""
        return (self.x, self.y)
