"""
Menu system for the racing game.
"""

import pygame
from enum import Enum
from typing import List, Tuple, Callable
from src.car_stats import CAR_TYPES, CAR_COLORS


class GameState(Enum):
    MENU = "menu"
    TRACK_SELECT = "track_select"
    CAR_TYPE_SELECT = "car_type_select"
    CAR_COLOR_SELECT = "car_color_select"
    PLAYING = "playing"
    PAUSED = "paused"


class Menu:
    """Handles all menu screens and navigation."""

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.option_font = pygame.font.Font(None, 48)
        self.hint_font = pygame.font.Font(None, 28)

        # Colors
        self.white = (255, 255, 255)
        self.gray = (128, 128, 128)
        self.green = (0, 255, 0)
        self.red = (255, 0, 0)
        self.black = (0, 0, 0)
        self.dark_gray = (40, 40, 40)

        # Menu state
        self.selected_index = 0

        # Main menu options
        self.main_options = ["Play", "Select Track", "Select Car", "Quit"]

        # Pause menu options
        self.pause_options = ["Resume", "Restart", "Main Menu"]

        # Selection state
        self.selected_track = 0
        self.selected_car_type = 1  # 1-5
        self.selected_car_color = 0  # index into CAR_COLORS
        self.track_names = ["Oval", "Figure-8"]

    def handle_input(self, event: pygame.event.Event, state: GameState) -> Tuple[GameState, dict]:
        """
        Handle menu input and return new state and any actions.

        Returns:
            Tuple of (new_state, actions_dict)
        """
        actions = {}

        if event.type != pygame.KEYDOWN:
            return state, actions

        if state == GameState.MENU:
            return self._handle_main_menu(event)
        elif state == GameState.TRACK_SELECT:
            return self._handle_track_select(event)
        elif state == GameState.CAR_TYPE_SELECT:
            return self._handle_car_type_select(event)
        elif state == GameState.CAR_COLOR_SELECT:
            return self._handle_car_color_select(event)
        elif state == GameState.PAUSED:
            return self._handle_pause_menu(event)

        return state, actions

    def _handle_main_menu(self, event) -> Tuple[GameState, dict]:
        """Handle main menu input."""
        actions = {}

        if event.key == pygame.K_UP:
            self.selected_index = (self.selected_index - 1) % len(self.main_options)
        elif event.key == pygame.K_DOWN:
            self.selected_index = (self.selected_index + 1) % len(self.main_options)
        elif event.key == pygame.K_RETURN:
            option = self.main_options[self.selected_index]
            if option == "Play":
                return GameState.PLAYING, {"start_race": True}
            elif option == "Select Track":
                self.selected_index = self.selected_track
                return GameState.TRACK_SELECT, {}
            elif option == "Select Car":
                self.selected_index = self.selected_car_type - 1
                return GameState.CAR_TYPE_SELECT, {}
            elif option == "Quit":
                actions["quit"] = True

        return GameState.MENU, actions

    def _handle_track_select(self, event) -> Tuple[GameState, dict]:
        """Handle track selection input."""
        actions = {}

        if event.key == pygame.K_UP or event.key == pygame.K_LEFT:
            self.selected_index = (self.selected_index - 1) % len(self.track_names)
        elif event.key == pygame.K_DOWN or event.key == pygame.K_RIGHT:
            self.selected_index = (self.selected_index + 1) % len(self.track_names)
        elif event.key == pygame.K_RETURN:
            self.selected_track = self.selected_index
            actions["track_changed"] = self.selected_track
            self.selected_index = 0
            return GameState.MENU, actions
        elif event.key == pygame.K_ESCAPE:
            self.selected_index = 0
            return GameState.MENU, {}

        return GameState.TRACK_SELECT, actions

    def _handle_car_type_select(self, event) -> Tuple[GameState, dict]:
        """Handle car type selection input."""
        actions = {}
        num_types = len(CAR_TYPES)

        if event.key == pygame.K_UP or event.key == pygame.K_LEFT:
            self.selected_index = (self.selected_index - 1) % num_types
        elif event.key == pygame.K_DOWN or event.key == pygame.K_RIGHT:
            self.selected_index = (self.selected_index + 1) % num_types
        elif event.key == pygame.K_RETURN:
            self.selected_car_type = self.selected_index + 1  # Types are 1-5
            self.selected_index = self.selected_car_color
            return GameState.CAR_COLOR_SELECT, {}
        elif event.key == pygame.K_ESCAPE:
            self.selected_index = 0
            return GameState.MENU, {}

        return GameState.CAR_TYPE_SELECT, actions

    def _handle_car_color_select(self, event) -> Tuple[GameState, dict]:
        """Handle car color selection input."""
        actions = {}

        if event.key == pygame.K_UP or event.key == pygame.K_LEFT:
            self.selected_index = (self.selected_index - 1) % len(CAR_COLORS)
        elif event.key == pygame.K_DOWN or event.key == pygame.K_RIGHT:
            self.selected_index = (self.selected_index + 1) % len(CAR_COLORS)
        elif event.key == pygame.K_RETURN:
            self.selected_car_color = self.selected_index
            actions["car_changed"] = {
                "type": self.selected_car_type,
                "color": CAR_COLORS[self.selected_car_color]
            }
            self.selected_index = 0
            return GameState.MENU, actions
        elif event.key == pygame.K_ESCAPE:
            self.selected_index = self.selected_car_type - 1
            return GameState.CAR_TYPE_SELECT, {}

        return GameState.CAR_COLOR_SELECT, actions

    def _handle_pause_menu(self, event) -> Tuple[GameState, dict]:
        """Handle pause menu input."""
        actions = {}

        if event.key == pygame.K_UP:
            self.selected_index = (self.selected_index - 1) % len(self.pause_options)
        elif event.key == pygame.K_DOWN:
            self.selected_index = (self.selected_index + 1) % len(self.pause_options)
        elif event.key == pygame.K_RETURN:
            option = self.pause_options[self.selected_index]
            if option == "Resume":
                self.selected_index = 0
                return GameState.PLAYING, {}
            elif option == "Restart":
                self.selected_index = 0
                return GameState.PLAYING, {"restart": True}
            elif option == "Main Menu":
                self.selected_index = 0
                return GameState.MENU, {"save_race": True}
        elif event.key == pygame.K_ESCAPE:
            self.selected_index = 0
            return GameState.PLAYING, {}

        return GameState.PAUSED, actions

    def draw(self, screen: pygame.Surface, state: GameState):
        """Draw the appropriate menu screen."""
        if state == GameState.MENU:
            self._draw_main_menu(screen)
        elif state == GameState.TRACK_SELECT:
            self._draw_track_select(screen)
        elif state == GameState.CAR_TYPE_SELECT:
            self._draw_car_type_select(screen)
        elif state == GameState.CAR_COLOR_SELECT:
            self._draw_car_color_select(screen)
        elif state == GameState.PAUSED:
            self._draw_pause_menu(screen)

    def _draw_main_menu(self, screen: pygame.Surface):
        """Draw the main menu."""
        screen.fill(self.dark_gray)

        # Title
        title = self.title_font.render("RACING GAME", True, self.white)
        title_rect = title.get_rect(center=(self.screen_width // 2, 120))
        screen.blit(title, title_rect)

        # Options
        start_y = 280
        for i, option in enumerate(self.main_options):
            color = self.green if i == self.selected_index else self.white
            text = self.option_font.render(option, True, color)
            rect = text.get_rect(center=(self.screen_width // 2, start_y + i * 60))
            screen.blit(text, rect)

        # Current selections
        info_y = 520
        track_info = self.hint_font.render(
            f"Track: {self.track_names[self.selected_track]}", True, self.gray
        )
        screen.blit(track_info, (self.screen_width // 2 - 100, info_y))

        car_type_name = CAR_TYPES[self.selected_car_type]["name"]
        car_color_name = CAR_COLORS[self.selected_car_color].capitalize()
        car_info = self.hint_font.render(
            f"Car: {car_color_name} {car_type_name}", True, self.gray
        )
        screen.blit(car_info, (self.screen_width // 2 - 100, info_y + 30))

        # Controls hint
        hint = self.hint_font.render("Arrow Keys: Navigate | Enter: Select", True, self.gray)
        hint_rect = hint.get_rect(center=(self.screen_width // 2, self.screen_height - 40))
        screen.blit(hint, hint_rect)

    def _draw_track_select(self, screen: pygame.Surface):
        """Draw track selection screen."""
        screen.fill(self.dark_gray)

        # Title
        title = self.title_font.render("SELECT TRACK", True, self.white)
        title_rect = title.get_rect(center=(self.screen_width // 2, 120))
        screen.blit(title, title_rect)

        # Track options
        start_y = 300
        for i, track in enumerate(self.track_names):
            color = self.green if i == self.selected_index else self.white
            text = self.option_font.render(track, True, color)
            rect = text.get_rect(center=(self.screen_width // 2, start_y + i * 80))
            screen.blit(text, rect)

        # Hint
        hint = self.hint_font.render("Arrow Keys: Select | Enter: Confirm | ESC: Back", True, self.gray)
        hint_rect = hint.get_rect(center=(self.screen_width // 2, self.screen_height - 40))
        screen.blit(hint, hint_rect)

    def _draw_car_type_select(self, screen: pygame.Surface):
        """Draw car type selection screen with stats."""
        screen.fill(self.dark_gray)

        # Title
        title = self.title_font.render("SELECT VEHICLE", True, self.white)
        title_rect = title.get_rect(center=(self.screen_width // 2, 50))
        screen.blit(title, title_rect)

        # Vehicle type options with stats
        start_y = 110
        row_height = 90
        for i, (type_id, stats) in enumerate(CAR_TYPES.items()):
            is_selected = i == self.selected_index
            color = self.green if is_selected else self.white

            # Vehicle name
            name_text = self.option_font.render(stats["name"], True, color)
            name_rect = name_text.get_rect(midleft=(80, start_y + i * row_height))
            screen.blit(name_text, name_rect)

            # Stats bars - shifted right with proper label spacing
            bar_x = 580
            bar_width = 160
            bar_height = 10
            label_x = 380

            # Speed bar (max 11 for motorcycle)
            speed_pct = stats["max_velocity"] / 11.0
            self._draw_stat_bar(screen, bar_x, start_y + i * row_height - 25, bar_width, bar_height,
                              speed_pct, "Speed", is_selected, label_x)

            # Acceleration bar (max 0.25 for motorcycle)
            accel_pct = stats["acceleration"] / 0.25
            self._draw_stat_bar(screen, bar_x, start_y + i * row_height - 10, bar_width, bar_height,
                              accel_pct, "Acceleration", is_selected, label_x)

            # Handling bar (max 4.5 for motorcycle)
            handling_pct = stats["handling"] / 4.5
            self._draw_stat_bar(screen, bar_x, start_y + i * row_height + 5, bar_width, bar_height,
                              handling_pct, "Handling", is_selected, label_x)

            # Durability bar (max 1.5 for truck)
            durability_pct = stats["durability"] / 1.5
            self._draw_stat_bar(screen, bar_x, start_y + i * row_height + 20, bar_width, bar_height,
                              durability_pct, "Durability", is_selected, label_x)

            # Description
            desc = self.hint_font.render(stats["description"], True, self.gray if not is_selected else self.white)
            screen.blit(desc, (760, start_y + i * row_height - 5))

        # Hint
        hint = self.hint_font.render("Arrow Keys: Select | Enter: Choose Color | ESC: Back", True, self.gray)
        hint_rect = hint.get_rect(center=(self.screen_width // 2, self.screen_height - 30))
        screen.blit(hint, hint_rect)

    def _draw_stat_bar(self, screen, x, y, width, height, pct, label, selected, label_x):
        """Draw a stat bar with label."""
        label_color = self.white if selected else self.gray
        label_text = self.hint_font.render(label, True, label_color)
        screen.blit(label_text, (label_x, y - 2))

        # Background
        pygame.draw.rect(screen, (60, 60, 60), (x, y, width, height))
        # Filled portion
        fill_color = self.green if selected else (100, 200, 100)
        pygame.draw.rect(screen, fill_color, (x, y, int(width * pct), height))

    def _draw_car_color_select(self, screen: pygame.Surface):
        """Draw car color selection screen."""
        screen.fill(self.dark_gray)

        # Title
        car_type_name = CAR_TYPES[self.selected_car_type]["name"]
        title = self.title_font.render(f"SELECT {car_type_name.upper()} COLOR", True, self.white)
        title_rect = title.get_rect(center=(self.screen_width // 2, 120))
        screen.blit(title, title_rect)

        # Car color options
        start_y = 250
        for i, color in enumerate(CAR_COLORS):
            text_color = self.green if i == self.selected_index else self.white
            text = self.option_font.render(color.capitalize(), True, text_color)
            rect = text.get_rect(center=(self.screen_width // 2, start_y + i * 60))
            screen.blit(text, rect)

        # Hint
        hint = self.hint_font.render("Arrow Keys: Select | Enter: Confirm | ESC: Back", True, self.gray)
        hint_rect = hint.get_rect(center=(self.screen_width // 2, self.screen_height - 40))
        screen.blit(hint, hint_rect)

    def _draw_pause_menu(self, screen: pygame.Surface):
        """Draw pause menu overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.fill(self.black)
        overlay.set_alpha(180)
        screen.blit(overlay, (0, 0))

        # Title
        title = self.title_font.render("PAUSED", True, self.white)
        title_rect = title.get_rect(center=(self.screen_width // 2, 200))
        screen.blit(title, title_rect)

        # Options
        start_y = 320
        for i, option in enumerate(self.pause_options):
            color = self.green if i == self.selected_index else self.white
            text = self.option_font.render(option, True, color)
            rect = text.get_rect(center=(self.screen_width // 2, start_y + i * 60))
            screen.blit(text, rect)

        # Hint
        hint = self.hint_font.render("Arrow Keys: Navigate | Enter: Select | ESC: Resume", True, self.gray)
        hint_rect = hint.get_rect(center=(self.screen_width // 2, self.screen_height - 60))
        screen.blit(hint, hint_rect)
