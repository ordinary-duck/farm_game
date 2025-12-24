# -*- coding: utf-8 -*-
"""
Farm Game Main Program
"""
import pygame
import sys
import os
import threading

# Set Windows console encoding to UTF-8
if sys.platform == 'win32':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except Exception:
        pass

from config import *
from database import db
from login_scene import LoginScene
from farm_scene import FarmScene


def get_font(size):
    """Helper to fetch configured font or fallback safely."""
    if FONT_PATH:
        try:
            return pygame.font.Font(FONT_PATH, size)
        except Exception:
            pass
    return pygame.font.Font(None, size)


class Game:
    """Main Game Class"""

    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Create window
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)

        # Clock
        self.clock = pygame.time.Clock()
        self.running = True

        # Loading screen helpers
        self.loading_font = get_font(48)
        self.loading_sub_font = get_font(28)
        self.loading_title = "Loading..."
        self.loading_subtitle = ""
        self.loading_hint = "Please wait..."
        self.loading_task = None
        self.loading_result = None
        self.loading_error = None

        # Connect to database
        if not db.connect():
            print("Cannot connect to database, please check config.py!")
            print("Make sure SQL Server is running and config is correct.")
            sys.exit(1)

        # Current scene
        self.current_scene = None
        self.scene_name = "login"
        self.login_scene = LoginScene(self.screen, db)
        self.farm_scene = None

        print("Game started successfully!")
        print(f"Resolution: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        print(f"FPS: {FPS}")

    def run(self):
        """Main game loop"""
        while self.running:
            # Calculate time delta
            dt = self.clock.tick(FPS) / 1000.0  # Convert to seconds

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.handle_event(event)

            # Update
            self.update(dt)

            # Draw
            self.draw()

            # Update display
            pygame.display.flip()

        # Cleanup
        self.cleanup()

    def handle_event(self, event):
        """Handle events"""
        if self.scene_name == "login":
            result = self.login_scene.handle_event(event)
            if result:
                # Switch to farm scene
                self.switch_to_farm(result['player'], result['farm'])

        elif self.scene_name == "farm":
            result = self.farm_scene.handle_event(event)
            if result == "login":
                # Return to login screen
                self.switch_to_login()

    def update(self, dt):
        """Update game state"""
        if self.scene_name == "login":
            self.login_scene.update(dt)
        elif self.scene_name == "farm":
            self.farm_scene.update(dt)
        elif self.scene_name == "loading":
            self.poll_loading_task()

    def draw(self):
        """Draw scene"""
        if self.scene_name == "login":
            self.login_scene.draw()
        elif self.scene_name == "farm":
            self.farm_scene.draw()
        elif self.scene_name == "loading":
            self.draw_loading_screen()

    def set_loading_screen(self, title="Loading...", subtitle=None, hint="Please wait..."):
        """Update loading texts that the draw function will use."""
        self.loading_title = title
        self.loading_subtitle = subtitle or ""
        self.loading_hint = hint

    def draw_loading_screen(self):
        """Render a simple loading screen each frame."""
        self.screen.fill(COLOR_LIGHT_GREEN)
        title_surface = self.loading_font.render(self.loading_title, True, COLOR_DARK_GREEN)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(title_surface, title_rect)

        if self.loading_subtitle:
            subtitle_surface = self.loading_sub_font.render(self.loading_subtitle, True, COLOR_BLACK)
            subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
            self.screen.blit(subtitle_surface, subtitle_rect)

        hint_surface = self.loading_sub_font.render(self.loading_hint, True, COLOR_BLACK)
        hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(hint_surface, hint_rect)

    def switch_to_farm(self, player_data, farm_data):
        """Begin loading the farm scene asynchronously."""
        print(f"Player {player_data['Name']} entering farm {farm_data['Name']}")
        if self.loading_task and self.loading_task.is_alive():
            return

        loading_subtitle = f"{player_data['Name']} -> {farm_data['Name']}"
        self.set_loading_screen("Loading Farm...", loading_subtitle)
        self.scene_name = "loading"
        self.loading_result = None
        self.loading_error = None

        self.loading_task = threading.Thread(
            target=self._load_farm_scene,
            args=(player_data, farm_data),
            daemon=True
        )
        self.loading_task.start()

    def _load_farm_scene(self, player_data, farm_data):
        """Worker thread that builds the farm scene."""
        try:
            scene = FarmScene(self.screen, db, player_data, farm_data)
            self.loading_result = scene
        except Exception as exc:
            self.loading_error = str(exc)

    def poll_loading_task(self):
        """Check whether the background loading thread has finished."""
        if not self.loading_task:
            return
        if self.loading_task.is_alive():
            return

        self.loading_task.join(timeout=0)
        self.loading_task = None

        if self.loading_error:
            print(f"Failed to load farm: {self.loading_error}")
            self.set_loading_screen("Load Failed", self.loading_error, "Returning to login...")
            pygame.time.delay(800)
            self.switch_to_login()
            return

        if self.loading_result:
            self.farm_scene = self.loading_result
            self.loading_result = None
            self.scene_name = "farm"

    def switch_to_login(self):
        """Switch to login screen"""
        print("Return to login screen")
        self.login_scene = LoginScene(self.screen, db)
        self.farm_scene = None
        self.scene_name = "login"
        self.loading_result = None
        self.loading_error = None
        self.loading_task = None

    def cleanup(self):
        """Cleanup resources"""
        print("Closing game...")
        db.disconnect()
        pygame.quit()
        print("Game closed")


def main():
    """Main function"""
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Game error: {e}")
        import traceback
        traceback.print_exc()

        # Make sure database connection is closed
        try:
            db.disconnect()
        except Exception:
            pass

        pygame.quit()
        sys.exit(1)


if __name__ == "__main__":
    main()
