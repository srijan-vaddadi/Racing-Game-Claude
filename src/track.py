"""
Track class for rendering tile-based racing tracks.
"""

import pygame
from typing import List, Tuple, Dict


# Tile types
GRASS = 0
ROAD_V = 1      # Vertical straight
ROAD_H = 2      # Horizontal straight
CORNER_TL = 3   # Top-left corner
CORNER_TR = 4   # Top-right corner
CORNER_BL = 5   # Bottom-left corner
CORNER_BR = 6   # Bottom-right corner


class Track:
    """A tile-based racing track."""

    def __init__(self, assets_path: str):
        """
        Initialize the track.

        Args:
            assets_path: Path to the assets folder
        """
        self.tile_size = 128  # Kenney tiles are 128x128
        self.tiles: Dict[int, pygame.Surface] = {}
        self.track_data: List[List[int]] = []
        self.width = 0
        self.height = 0

        # Load tile images
        self._load_tiles(assets_path)

        # Create a simple oval test track
        self._create_test_track()

    def _load_tiles(self, assets_path: str):
        """Load all tile images."""
        roads_path = f"{assets_path}/roads"

        self.tiles[GRASS] = pygame.image.load(f"{roads_path}/land_grass04.png").convert()
        self.tiles[ROAD_V] = pygame.image.load(f"{roads_path}/road_asphalt01.png").convert_alpha()
        self.tiles[ROAD_H] = pygame.image.load(f"{roads_path}/road_asphalt43.png").convert_alpha()
        self.tiles[CORNER_TL] = pygame.image.load(f"{roads_path}/road_asphalt26.png").convert_alpha()
        self.tiles[CORNER_TR] = pygame.image.load(f"{roads_path}/road_asphalt29.png").convert_alpha()
        self.tiles[CORNER_BL] = pygame.image.load(f"{roads_path}/road_asphalt28.png").convert_alpha()
        self.tiles[CORNER_BR] = pygame.image.load(f"{roads_path}/road_asphalt27.png").convert_alpha()

    def _create_test_track(self):
        """Create a simple oval test track."""
        # Track layout (12 columns x 10 rows)
        # Simple oval shape
        G = GRASS
        V = ROAD_V
        H = ROAD_H
        TL = CORNER_TL
        TR = CORNER_TR
        BL = CORNER_BL
        BR = CORNER_BR

        self.track_data = [
            [G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G],
            [G,  G,  TL, H,  H,  H,  H,  H,  H,  TR, G,  G],
            [G,  G,  V,  G,  G,  G,  G,  G,  G,  V,  G,  G],
            [G,  G,  V,  G,  G,  G,  G,  G,  G,  V,  G,  G],
            [G,  G,  V,  G,  G,  G,  G,  G,  G,  V,  G,  G],
            [G,  G,  V,  G,  G,  G,  G,  G,  G,  V,  G,  G],
            [G,  G,  V,  G,  G,  G,  G,  G,  G,  V,  G,  G],
            [G,  G,  V,  G,  G,  G,  G,  G,  G,  V,  G,  G],
            [G,  G,  BL, H,  H,  H,  H,  H,  H,  BR, G,  G],
            [G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G],
        ]

        self.height = len(self.track_data)
        self.width = len(self.track_data[0])

    def get_start_position(self) -> Tuple[float, float]:
        """Get the starting position for a car (middle of bottom straight)."""
        # Start on the bottom horizontal section
        start_x = 6 * self.tile_size + self.tile_size // 2
        start_y = 8 * self.tile_size + self.tile_size // 2
        return (start_x, start_y)

    def get_world_size(self) -> Tuple[int, int]:
        """Get the total size of the track in pixels."""
        return (self.width * self.tile_size, self.height * self.tile_size)

    def draw(self, screen: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)):
        """
        Draw the track.

        Args:
            screen: Pygame surface to draw on
            camera_offset: Tuple of (x, y) camera offset
        """
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        # Calculate visible tile range for optimization
        start_col = max(0, int(camera_offset[0] // self.tile_size))
        end_col = min(self.width, int((camera_offset[0] + screen_width) // self.tile_size) + 2)
        start_row = max(0, int(camera_offset[1] // self.tile_size))
        end_row = min(self.height, int((camera_offset[1] + screen_height) // self.tile_size) + 2)

        # Draw visible tiles
        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                tile_type = self.track_data[row][col]
                tile_image = self.tiles[tile_type]

                # Calculate screen position
                world_x = col * self.tile_size
                world_y = row * self.tile_size
                screen_x = world_x - camera_offset[0]
                screen_y = world_y - camera_offset[1]

                # Draw grass first as background for all tiles
                screen.blit(self.tiles[GRASS], (screen_x, screen_y))

                # Draw road tile on top if not grass
                if tile_type != GRASS:
                    screen.blit(tile_image, (screen_x, screen_y))
