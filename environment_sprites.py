# -*- coding: utf-8 -*-
"""
Environment sprites (trees, apples, particles) used inside the farm scene.
"""
from __future__ import annotations

import os
import random
import pygame
from typing import Callable, Iterable, Tuple

from config import LAYERS, APPLE_POS, APPLE_SPAWN_CHANCE


class Generic(pygame.sprite.Sprite):
    """Generic sprite with a hitbox for collision/interaction."""

    def __init__(self, pos, surf, groups, z=LAYERS['main']):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = z
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2,
                                               -self.rect.height * 0.75)


class Particle(Generic):
    """Simple fading sprite used when apples fall or trees break."""

    def __init__(self, pos, surf, groups, z, duration=300):
        super().__init__(pos, surf, groups, z)
        self.start_time = pygame.time.get_ticks()
        self.duration = duration

        mask = pygame.mask.from_surface(self.image)
        white_surf = mask.to_surface()
        white_surf.set_colorkey((0, 0, 0))
        self.image = white_surf

    def update(self, dt):
        now = pygame.time.get_ticks()
        if now - self.start_time > self.duration:
            self.kill()


class Tree(Generic):
    """Interactive tree that can drop apples and be chopped for wood."""

    def __init__(self, pos, surf, groups, name, player_add: Callable[[str], None]):
        super().__init__(pos, surf, groups, z=LAYERS['main'])
        self.health = 5
        self.alive = True
        self.name = name
        base_dir = os.path.dirname(os.path.abspath(__file__))
        stump_file = "small.png" if name.lower() == "small" else "large.png"
        self.stump_surf = pygame.image.load(
            os.path.join(base_dir, "graphics", "stumps", stump_file)
        ).convert_alpha()

        self.apple_surf = pygame.image.load(
            os.path.join(base_dir, "graphics", "fruit", "apple.png")
        ).convert_alpha()
        self.apple_pos = APPLE_POS.get('Small' if name.lower() == 'small' else 'Large', [])
        self.apple_sprites = pygame.sprite.Group()
        self.create_fruit()

        self.player_add = player_add

    def create_fruit(self):
        for offset in self.apple_pos:
            if random.random() < APPLE_SPAWN_CHANCE:
                pos = (self.rect.left + offset[0], self.rect.top + offset[1])
                Generic(
                    pos=pos,
                    surf=self.apple_surf,
                    groups=[self.apple_sprites, self.groups()[0]],
                    z=LAYERS['fruit']
                )

    def damage(self):
        if not self.alive:
            return
        self.health -= 1
        self.drop_apple()
        self.check_death()

    def drop_apple(self):
        apples = self.apple_sprites.sprites()
        if apples:
            apple = random.choice(apples)
            Particle(
                pos=apple.rect.topleft,
                surf=apple.image,
                groups=self.groups()[0],
                z=LAYERS['fruit']
            )
            apple.kill()
            if self.player_add:
                self.player_add('apple')

    def check_death(self):
        if self.health > 0:
            return
        Particle(self.rect.topleft, self.image, self.groups()[0], LAYERS['fruit'], 400)
        self.image = self.stump_surf
        self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
        self.hitbox = self.rect.copy().inflate(-10, -self.rect.height * 0.6)
        self.apple_sprites.empty()
        self.alive = False
        if self.player_add:
            self.player_add('wood')

    def update(self, dt):
        pass  # Reserved for animations if needed

    def draw(self, surface: pygame.Surface, camera_x: float, camera_y: float):
        dest = self.rect.move(-camera_x, -camera_y)
        surface.blit(self.image, dest)
        for apple in self.apple_sprites:
            apple_dest = apple.rect.move(-camera_x, -camera_y)
            surface.blit(apple.image, apple_dest)


class Interaction(Generic):
    """Invisible trigger area for house beds, traders, etc."""

    def __init__(self, pos, size, name, groups=None):
        surf = pygame.Surface(size, pygame.SRCALPHA)
        groups = groups or []
        super().__init__(pos, surf, groups, z=LAYERS['main'])
        self.name = name
        self.hitbox = self.rect.copy()


