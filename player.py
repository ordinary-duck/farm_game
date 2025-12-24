# -*- coding: utf-8 -*-
"""
Player Character Class
"""
import pygame
from config import (
    PLAYER_SIZE,
    PLAYER_SPEED,
    COLOR_BLUE,
    COLOR_WHITE,
    COLOR_BLACK,
    PLAYER_TOOL_OFFSET,
)
from resource_manager import get_resources


class Player:
    """Player Character"""
    
    def __init__(self, x, y):
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.speed = PLAYER_SPEED
        self.direction = "down"  # Direction: up, down, left, right
        self.is_moving = False
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.15  # Animation switch speed
        
        # Load character animations
        self.resources = get_resources()
        self.current_action = "down_idle"
        self.use_sprite_graphics = len(self.resources.character_animations) > 0

        # Sprite rect & hitbox (follow reference implementation style)
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        spawn_center = (x + self.width // 2, y + self.height // 2)
        self.rect.center = spawn_center
        hitbox_shrink_x = int(self.width * 0.35)
        hitbox_shrink_y = int(self.height * 0.5)
        self.hitbox = self.rect.copy().inflate(-hitbox_shrink_x, -hitbox_shrink_y)
        self.pos = pygame.math.Vector2(self.hitbox.center)
        self.direction_vector = pygame.math.Vector2()
        self.x = self.hitbox.left
        self.y = self.hitbox.top

        # Tool/seed selection for overlay UI
        self.tools = ['hoe', 'axe', 'water']
        self.seeds = ['corn', 'tomato']
        self.selected_tool_index = 0
        self.selected_seed_index = 0
        self.selected_tool = self.tools[0] if self.tools else None
        self.selected_seed = self.seeds[0] if self.seeds else None
        self.tool_target_offset = PLAYER_TOOL_OFFSET
        self.tool_animation_time = 0.0
        self.tool_action = None
        self.sleep = False

    def update(self, dt, keys_pressed, tile_size, max_x, max_y, obstacles=None):
        """Update player state and resolve collisions using sprite-style hitbox handling."""
        self.is_moving = False
        self.direction_vector = pygame.math.Vector2()
        if self.sleep:
            self.current_action = f"{self.direction}_idle"
            return
        
        # Handle keyboard input
        if keys_pressed[pygame.K_w] or keys_pressed[pygame.K_UP]:
            self.direction_vector.y = -1
            self.direction = "up"
            self.is_moving = True
        elif keys_pressed[pygame.K_s] or keys_pressed[pygame.K_DOWN]:
            self.direction_vector.y = 1
            self.direction = "down"
            self.is_moving = True
        
        if keys_pressed[pygame.K_a] or keys_pressed[pygame.K_LEFT]:
            self.direction_vector.x = -1
            self.direction = "left"
            self.is_moving = True
        elif keys_pressed[pygame.K_d] or keys_pressed[pygame.K_RIGHT]:
            self.direction_vector.x = 1
            self.direction = "right"
            self.is_moving = True
        
        # Prevent movement while tool animation is playing
        if self.tool_animation_time > 0:
            self.direction_vector.update(0, 0)
            self.is_moving = False
        
        self.move(dt, max_x, max_y, obstacles)
        
        using_tool = self.tool_animation_time > 0
        if using_tool:
            self.tool_animation_time = max(0.0, self.tool_animation_time - dt)
            if self.tool_animation_time <= 0:
                self.tool_action = None
        self.sleep = False

        # Update animation and action
        if using_tool:
            action = self.tool_action or f"{self.direction}_{self.selected_tool}"
            self.current_action = action
            self.animation_timer += dt
            frames = self.resources.character_animations.get(action, [])
            frame_count = max(1, len(frames))
            if self.animation_timer >= self.animation_speed:
                self.animation_frame = (self.animation_frame + 1) % frame_count
                self.animation_timer = 0
        elif self.is_moving:
            self.current_action = self.direction
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                frames = self.resources.character_animations.get(self.current_action, [])
                frame_count = len(frames) if frames else 4
                self.animation_frame = (self.animation_frame + 1) % frame_count
                self.animation_timer = 0
        else:
            self.current_action = f"{self.direction}_idle"
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                frames = self.resources.character_animations.get(self.current_action, [])
                frame_count = len(frames) if frames else 2
                self.animation_frame = (self.animation_frame + 1) % frame_count
                self.animation_timer = 0
    
    def draw(self, surface, camera_x=0, camera_y=0):
        """Draw player"""
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y - camera_y
        
        if self.use_sprite_graphics:
            self.draw_sprite(surface, screen_x, screen_y)
        else:
            self.draw_simple(surface, screen_x, screen_y)
    
    def draw_sprite(self, surface, screen_x, screen_y):
        """Draw player using sprite graphics"""
        frames = self.resources.character_animations.get(self.current_action, [])
        
        if frames and len(frames) > 0:
            frame_index = min(self.animation_frame, len(frames) - 1)
            sprite = frames[frame_index]
            scaled_sprite = pygame.transform.scale(sprite, (self.width, self.height))
            sprite_rect = scaled_sprite.get_rect(topleft=(int(screen_x), int(screen_y)))
            surface.blit(scaled_sprite, sprite_rect)
        else:
            self.draw_simple(surface, screen_x, screen_y)
    
    def draw_simple(self, surface, screen_x, screen_y):
        """Draw simple player character (fallback)"""
        center_x = int(screen_x + self.width // 2)
        center_y = int(screen_y + self.height // 2)
        radius = self.width // 2
        
        pygame.draw.circle(surface, COLOR_BLUE, (center_x, center_y), radius)
        pygame.draw.circle(surface, COLOR_BLACK, (center_x, center_y), radius, 2)
        
        eye_offset = radius // 3
        eye_size = radius // 5
        
        if self.direction == "down":
            left_eye = (center_x - eye_offset, center_y - eye_offset // 2)
            right_eye = (center_x + eye_offset, center_y - eye_offset // 2)
        elif self.direction == "up":
            left_eye = (center_x - eye_offset, center_y - eye_offset)
            right_eye = (center_x + eye_offset, center_y - eye_offset)
        elif self.direction == "left":
            left_eye = (center_x - eye_offset, center_y - eye_offset // 2)
            right_eye = (center_x, center_y - eye_offset // 2)
        else:  # right
            left_eye = (center_x, center_y - eye_offset // 2)
            right_eye = (center_x + eye_offset, center_y - eye_offset // 2)
        
        pygame.draw.circle(surface, COLOR_WHITE, left_eye, eye_size)
        pygame.draw.circle(surface, COLOR_WHITE, right_eye, eye_size)
        pygame.draw.circle(surface, COLOR_BLACK, left_eye, eye_size // 2)
        pygame.draw.circle(surface, COLOR_BLACK, right_eye, eye_size // 2)
        
        indicator_size = radius // 3
        if self.direction == "down":
            points = [
                (center_x, center_y + radius - 5),
                (center_x - indicator_size, center_y + radius // 2),
                (center_x + indicator_size, center_y + radius // 2)
            ]
        elif self.direction == "up":
            points = [
                (center_x, center_y - radius + 5),
                (center_x - indicator_size, center_y - radius // 2),
                (center_x + indicator_size, center_y - radius // 2)
            ]
        elif self.direction == "left":
            points = [
                (center_x - radius + 5, center_y),
                (center_x - radius // 2, center_y - indicator_size),
                (center_x - radius // 2, center_y + indicator_size)
            ]
        else:  # right
            points = [
                (center_x + radius - 5, center_y),
                (center_x + radius // 2, center_y - indicator_size),
                (center_x + radius // 2, center_y + indicator_size)
            ]
        
        pygame.draw.polygon(surface, COLOR_WHITE, points)
        
        if self.is_moving:
            offset = 2 if self.animation_frame % 2 == 0 else -2
            pygame.draw.circle(surface, (100, 150, 255, 100), 
                             (center_x, center_y + offset), radius - 2, 1)

    def cycle_tool(self, direction=1):
        """Switch equipped tool shown on the overlay."""
        if not self.tools:
            return
        self.selected_tool_index = (self.selected_tool_index + direction) % len(self.tools)
        self.selected_tool = self.tools[self.selected_tool_index]

    def cycle_seed(self, direction=1):
        """Switch selected seed shown on the overlay."""
        if not self.seeds:
            return
        self.selected_seed_index = (self.selected_seed_index + direction) % len(self.seeds)
        self.selected_seed = self.seeds[self.selected_seed_index]

    def get_tool_target(self):
        """World coordinates where the current tool should act."""
        offset = self.tool_target_offset.get(self.direction, (0, 0))
        center_x, center_y = self.rect.center
        return center_x + offset[0], center_y + offset[1]

    def start_tool_animation(self, duration=0.35):
        """Play the animation that corresponds to the currently selected tool."""
        action = f"{self.direction}_{self.selected_tool}"
        if not self.resources.character_animations.get(action):
            return
        self.tool_animation_time = duration
        self.tool_action = action
        self.animation_frame = 0
        self.animation_timer = 0
        self.is_moving = False
    
    def get_grid_position(self, tile_size):
        """Get player's grid coordinates"""
        grid_x = int(self.rect.centerx // tile_size)
        grid_y = int(self.rect.centery // tile_size)
        return grid_x, grid_y
    
    def get_rect(self):
        """Get player's hitbox rectangle (for interactions)"""
        return self.hitbox.copy()

    def set_position(self, x, y):
        """Teleport player to a specific world coordinate"""
        center = (x + self.width // 2, y + self.height // 2)
        self.rect.center = center
        self.hitbox.center = center
        self.pos = pygame.math.Vector2(center)
        self.x = self.hitbox.left
        self.y = self.hitbox.top

    def move(self, dt, max_x, max_y, obstacles):
        """Move with axis-aligned collision resolution identical to the reference player."""
        if self.direction_vector.length_squared() > 0:
            self.direction_vector = self.direction_vector.normalize()
        
        # Horizontal axis
        self.pos.x += self.direction_vector.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self._resolve_collisions('horizontal', obstacles)
        self.rect.center = self.hitbox.center
        
        # Vertical axis
        self.pos.y += self.direction_vector.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self._resolve_collisions('vertical', obstacles)
        self.rect.center = self.hitbox.center
        
        # Clamp the sprite to the world bounds, then sync hitbox
        world_rect = pygame.Rect(0, 0, max_x, max_y)
        self.rect.clamp_ip(world_rect)
        self.hitbox.center = self.rect.center
        self.pos.xy = self.hitbox.center
        self.x = self.hitbox.left
        self.y = self.hitbox.top

    def _resolve_collisions(self, axis, obstacles):
        if not obstacles:
            return
        for ob in obstacles:
            rect = ob.hitbox if hasattr(ob, "hitbox") else ob
            if not self.hitbox.colliderect(rect):
                continue
            if axis == 'horizontal':
                if self.direction_vector.x > 0:
                    self.hitbox.right = rect.left
                elif self.direction_vector.x < 0:
                    self.hitbox.left = rect.right
                self.pos.x = self.hitbox.centerx
            else:
                if self.direction_vector.y > 0:
                    self.hitbox.bottom = rect.top
                elif self.direction_vector.y < 0:
                    self.hitbox.top = rect.bottom
                self.pos.y = self.hitbox.centery
            self.rect.center = self.hitbox.center
