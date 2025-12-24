# -*- coding: utf-8 -*-
"""
Login Scene - Player Selection with Navigation
"""
import pygame
import os
from config import *


def get_font(size):
    """Get font with Chinese support"""
    if FONT_PATH:
        try:
            return pygame.font.Font(FONT_PATH, size)
        except:
            pass
    return pygame.font.Font(None, size)


class Button:
    """Button Class with optional custom image support"""
    
    def __init__(self, x, y, width, height, text, font_size=FONT_SIZE_SMALL, image_path=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = BUTTON_COLOR
        self.hover_color = BUTTON_HOVER_COLOR
        self.text_color = BUTTON_TEXT_COLOR
        self.font = get_font(font_size)
        self.is_hovered = False
        
        # Load custom image if provided
        self.image = None
        self.hover_image = None
        if image_path:
            self.load_button_image(image_path)
    
    def load_button_image(self, image_path):
        """Load and scale button image"""
        # Handle relative paths - convert to absolute path
        if not os.path.isabs(image_path):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            full_path = os.path.join(script_dir, image_path)
        else:
            full_path = image_path
        
        if os.path.exists(full_path):
            try:
                # Load original image
                original_image = pygame.image.load(full_path).convert_alpha()
                # Scale to button size
                self.image = pygame.transform.scale(original_image, (self.rect.width, self.rect.height))
                
                # Create a slightly brighter version for hover effect
                self.hover_image = self.image.copy()
                self.hover_image.fill((50, 50, 50, 0), special_flags=pygame.BLEND_RGB_ADD)
                
                print(f"Loaded button image: {full_path}")
            except Exception as e:
                print(f"Failed to load button image {full_path}: {e}")
                self.image = None
                self.hover_image = None
        else:
            print(f"Button image not found: {full_path}")
        
    def draw(self, surface):
        """Draw button (image or default rectangle)"""
        if self.image:
            # Draw custom image
            current_image = self.hover_image if (self.is_hovered and self.hover_image) else self.image
            surface.blit(current_image, self.rect)
        else:
            # Draw default rectangle button
            color = self.hover_color if self.is_hovered else self.color
            pygame.draw.rect(surface, color, self.rect, border_radius=5)
            pygame.draw.rect(surface, COLOR_BLACK, self.rect, 2, border_radius=5)
        
        # Draw text on top of button
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        """Handle event"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                return True
        return False


class LoginScene:
    """Login Scene with Player Navigation"""
    
    def __init__(self, screen, db):
        self.screen = screen
        self.db = db
        self.font_large = get_font(FONT_SIZE_LARGE)
        self.font_medium = get_font(FONT_SIZE_MEDIUM)
        self.font_small = get_font(FONT_SIZE_SMALL)
        
        self.players = []
        self.current_player_index = 0  # Current selected player index
        self.selected_farm = None
        
        # Navigation buttons
        self.prev_button = None
        self.next_button = None
        self.start_button = None
        
        # Load background image
        self.background_image = None
        self.load_background()
        
        # Load players and create buttons
        self.load_players()
        self.create_buttons()
    
    def load_background(self):
        """Load custom background image"""
        if LOGIN_BG_IMAGE:
            # Handle relative paths - convert to absolute path
            if not os.path.isabs(LOGIN_BG_IMAGE):
                # Get the directory where the script is running
                script_dir = os.path.dirname(os.path.abspath(__file__))
                image_path = os.path.join(script_dir, LOGIN_BG_IMAGE)
            else:
                image_path = LOGIN_BG_IMAGE
            
            if os.path.exists(image_path):
                try:
                    # Load and scale image to fit screen
                    original_image = pygame.image.load(image_path)
                    self.background_image = pygame.transform.scale(
                        original_image, 
                        (SCREEN_WIDTH, SCREEN_HEIGHT)
                    )
                    print(f"Loaded background image: {image_path}")
                except Exception as e:
                    print(f"Failed to load background image: {e}")
                    self.background_image = None
            else:
                print(f"Background image not found: {image_path}")
                self.background_image = None
        else:
            self.background_image = None
    
    def load_players(self):
        """Load all players"""
        self.players = self.db.get_all_players()
        if self.players:
            # Load farms for the first player
            self.load_current_player_farms()
    
    def load_current_player_farms(self):
        """Load farms for current player"""
        if self.players and 0 <= self.current_player_index < len(self.players):
            player = self.players[self.current_player_index]
            farms = self.db.get_player_farms(player['PlayerId'])
            # Auto select first farm
            self.selected_farm = farms[0] if farms else None
    
    def create_buttons(self):
        """Create navigation buttons with custom images"""
        if not self.players:
            return
        
        # Get card configuration for button positioning
        card_x_offset = LOGIN_CARD_X_OFFSET if 'LOGIN_CARD_X_OFFSET' in dir() else 0
        card_y = LOGIN_CARD_Y if 'LOGIN_CARD_Y' in dir() else 200
        card_height = LOGIN_CARD_HEIGHT if 'LOGIN_CARD_HEIGHT' in dir() else 280
        
        # Calculate arrow button Y position (middle of card)
        arrow_y = card_y + card_height // 2 - 30
        
        # Previous player button (Left arrow)
        arrow_size = 60
        self.prev_button = Button(
            SCREEN_WIDTH // 2 - 220 + card_x_offset,
            arrow_y,
            arrow_size,
            arrow_size,
            "<",
            FONT_SIZE_LARGE,
            image_path=BUTTON_PREV_IMAGE  # Use custom image if configured
        )
        
        # Next player button (Right arrow)
        self.next_button = Button(
            SCREEN_WIDTH // 2 + 160 + card_x_offset,
            arrow_y,
            arrow_size,
            arrow_size,
            ">",
            FONT_SIZE_LARGE,
            image_path=BUTTON_NEXT_IMAGE  # Use custom image if configured
        )
        
        # Start game button (below card)
        start_btn_y = card_y + card_height + 40
        self.start_button = Button(
            SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2 + card_x_offset,
            start_btn_y,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "Enter Game",
            FONT_SIZE_MEDIUM,
            image_path=BUTTON_START_IMAGE  # Use custom image if configured
        )
    
    def switch_player(self, direction):
        """Switch player (direction: -1 for previous, 1 for next)"""
        if not self.players:
            return
        
        self.current_player_index = (self.current_player_index + direction) % len(self.players)
        self.load_current_player_farms()
    
    def get_current_player(self):
        """Get current selected player"""
        if self.players and 0 <= self.current_player_index < len(self.players):
            return self.players[self.current_player_index]
        return None
    
    def handle_event(self, event):
        """Handle event"""
        if not self.players:
            return None
        
        # Handle previous button
        if self.prev_button and self.prev_button.handle_event(event):
            self.switch_player(-1)
        
        # Handle next button
        if self.next_button and self.next_button.handle_event(event):
            self.switch_player(1)
        
        # Handle start button
        if self.start_button and self.start_button.handle_event(event):
            player = self.get_current_player()
            if player and self.selected_farm:
                # Return selected player and farm to start game
                return {
                    'player': player,
                    'farm': self.selected_farm
                }
        
        # Handle keyboard navigation
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.switch_player(-1)
            elif event.key == pygame.K_RIGHT:
                self.switch_player(1)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                player = self.get_current_player()
                if player and self.selected_farm:
                    return {
                        'player': player,
                        'farm': self.selected_farm
                    }
        
        return None
    
    def update(self, dt):
        """Update scene"""
        pass
    
    def draw(self):
        """Draw scene"""
        # Draw background (image or solid color)
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            self.screen.fill(COLOR_LIGHT_GREEN)
        
        # Draw title (using configured position)
        title_text = self.font_large.render("Farm Game", True, COLOR_DARK_GREEN)
        title_y = LOGIN_TITLE_Y if 'LOGIN_TITLE_Y' in dir() else 80
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, title_y))
        self.screen.blit(title_text, title_rect)
        
        if not self.players:
            # No players found
            message = self.font_medium.render("No players found in database", True, COLOR_RED)
            message_rect = message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(message, message_rect)
            return
        
        # Get current player
        player = self.get_current_player()
        if not player:
            return
        
        # Draw player info card
        self.draw_player_card(player)
        
        # Draw navigation buttons
        if len(self.players) > 1:
            self.prev_button.draw(self.screen)
            self.next_button.draw(self.screen)
        
        # Draw start button
        self.start_button.draw(self.screen)
        
        # Draw hint text
        hint_text = self.font_small.render(
            "Use arrow keys or click arrows to switch | Press Enter or click to start",
            True,
            COLOR_GRAY
        )
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
        self.screen.blit(hint_text, hint_rect)
    
    def draw_player_card(self, player):
        """Draw player information card with configurable position"""
        # Get card configuration
        card_width = LOGIN_CARD_WIDTH if 'LOGIN_CARD_WIDTH' in dir() else 400
        card_height = LOGIN_CARD_HEIGHT if 'LOGIN_CARD_HEIGHT' in dir() else 280
        card_x_offset = LOGIN_CARD_X_OFFSET if 'LOGIN_CARD_X_OFFSET' in dir() else 0
        card_y = LOGIN_CARD_Y if 'LOGIN_CARD_Y' in dir() else 200
        card_alpha = LOGIN_CARD_ALPHA if 'LOGIN_CARD_ALPHA' in dir() else 220
        
        card_x = SCREEN_WIDTH // 2 - card_width // 2 + card_x_offset
        
        # Semi-transparent card background
        card_surface = pygame.Surface((card_width, card_height))
        card_surface.set_alpha(card_alpha)
        card_surface.fill(COLOR_WHITE)
        self.screen.blit(card_surface, (card_x, card_y))
        
        # Card border
        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
        pygame.draw.rect(self.screen, COLOR_DARK_GREEN, card_rect, 3, border_radius=10)
        
        # Calculate card center for text positioning
        card_center_x = card_x + card_width // 2
        
        # Player name
        name_text = self.font_large.render(player['Name'], True, COLOR_DARK_GREEN)
        name_rect = name_text.get_rect(center=(card_center_x, card_y + 40))
        self.screen.blit(name_text, name_rect)
        
        # Player level
        level_text = self.font_medium.render(f"Level: {player['Level']}", True, COLOR_BLACK)
        level_rect = level_text.get_rect(center=(card_center_x, card_y + 85))
        self.screen.blit(level_text, level_rect)
        
        # Player stats
        stats_y = card_y + 130
        
        # Gold
        gold_text = self.font_small.render(
            f"Gold: {player['CurrencyGold']:.0f}",
            True,
            COLOR_BLACK
        )
        gold_rect = gold_text.get_rect(center=(card_center_x - 80, stats_y))
        self.screen.blit(gold_text, gold_rect)
        
        # Gem
        gem_text = self.font_small.render(
            f"Gem: {player['CurrencyGem']}",
            True,
            COLOR_BLACK
        )
        gem_rect = gem_text.get_rect(center=(card_center_x + 80, stats_y))
        self.screen.blit(gem_text, gem_rect)
        
        # Experience
        exp_text = self.font_small.render(
            f"Experience: {player['Exp']}",
            True,
            COLOR_BLACK
        )
        exp_rect = exp_text.get_rect(center=(card_center_x, stats_y + 35))
        self.screen.blit(exp_text, exp_rect)
        
        # Farm info
        if self.selected_farm:
            farm_y = card_y + 210
            farm_title = self.font_small.render("Farm:", True, COLOR_GRAY)
            farm_title_rect = farm_title.get_rect(center=(card_center_x, farm_y))
            self.screen.blit(farm_title, farm_title_rect)
            
            farm_name = self.font_small.render(
                f"{self.selected_farm['Name']} (Soil Quality: {self.selected_farm['SoilQuality']})",
                True,
                COLOR_BLACK
            )
            farm_name_rect = farm_name.get_rect(center=(card_center_x, farm_y + 30))
            self.screen.blit(farm_name, farm_name_rect)
        
        # Player counter (above card)
        counter_text = self.font_small.render(
            f"Player {self.current_player_index + 1} / {len(self.players)}",
            True,
            COLOR_GRAY
        )
        counter_rect = counter_text.get_rect(center=(card_center_x, card_y - 30))
        self.screen.blit(counter_text, counter_rect)
