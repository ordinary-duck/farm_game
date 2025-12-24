# -*- coding: utf-8 -*-
"""
Overlay UI for showing currently selected tool / seed icons.
"""
import pygame

from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_WHITE,
    COLOR_BLACK,
    COLOR_YELLOW,
)


class OverlayUI:
    """Draws tool / seed icons on top of the HUD."""

    ICON_SIZE = 64
    SLOT_PADDING = 12
    TOOL_POS = (SCREEN_WIDTH - 40, SCREEN_HEIGHT - 40)
    SEED_POS = (SCREEN_WIDTH - 120, SCREEN_HEIGHT - 40)

    def __init__(self, screen, player, resources):
        self.screen = screen
        self.player = player
        self.resources = resources

        # Semi-transparent background for icon slots
        self.slot_surface = pygame.Surface(
            (self.ICON_SIZE + self.SLOT_PADDING * 2,
             self.ICON_SIZE + self.SLOT_PADDING * 2),
            pygame.SRCALPHA
        )
        self.slot_surface.fill((0, 0, 0, 160))

    def draw(self):
        """Draw both tool and seed slots."""
        self._draw_slot(
            self.TOOL_POS,
            self.player.selected_tool,
            label="Tool",
            active=True
        )
        self._draw_slot(
            self.SEED_POS,
            self.player.selected_seed,
            label="Seed",
            active=True
        )

    def _draw_slot(self, pos, key, label="", active=False):
        """Draw a single overlay slot at the given position."""
        x, y = pos
        slot_rect = self.slot_surface.get_rect(center=(x, y))
        self.screen.blit(self.slot_surface, slot_rect)

        # Draw accent border to indicate selection
        border_color = COLOR_YELLOW if active else COLOR_WHITE
        pygame.draw.rect(
            self.screen,
            border_color,
            slot_rect,
            2,
            border_radius=8
        )

        # Render icon if available
        icon = self.resources.overlay_images.get(key)
        if icon:
            scaled_icon = pygame.transform.scale(icon, (self.ICON_SIZE, self.ICON_SIZE))
            icon_rect = scaled_icon.get_rect(center=(x, y))
            self.screen.blit(scaled_icon, icon_rect)
        else:
            # Fallback text if icon missing
            font = pygame.font.Font(None, 20)
            text = font.render(key or "N/A", True, COLOR_WHITE)
            text_rect = text.get_rect(center=(x, y))
            self.screen.blit(text, text_rect)

        if label:
            font = pygame.font.Font(None, 22)
            label_surf = font.render(label, True, COLOR_WHITE)
            label_rect = label_surf.get_rect(midbottom=(x, slot_rect.top - 4))
            # subtle shadow for readability
            shadow_rect = label_rect.move(1, 1)
            shadow = font.render(label, True, COLOR_BLACK)
            self.screen.blit(shadow, shadow_rect)
            self.screen.blit(label_surf, label_rect)
