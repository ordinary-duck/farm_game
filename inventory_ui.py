# -*- coding: utf-8 -*-
"""
Inventory UI System
"""
import pygame
from config import *


def get_font(size):
    """Get font with Chinese support"""
    if FONT_PATH:
        try:
            return pygame.font.Font(FONT_PATH, size)
        except:
            pass
    return pygame.font.Font(None, size)


class InventoryUI:
    """Inventory Interface"""
    
    def __init__(self, screen, db):
        self.screen = screen
        self.db = db
        self.is_visible = False
        self.farm_id = None
        self.inventory_items = []
        
        self.font_large = get_font(FONT_SIZE_LARGE)
        self.font_medium = get_font(FONT_SIZE_MEDIUM)
        self.font_small = get_font(FONT_SIZE_SMALL)
        
        # UI position and size
        self.panel_width = 600
        self.panel_height = 500
        self.panel_x = (SCREEN_WIDTH - self.panel_width) // 2
        self.panel_y = (SCREEN_HEIGHT - self.panel_height) // 2
        
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # Item type colors
        self.type_colors = {
            'Seed': (139, 69, 19),      # Brown - Seed
            'Produce': (255, 215, 0),    # Gold - Produce
            'Material': (128, 128, 128), # Gray - Material
            'Feed': (255, 165, 0),       # Orange - Feed
            'Tool': (70, 130, 180),      # Blue - Tool
            'Misc': (200, 200, 200)      # Light Gray - Misc
        }
    
    def toggle(self, farm_id=None):
        """Toggle inventory display"""
        self.is_visible = not self.is_visible
        if self.is_visible and farm_id:
            self.farm_id = farm_id
            self.load_inventory()
    
    def load_inventory(self):
        """Load inventory data"""
        if self.farm_id:
            self.inventory_items = self.db.get_farm_inventory(self.farm_id)
            self.scroll_offset = 0
            # Calculate max scroll distance
            items_height = len(self.inventory_items) * 60 + 20
            self.max_scroll = max(0, items_height - (self.panel_height - 100))
    
    def handle_event(self, event):
        """Handle event"""
        if not self.is_visible:
            return False
        
        # Handle mouse wheel
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset = max(0, min(self.max_scroll, 
                                           self.scroll_offset - event.y * 20))
        
        # Handle close (click outside panel or ESC key)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_i:
                self.is_visible = False
                return True
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if click is outside panel
            panel_rect = pygame.Rect(self.panel_x, self.panel_y, 
                                    self.panel_width, self.panel_height)
            if not panel_rect.collidepoint(event.pos):
                self.is_visible = False
                return True
        
        return True  # Block event propagation to lower layers
    
    def draw(self):
        """Draw inventory interface"""
        if not self.is_visible:
            return
        
        # Semi-transparent background overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(COLOR_BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Inventory panel
        panel_rect = pygame.Rect(self.panel_x, self.panel_y, 
                                self.panel_width, self.panel_height)
        pygame.draw.rect(self.screen, COLOR_WHITE, panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLOR_BLACK, panel_rect, 3, border_radius=10)
        
        # Title
        title_text = self.font_large.render("Inventory", True, COLOR_DARK_GREEN)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, self.panel_y + 30))
        self.screen.blit(title_text, title_rect)
        
        # Close hint
        close_text = self.font_small.render("[I] or [ESC] to Close", True, COLOR_GRAY)
        self.screen.blit(close_text, (self.panel_x + self.panel_width - 150, self.panel_y + 10))
        
        # Separator line
        pygame.draw.line(self.screen, COLOR_GRAY, 
                        (self.panel_x + 20, self.panel_y + 60),
                        (self.panel_x + self.panel_width - 20, self.panel_y + 60), 2)
        
        # Create clipping area for scrolling
        content_rect = pygame.Rect(self.panel_x + 20, self.panel_y + 70,
                                   self.panel_width - 40, self.panel_height - 90)
        
        # Draw item list
        if not self.inventory_items:
            empty_text = self.font_medium.render("Inventory is empty", True, COLOR_GRAY)
            empty_rect = empty_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(empty_text, empty_rect)
        else:
            # Set clipping area
            self.screen.set_clip(content_rect)
            
            y_offset = self.panel_y + 80 - self.scroll_offset
            
            for item in self.inventory_items:
                item_y = y_offset
                
                # Only draw visible items
                if item_y + 50 < self.panel_y + 70 or item_y > self.panel_y + self.panel_height - 20:
                    y_offset += 60
                    continue
                
                # Item background box
                item_rect = pygame.Rect(self.panel_x + 30, item_y, 
                                       self.panel_width - 60, 50)
                pygame.draw.rect(self.screen, COLOR_LIGHT_GRAY, item_rect, border_radius=5)
                pygame.draw.rect(self.screen, COLOR_GRAY, item_rect, 1, border_radius=5)
                
                # Item type indicator (colored square)
                type_color = self.type_colors.get(item['ItemType'], COLOR_GRAY)
                type_rect = pygame.Rect(self.panel_x + 40, item_y + 10, 30, 30)
                pygame.draw.rect(self.screen, type_color, type_rect, border_radius=3)
                pygame.draw.rect(self.screen, COLOR_BLACK, type_rect, 1, border_radius=3)
                
                # Item type abbreviation
                type_abbr = {
                    'Seed': 'S',
                    'Produce': 'P',
                    'Material': 'M',
                    'Feed': 'F',
                    'Tool': 'T',
                    'Misc': 'X'
                }.get(item['ItemType'], '?')
                type_text = self.font_small.render(type_abbr, True, COLOR_WHITE)
                type_text_rect = type_text.get_rect(center=type_rect.center)
                self.screen.blit(type_text, type_text_rect)
                
                # Item name
                name_text = self.font_medium.render(item['Name'], True, COLOR_BLACK)
                self.screen.blit(name_text, (self.panel_x + 85, item_y + 8))
                
                # Item quantity
                quantity_text = self.font_small.render(
                    f"x{item['Quantity']}", 
                    True, COLOR_DARK_GREEN
                )
                self.screen.blit(quantity_text, (self.panel_x + 85, item_y + 28))
                
                # Item price
                price_text = self.font_small.render(
                    f"Price: {item['BasePrice']:.2f}", 
                    True, COLOR_BLUE
                )
                price_rect = price_text.get_rect(right=self.panel_x + self.panel_width - 50, 
                                                 centery=item_y + 25)
                self.screen.blit(price_text, price_rect)
                
                y_offset += 60
            
            # Cancel clipping
            self.screen.set_clip(None)
            
            # Scrollbar (if needed)
            if self.max_scroll > 0:
                scrollbar_height = max(30, (self.panel_height - 90) * 
                                      (self.panel_height - 90) / 
                                      (len(self.inventory_items) * 60 + 20))
                scrollbar_y = self.panel_y + 70 + (self.scroll_offset / self.max_scroll) * \
                             (self.panel_height - 90 - scrollbar_height)
                scrollbar_rect = pygame.Rect(self.panel_x + self.panel_width - 15, 
                                            scrollbar_y, 10, scrollbar_height)
                pygame.draw.rect(self.screen, COLOR_GRAY, scrollbar_rect, border_radius=5)
        
        # Statistics info
        total_items = sum(item['Quantity'] for item in self.inventory_items)
        total_value = sum(item['Quantity'] * item['BasePrice'] for item in self.inventory_items)
        
        stats_text = self.font_small.render(
            f"Types: {len(self.inventory_items)} | Total: {total_items} | Value: {total_value:.2f}",
            True, COLOR_GRAY
        )
        stats_rect = stats_text.get_rect(center=(SCREEN_WIDTH // 2, 
                                                  self.panel_y + self.panel_height - 15))
        self.screen.blit(stats_text, stats_rect)

