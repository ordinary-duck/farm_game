# -*- coding: utf-8 -*-
"""
TMX map loader that builds layered sprites for the farm scene.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, List, Optional

import pygame

try:
    from pytmx import TiledObjectGroup, TiledTileLayer, TiledImageLayer
    from pytmx.util_pygame import load_pygame
except ImportError as exc:
    raise ImportError(
        "pytmx is required for TMX map rendering. Install it with 'pip install pytmx'."
    ) from exc


@dataclass
class MapSprite:
    """A lightweight sprite used for rendering TMX layers."""

    image: pygame.Surface
    rect: pygame.Rect
    z: int


class FarmMap:
    """Loads TMX data and exposes renderable sprites plus collision rects."""

    def __init__(self, map_path: str, layers: Optional[Dict[str, int]] = None):
        self.map_path = map_path
        self.layers = layers or {}

        self.sprites: List[MapSprite] = []
        self.collision_rects: List[pygame.Rect] = []
        self.width = 0
        self.height = 0
        self.water_tile: Optional[pygame.Surface] = None

        self._load_map()
        self._load_water_tile()

    def _load_map(self):
        """Read TMX file and extract sprites/collisions."""
        tmx_data = load_pygame(self.map_path)
        self.tmx_data = tmx_data
        tile_w = tmx_data.tilewidth
        tile_h = tmx_data.tileheight
        self.width = tmx_data.width * tile_w
        self.height = tmx_data.height * tile_h

        for layer in tmx_data.visible_layers:
            if isinstance(layer, TiledTileLayer):
                z_val = self.layers.get(layer.name, self.layers.get('ground', 0))
                for x, y, surf in layer.tiles():
                    if not surf:
                        continue
                    rect = surf.get_rect(topleft=(x * tile_w, y * tile_h))
                    self.sprites.append(MapSprite(surf, rect, z_val))

            elif isinstance(layer, TiledObjectGroup):
                lname = (layer.name or '').lower()
                if lname == 'collision':# Åö×²
                    for obj in layer:
                        rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                        self.collision_rects.append(rect)
                else:
                    z_val = self.layers.get(layer.name, self.layers.get('main', 5))
                    for obj in layer:
                        surf = getattr(obj, 'image', None)
                        if not surf:
                            continue
                        rect = surf.get_rect(topleft=(obj.x, obj.y - surf.get_height()))
                        self.sprites.append(MapSprite(surf, rect, z_val))

            elif isinstance(layer, TiledImageLayer):
                surf = layer.image
                if not surf:
                    continue
                z_val = self.layers.get(layer.name, self.layers.get('ground', 0))
                rect = surf.get_rect(topleft=(0, 0))
                self.sprites.append(MapSprite(surf, rect, z_val))

    def _load_water_tile(self):
        """Load tiled water background so empty areas appear as water instead of solid color."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        water_path = os.path.join(base_dir, "graphics", "environment", "Water.png")
        if not os.path.exists(water_path):
            return
        try:
            self.water_tile = pygame.image.load(water_path).convert_alpha()
        except Exception as exc:
            print(f"Failed to load water tile {water_path}: {exc}")
            self.water_tile = None

    def draw(self, surface: pygame.Surface, camera_x: float, camera_y: float):
        """Draw sprites in layer order with a faux-3D effect."""
        screen_w = surface.get_width()
        screen_h = surface.get_height()

        # Draw tiled water first to cover void areas
        if self.water_tile:
            tile_w = self.water_tile.get_width()
            tile_h = self.water_tile.get_height()
            start_x = int((camera_x) // tile_w) - 1
            start_y = int((camera_y) // tile_h) - 1
            end_x = int((camera_x + screen_w) // tile_w) + 2
            end_y = int((camera_y + screen_h) // tile_h) + 2
            for ty in range(start_y, end_y):
                for tx in range(start_x, end_x):
                    dest_x = tx * tile_w - camera_x
                    dest_y = ty * tile_h - camera_y
                    surface.blit(self.water_tile, (dest_x, dest_y))

        if not self.sprites:
            return

        # Sort first by layer (z), then by vertical position for pseudo depth.
        for sprite in sorted(self.sprites, key=lambda s: (s.z, s.rect.bottom)):
            dest = sprite.rect.move(-camera_x, -camera_y)
            if dest.right < 0 or dest.left > surface.get_width():
                continue
            if dest.bottom < 0 or dest.top > surface.get_height():
                continue
            surface.blit(sprite.image, dest)
