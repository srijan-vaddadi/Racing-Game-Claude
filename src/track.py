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

# Road tiles set (for checking if on road)
ROAD_TILES = {ROAD_V, ROAD_H, CORNER_TL, CORNER_TR, CORNER_BL, CORNER_BR}


class Track:
    """A tile-based racing track."""

    def __init__(self, assets_path: str, track_index: int = 0):
        """
        Initialize the track.

        Args:
            assets_path: Path to the assets folder
            track_index: Which track to load (0 or 1)
        """
        self.assets_path = assets_path
        self.tile_size = 128  # Kenney tiles are 128x128
        self.tiles: Dict[int, pygame.Surface] = {}
        self.track_data: List[List[int]] = []
        self.width = 0
        self.height = 0
        self.track_index = track_index

        # Start/finish line (pixel coordinates)
        self.finish_line_x = 0
        self.finish_line_y1 = 0
        self.finish_line_y2 = 0

        # Load tile images
        self._load_tiles(assets_path)

        # Load selected track
        self._load_track(track_index)

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

    def _load_track(self, track_index: int):
        """Load track data based on index."""
        if track_index == 0:
            self._create_oval_track()
        else:
            self._create_figure8_track()

    def _create_oval_track(self):
        """Create a simple oval track."""
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

        # Finish line on bottom straight (column 7, behind the car start at column 6)
        self.finish_line_x = 7 * self.tile_size
        self.finish_line_y1 = 8 * self.tile_size
        self.finish_line_y2 = 9 * self.tile_size

    def _create_figure8_track(self):
        """Create a figure-8 shaped track."""
        G = GRASS
        V = ROAD_V
        H = ROAD_H
        TL = CORNER_TL
        TR = CORNER_TR
        BL = CORNER_BL
        BR = CORNER_BR

        self.track_data = [
            [G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G],
            [G,  TL, H,  H,  TR, G,  G,  G,  G,  TL, H,  H,  TR, G],
            [G,  V,  G,  G,  V,  G,  G,  G,  G,  V,  G,  G,  V,  G],
            [G,  V,  G,  G,  BL, H,  H,  H,  H,  BR, G,  G,  V,  G],
            [G,  V,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  V,  G],
            [G,  V,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  V,  G],
            [G,  V,  G,  G,  TL, H,  H,  H,  H,  TR, G,  G,  V,  G],
            [G,  V,  G,  G,  V,  G,  G,  G,  G,  V,  G,  G,  V,  G],
            [G,  BL, H,  H,  BR, G,  G,  G,  G,  BL, H,  H,  BR, G],
            [G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G],
        ]

        self.height = len(self.track_data)
        self.width = len(self.track_data[0])

        # Finish line on left side (column 3, behind the car start at column 2)
        self.finish_line_x = 3 * self.tile_size
        self.finish_line_y1 = 8 * self.tile_size
        self.finish_line_y2 = 9 * self.tile_size

    def get_tile_at(self, x: float, y: float) -> int:
        """
        Get the tile type at a world position.

        Args:
            x: World x coordinate
            y: World y coordinate

        Returns:
            Tile type constant (GRASS, ROAD_V, etc.)
        """
        col = int(x // self.tile_size)
        row = int(y // self.tile_size)

        # Return GRASS if outside bounds
        if col < 0 or col >= self.width or row < 0 or row >= self.height:
            return GRASS

        return self.track_data[row][col]

    def is_on_road(self, x: float, y: float) -> bool:
        """Check if a position is on a road tile."""
        return self.get_tile_at(x, y) in ROAD_TILES

    def get_start_position(self) -> Tuple[float, float]:
        """Get the starting position for a car."""
        if self.track_index == 0:
            # Oval track: start on bottom straight
            start_x = 6 * self.tile_size + self.tile_size // 2
            start_y = 8 * self.tile_size + self.tile_size // 2
        else:
            # Figure-8: start on bottom left
            start_x = 2 * self.tile_size + self.tile_size // 2
            start_y = 8 * self.tile_size + self.tile_size // 2
        return (start_x, start_y)

    def get_start_angle(self) -> float:
        """Get the starting angle for a car."""
        if self.track_index == 0:
            return 90  # Facing right on oval
        else:
            return 90  # Facing right on figure-8

    def get_world_size(self) -> Tuple[int, int]:
        """Get the total size of the track in pixels."""
        return (self.width * self.tile_size, self.height * self.tile_size)

    def check_finish_line(self, old_x: float, new_x: float, y: float) -> bool:
        """
        Check if car crossed the finish line (moving right to left / clockwise).

        Args:
            old_x: Previous x position
            new_x: Current x position
            y: Current y position

        Returns:
            True if crossed finish line in correct direction
        """
        # Check if y is within finish line bounds
        if y < self.finish_line_y1 or y > self.finish_line_y2:
            return False

        # Check if crossed the line (moving left, which is decreasing x - clockwise)
        if old_x > self.finish_line_x >= new_x:
            return True

        return False

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

        # Draw finish line
        finish_screen_x = self.finish_line_x - camera_offset[0]
        finish_screen_y1 = self.finish_line_y1 - camera_offset[1]
        finish_screen_y2 = self.finish_line_y2 - camera_offset[1]
        pygame.draw.line(screen, (255, 255, 255),
                        (finish_screen_x, finish_screen_y1),
                        (finish_screen_x, finish_screen_y2), 5)
