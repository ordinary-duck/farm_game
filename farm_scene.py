# -*- coding: utf-8 -*-
"""
Farm Game Main Scene
"""
import pygame
import json
import os
import random
from datetime import datetime
from config import *
from player import Player
from inventory_ui import InventoryUI
from resource_manager import get_resources
from overlay_ui import OverlayUI
from map_loader import FarmMap
from environment_sprites import Tree, Interaction
from transition import Transition


def get_font(size):
    """Get font with Chinese support"""
    if FONT_PATH:
        try:
            return pygame.font.Font(FONT_PATH, size)
        except:
            pass
    return pygame.font.Font(None, size)


class FarmScene:
    """Farm Main Scene"""
    
    def __init__(self, screen, db, player_data, farm_data):
        self.screen = screen
        self.db = db
        self.player_data = player_data
        self.farm_data = farm_data
        try:
            self.item_catalog = {item['Name'].lower(): item for item in self.db.get_all_items()}
        except Exception:
            self.item_catalog = {}
        
        self.font_large = get_font(FONT_SIZE_LARGE)
        self.font_medium = get_font(FONT_SIZE_MEDIUM)
        self.font_small = get_font(FONT_SIZE_SMALL)
        self.font_tiny = get_font(FONT_SIZE_TINY)
        
        # World alignment / collision data
        if isinstance(FARM_PLOT_OFFSET, (tuple, list)) and len(FARM_PLOT_OFFSET) == 2:
            self.plot_offset_x, self.plot_offset_y = FARM_PLOT_OFFSET
        else:
            self.plot_offset_x = self.plot_offset_y = 0
        if isinstance(FARM_PLAYER_SPAWN, (tuple, list)) and len(FARM_PLAYER_SPAWN) == 2:
            self.player_spawn = tuple(FARM_PLAYER_SPAWN)
        else:
            self.player_spawn = None
        self.world_obstacles = []
        self.map_collision_rects = []
        self.tilemap = None
        self.environment_group = pygame.sprite.Group()
        self.trees = []
        self.tree_hitboxes = []
        self.interaction_sprites = pygame.sprite.Group()
        self.day_counter = 1
        self.debug_draw = False

        # Load plot data
        self.plots = []
        self.load_plots()
        
        # Calculate farm size
        if self.plots:
            self.max_x = max(p['X'] for p in self.plots) + 1
            self.max_y = max(p['Y'] for p in self.plots) + 1
        else:
            self.max_x = 3
            self.max_y = 3
        
        self.map_width = self.max_x * TILE_SIZE
        self.map_height = self.max_y * TILE_SIZE
        if not self.player_spawn:
            self.player_spawn = (self.map_width // 2, self.map_height // 2)

        # TMX map (overrides world size/spawn if available)
        self.load_tmx_map()
        self.load_interactions_from_map()
        
        # Create player
        self.player = Player(*self.player_spawn)
        self.transition = Transition(self.start_new_day, self.player)
        
        # Camera
        self.camera_x = 0
        self.camera_y = 0
        
        # UI system
        self.inventory_ui = InventoryUI(screen, db)
        
        # Interaction hint
        self.interaction_hint = ""
        self.hint_timer = 0
        
        # Selected plot
        self.selected_plot = None
        
        # Load crop varieties
        self.crop_varieties = self.db.get_all_crop_varieties()
        self.seed_item_to_variety = {
            cv['SeedItemId']: cv for cv in self.crop_varieties if cv.get('SeedItemId')
        }
        
        # Message notifications
        self.messages = []  # [(text, timer), ...]
        
        # Show help
        self.show_help = True
        self.help_timer = 10.0  # Auto-hide after 10 seconds
        
        # Load graphics resources
        self.resources = get_resources()
        self.overlay_ui = OverlayUI(screen, self.player, self.resources)
        self.load_trees_from_map()

        # Load background image (skipped when TMX map is active)
        self.background_image = None
        self.load_background()
        self.build_world_obstacles()
        self.world_obstacles.extend(self.tree_hitboxes)
        if self.background_image:
            self.build_world_obstacles_from_background()
        
        # Ground tile surface (for tiled background)
        self.ground_tile = None
        if 'ground' in self.resources.world_images:
            self.ground_tile = self.resources.world_images['ground']
        
        # Environment decorations (trees, bushes, etc.)
        self.decorations = []
        self.init_decorations()
    
    def init_decorations(self):
        """Initialize environment decorations"""
        if self.tilemap or self.background_image:
            # The background image already contains baked-in environment art.
            self.decorations = []
            return
        import random
        
        # Add decorations around the farm
        decoration_types = [
            ('tree_small', 32, 48),
            ('tree_medium', 48, 64),
            ('bush', 24, 24),
            ('flower', 16, 16),
            ('sunflower', 20, 28),
            ('mushroom', 16, 16),
        ]
        
        # Place decorations in non-plot areas
        num_decorations = min(15, self.max_x * self.max_y // 3)
        
        for _ in range(num_decorations):
            # Random position
            x = random.randint(-1, self.max_x)
            y = random.randint(-1, self.max_y)
            
            # Check if position overlaps with plots
            is_plot = any(p['X'] == x and p['Y'] == y for p in self.plots)
            
            if not is_plot:
                # Random decoration type
                dec_type, width, height = random.choice(decoration_types)
                
                if dec_type in self.resources.objects_images:
                    self.decorations.append({
                        'type': dec_type,
                        'x': x * TILE_SIZE + random.randint(-10, 10),
                        'y': y * TILE_SIZE + random.randint(-10, 10),
                        'width': width,
                        'height': height,
                        'layer': 1 if 'tree' in dec_type else 0  # Trees behind, others in front
                    })

    def load_tmx_map(self):
        """Load TMX map and build layered sprites plus collision data."""
        if not USE_TMX_MAP:
            return
        
        map_path = TMX_MAP_PATH
        if not os.path.isabs(map_path):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            map_path = os.path.join(script_dir, map_path)
        
        if not os.path.exists(map_path):
            print(f"TMX map not found: {map_path}")
            return
        
        try:
            self.tilemap = FarmMap(map_path, LAYERS)
            self.map_collision_rects = [rect.copy() for rect in self.tilemap.collision_rects]
            self.map_width = max(self.map_width, self.tilemap.width)
            self.map_height = max(self.map_height, self.tilemap.height)
            
            spawn_x, spawn_y = self.player_spawn or (self.map_width // 2, self.map_height // 2)
            spawn_x = max(0, min(spawn_x, max(0, self.map_width - PLAYER_SIZE)))
            spawn_y = max(0, min(spawn_y, max(0, self.map_height - PLAYER_SIZE)))
            self.player_spawn = (spawn_x, spawn_y)
            
            print(f"Loaded TMX map: {map_path}")
        except Exception as e:
            print(f"Failed to load TMX map: {e}")
            self.tilemap = None
            self.map_collision_rects = []

    def load_interactions_from_map(self):
        """Load interaction trigger areas (bed, trader, etc.) from TMX."""
        self.interaction_sprites.empty()
        if not self.tilemap or not getattr(self.tilemap, 'tmx_data', None):
            return
        try:
            player_layer = self.tilemap.tmx_data.get_layer_by_name('Player')
        except (ValueError, KeyError):
            return
        for obj in player_layer:
            name = (obj.name or '').strip()
            if name.lower() == 'start' and not FARM_PLAYER_SPAWN:
                self.player_spawn = (obj.x, obj.y)
            elif name:
                Interaction(
                    (obj.x, obj.y),
                    (obj.width or 1, obj.height or 1),
                    name,
                    [self.interaction_sprites]
                )

    def load_trees_from_map(self):
        """Instantiate trees from the TMX object layer."""
        self.environment_group.empty()
        self.trees = []
        self.tree_hitboxes = []
        if not self.tilemap or not getattr(self.tilemap, 'tmx_data', None):
            return
        try:
            trees_layer = self.tilemap.tmx_data.get_layer_by_name('Trees')
        except (KeyError, ValueError):
            return
        surface_map = {
            'small': self.resources.objects_images.get('tree_small'),
            'large': self.resources.objects_images.get('tree_medium')
        }
        for obj in trees_layer:
            name = (obj.name or 'Small')
            surf = surface_map.get(name.lower())
            if not surf:
                continue
            pos_x = obj.x
            pos_y = obj.y - surf.get_height()
            tree = Tree((pos_x, pos_y), surf, [self.environment_group], name, self.collect_tree_item)
            self.trees.append(tree)
            self.tree_hitboxes.append(tree.hitbox)
    
    def load_background(self):
        """Load custom background image"""
        if USE_TMX_MAP and self.tilemap:
            # TMX map already provides full layered rendering.
            self.background_image = None
            return
        
        if FARM_BG_IMAGE:
            # Handle relative paths - convert to absolute path
            if not os.path.isabs(FARM_BG_IMAGE):
                script_dir = os.path.dirname(os.path.abspath(__file__))
                image_path = os.path.join(script_dir, FARM_BG_IMAGE)
            else:
                image_path = FARM_BG_IMAGE
            
            if os.path.exists(image_path):
                try:
                    original_image = pygame.image.load(image_path).convert_alpha()
                    if FARM_BG_SCALE_TO_SCREEN:
                        self.background_image = pygame.transform.scale(
                            original_image,
                            (SCREEN_WIDTH, SCREEN_HEIGHT)
                        )
                    else:
                        self.background_image = original_image
                    
                    # Update world bounds so the player can explore the entire image
                    self.map_width = self.background_image.get_width()
                    self.map_height = self.background_image.get_height()
                    
                    # Clamp spawn point to the available world size
                    spawn_x, spawn_y = self.player_spawn or (self.map_width // 2, self.map_height // 2)
                    spawn_x = max(0, min(spawn_x, max(0, self.map_width - self.player.width)))
                    spawn_y = max(0, min(spawn_y, max(0, self.map_height - self.player.height)))
                    self.player_spawn = (spawn_x, spawn_y)
                    self.player.set_position(spawn_x, spawn_y)
                    
                    self.update_camera()
                    
                    print(f"Loaded farm background image: {image_path}")
                except Exception as e:
                    print(f"Failed to load farm background image: {e}")
                    self.background_image = None
                    self.world_obstacles = []
            else:
                print(f"Farm background image not found: {image_path}")
                self.background_image = None
                self.world_obstacles = []
        else:
            self.background_image = None
            self.world_obstacles = []
    
    def load_plots(self):
        """Load plot data"""
        self.plots = self.db.get_farm_plots(self.farm_data['FarmId'])
        self.apply_plot_offsets()

    def apply_plot_offsets(self):
        """Pre-compute world positions for each plot so we can align with the background map"""
        for plot in self.plots:
            world_x = self.plot_offset_x + plot['X'] * TILE_SIZE
            world_y = self.plot_offset_y + plot['Y'] * TILE_SIZE
            plot['world_x'] = world_x
            plot['world_y'] = world_y
            plot['world_rect'] = pygame.Rect(world_x, world_y, TILE_SIZE, TILE_SIZE)
            plot['WaterLevel'] = plot.get('WaterLevel') or 0
            plot['FertilizerLevel'] = plot.get('FertilizerLevel') or 0

    def find_variety_by_keyword(self, keyword):
        """Locate crop variety by fuzzy keyword (corn/tomato)."""
        if not keyword:
            return None
        key = keyword.lower()
        for cv in self.crop_varieties:
            if key in cv['Name'].lower():
                return cv
        return None

    def build_world_obstacles(self):
        """Create pygame.Rect objects for impassable structures or voids"""
        self.world_obstacles = [rect.copy() for rect in self.map_collision_rects]
        for rect_data in FARM_OBSTACLE_RECTS:
            if not isinstance(rect_data, (tuple, list)) or len(rect_data) != 4:
                continue
            x, y, w, h = rect_data
            self.world_obstacles.append(pygame.Rect(x, y, w, h))

    def build_world_obstacles_from_background(self, alpha_threshold=10, solid_ratio_threshold=0.2):
        """
        Sample the background image and add collision rectangles wherever the image
        is mostly transparent (water/void areas). This keeps the player from walking
        outside the painted part of the map without having to hand-encode every edge.
        """
        if not self.background_image:
            return

        opaque_mask = pygame.mask.from_surface(self.background_image, alpha_threshold)
        width, height = opaque_mask.get_size()
        sample_size = max(16, TILE_SIZE)  # Align sampling with tile resolution
        world_bounds = pygame.Rect(0, 0, width, height)
        filled_mask_cache = {}

        def get_filled_mask(size):
            mask = filled_mask_cache.get(size)
            if mask is None:
                mask = pygame.Mask(size)
                mask.fill()
                filled_mask_cache[size] = mask
            return mask

        for top in range(0, height, sample_size):
            tile_h = min(sample_size, height - top)
            for left in range(0, width, sample_size):
                tile_w = min(sample_size, width - left)
                tile_area = tile_w * tile_h
                if tile_area == 0:
                    continue

                tile_mask = get_filled_mask((tile_w, tile_h))
                solid_pixels = opaque_mask.overlap_area(tile_mask, (left, top))
                solid_ratio = solid_pixels / tile_area

                if solid_ratio < solid_ratio_threshold:
                    rect = pygame.Rect(left, top, tile_w, tile_h)
                    rect.inflate_ip(4, 4)  # Expand slightly so collision happens before leaving art
                    rect.clamp_ip(world_bounds)
                    self.world_obstacles.append(rect)

    def find_item_catalog_entry(self, candidates):
        if not isinstance(candidates, (list, tuple)):
            candidates = [candidates]
        for name in candidates:
            item = self.item_catalog.get(name.lower())
            if item:
                return item
        return None

    def collect_tree_item(self, tag):
        """Add apples/wood from trees into inventory (if possible)."""
        keywords = {
            'apple': ['apple', '鑻规灉'],
            'wood': ['wood', '鏈ㄦ潗']
        }
        candidate = keywords.get(tag.lower(), [tag])
        item_entry = self.find_item_catalog_entry(candidate)
        if item_entry:
            try:
                if self.db.update_inventory(self.farm_data['FarmId'], item_entry['ItemId'], 1):
                    self.add_message(f"Obtained {item_entry['Name']} x1", 1.5)
                    self.inventory_ui.load_inventory()
                    return
            except Exception:
                pass
        self.add_message(f"Obtained {tag} (not registered in item catalog)锛堟湭鍦ㄧ墿鍝佽〃涓敞鍐岋級", 1.5)
    
    def add_message(self, text, duration=3.0):
        """Add message notification"""
        self.messages.append({'text': text, 'timer': duration})
    
    def update(self, dt):
        """Update scene"""
        if self.inventory_ui.is_visible:
            return  # Pause game update when inventory is open
        
        # Get key states
        keys_pressed = pygame.key.get_pressed()
        
        # Update player
        self.player.update(
            dt,
            keys_pressed,
            TILE_SIZE,
            self.map_width,
            self.map_height,
            self.world_obstacles
        )
        self.environment_group.update(dt)
        
        # Update camera
        self.update_camera()
        
        # Check nearby plots
        self.check_nearby_plots()
        
        # Update messages
        for msg in self.messages[:]:
            msg['timer'] -= dt
            if msg['timer'] <= 0:
                self.messages.remove(msg)
        
        # Update help timer
        if self.show_help:
            self.help_timer -= dt
            if self.help_timer <= 0:
                self.show_help = False
    
    def update_camera(self):
        """Update camera position"""
        # Make camera follow player
        target_x = self.player.x + self.player.width // 2 - SCREEN_WIDTH // 2
        target_y = self.player.y + self.player.height // 2 - SCREEN_HEIGHT // 2
        
        # Limit camera range
        self.camera_x = max(0, min(target_x, self.map_width - SCREEN_WIDTH))
        self.camera_y = max(0, min(target_y, self.map_height - SCREEN_HEIGHT))
        
        # If map is smaller than screen, center display
        if self.map_width < SCREEN_WIDTH:
            self.camera_x = -(SCREEN_WIDTH - self.map_width) // 2
        if self.map_height < SCREEN_HEIGHT:
            self.camera_y = -(SCREEN_HEIGHT - self.map_height) // 2
    
    def check_nearby_plots(self):
        """Check plots near player using world-space rectangles"""
        player_rect = self.player.get_rect()
        interaction_zone = player_rect.inflate(40, 40)
        
        self.selected_plot = None
        min_dist = float('inf')
        
        for plot in self.plots:
            plot_rect = plot.get('world_rect')
            if not plot_rect:
                continue
            
            if interaction_zone.colliderect(plot_rect):
                dx = plot_rect.centerx - player_rect.centerx
                dy = plot_rect.centery - player_rect.centery
                dist = dx * dx + dy * dy
                if dist < min_dist:
                    min_dist = dist
                    self.selected_plot = plot
        
        # Update interaction hint
        if self.selected_plot:
            status = self.selected_plot['Status']
            if status == 'Empty':
                self.interaction_hint = "[Space] Plant Crop"
            elif status == 'Growing':
                self.interaction_hint = "[Space] Check Growth"
            elif status == 'Mature':
                self.interaction_hint = "[Space] Harvest Crop"
            elif status == 'Withered':
                self.interaction_hint = "[Space] Clear Withered"
        else:
            self.interaction_hint = ""

    def get_target_plot(self):
        """Return plot located at the player's tool target point."""
        target_x, target_y = self.player.get_tool_target()
        for plot in self.plots:
            rect = plot.get('world_rect')
            if rect and rect.collidepoint(target_x, target_y):
                return plot
        return None

    def get_target_tree(self):
        """Return tree under the player's tool target, if any."""
        target_x, target_y = self.player.get_tool_target()
        for tree in self.trees:
            if tree.hitbox.collidepoint(target_x, target_y):
                return tree
        return None
    
    def handle_event(self, event):
        """Handle event"""
        # Handle UI events first
        if self.inventory_ui.is_visible:
            if self.inventory_ui.handle_event(event):
                return None
        
        if event.type == pygame.KEYDOWN:
            # Open inventory
            if event.key == pygame.K_i:
                self.inventory_ui.toggle(self.farm_data['FarmId'])
                return None
            
            # Toggle help
            if event.key == pygame.K_h:
                self.show_help = not self.show_help
                return None
            
            # Interact
            if event.key == pygame.K_SPACE:
                if not self.use_selected_tool():
                    self.interact_with_plot()
                return None
            
            # Use seed
            if event.key == pygame.K_LCTRL:
                self.use_selected_seed()
                return None
            
            # Interact with environment triggers (bed, trader)
            if event.key == pygame.K_RETURN:
                if self.handle_interaction_trigger():
                    return None
            
            # Cycle tools
            if event.key == pygame.K_q:
                self.player.cycle_tool(-1)
                return None
            if event.key == pygame.K_e:
                self.player.cycle_tool(1)
                return None
            
            # Cycle seeds
            if event.key == pygame.K_z:
                self.player.cycle_seed(-1)
                return None
            if event.key == pygame.K_x:
                self.player.cycle_seed(1)
                return None
            
            # Toggle debug overlay
            if event.key == pygame.K_F3:
                self.debug_draw = not self.debug_draw
                return None
            
            # Return to login screen
            if event.key == pygame.K_ESCAPE:
                return "login"
        
        return None
    
    def interact_with_plot(self):
        """Interact with plot"""
        if not self.selected_plot:
            return
        
        plot_id = self.selected_plot['PlotId']
        status = self.selected_plot['Status']
        
        if status == 'Empty':
            # Plant crop
            self.plant_crop(plot_id)
        elif status == 'Growing':
            # Check growth progress
            self.check_growth(self.selected_plot)
        elif status == 'Mature':
            # Harvest crop
            self.harvest_crop(plot_id)
        elif status == 'Withered':
            # Clear withered
            self.clear_withered(plot_id)

    def handle_interaction_trigger(self):
        """Check if the player is overlapping any interaction trigger."""
        interaction = self.check_player_interaction()
        if not interaction:
            self.add_message("Nothing to interact with here.", 1.5)
            return False
        
        name = interaction.name.lower()
        if name == 'bed':  #碰到床就睡          
            if not self.player.sleep:
                self.player.sleep = True
                self.add_message('Going to bed...', 1.5)
            return True
        if name == 'trader':
            self.add_message("Trader is not available yet.", 1.5)
            return True
        
        self.add_message(f"Interacted with {interaction.name}", 1.5)
        return True
    # 检查玩家是否与交互触发器碰撞
    def check_player_interaction(self):
        """Return the interaction sprite the player is currently touching."""
        player_rect = self.player.hitbox
        for sprite in self.interaction_sprites:
            if sprite.rect.colliderect(player_rect):
                return sprite # true 有碰撞 
        return None# false 没有碰撞

    # 新的一天开始
    def start_new_day(self):
        """Simple daily reset hook triggered when sleeping in the bed."""
        raining = random.random() < 0.35
        if raining:
            for plot in self.plots:
                try:
                    new_water = min(100, (plot.get('WaterLevel') or 0) + 25)
                    self.db.set_plot_levels(plot['PlotId'], water_level=new_water)
                except Exception:
                    pass
        self.day_counter += 1
        self.load_plots()
        self.inventory_ui.load_inventory()
        self.add_message(f"Day {self.day_counter} begins!", 2.5)

    def use_selected_tool(self):
        """Trigger the equipped tool on the tile in front of the player."""
        tool = self.player.selected_tool
        result = False
        plot = self.get_target_plot()
        if tool == 'water' and plot:
            result = self.apply_water(plot)
        elif tool == 'hoe' and plot:
            result = self.apply_fertilizer(plot)
        elif tool == 'axe':
            if plot:
                result = self.use_axe_on_plot(plot)
            else:
                tree = self.get_target_tree()
                if tree:
                    tree.damage()
                    result = True

        if tool:
            self.player.start_tool_animation()
            return True
        return result

    def use_selected_seed(self):
        """Plant the currently selected seed on the targeted plot."""
        plot = self.get_target_plot()
        if not plot:
            self.add_message("No soil ahead, but you swung the seeds anyway.", 1.5)
            self.player.start_tool_animation()
            return

        if plot['Status'] != 'Empty':
            self.add_message("Target plot is not empty.", 2.0)
            self.player.start_tool_animation()
            return

        preferred_variety = self.find_variety_by_keyword(self.player.selected_seed)
        if not preferred_variety:
            self.add_message("No crop variety matches the selected seed.", 2.0)
            self.player.start_tool_animation()
            return

        if self.plant_crop(plot['PlotId'], preferred_variety):
            self.add_message(f"Sowed {preferred_variety['Name']}", 2.0)
            self.load_plots()
        self.player.start_tool_animation()

    def apply_water(self, plot, amount=30):
        """Increase soil moisture for the given plot."""
        new_water = min(100, (plot.get('WaterLevel') or 0) + amount)
        if new_water == plot.get('WaterLevel'):
            self.add_message("Soil moisture is already sufficient.", 1.5)
            return True
        if self.db.set_plot_levels(plot['PlotId'], water_level=new_water):
            plot['WaterLevel'] = new_water
            self.add_message("Water +30", 1.5)
            return True
        self.add_message("Watering failed.", 1.5)
        return False

    def apply_fertilizer(self, plot, amount=20):
        """Simulate hoeing by increasing fertilizer level."""
        new_fert = min(100, (plot.get('FertilizerLevel') or 0) + amount)
        if new_fert == plot.get('FertilizerLevel'):
            self.add_message("Soil is already fertile.", 1.5)
            return True
        if self.db.set_plot_levels(plot['PlotId'], fertilizer_level=new_fert):
            plot['FertilizerLevel'] = new_fert
            self.add_message("Hoeing improved fertility.", 1.5)
            return True
        self.add_message("Hoeing failed.", 1.5)
        return False

    def use_axe_on_plot(self, plot):
        """Use axe to harvest mature crops or clear withered ones."""
        if plot['Status'] == 'Mature':
            self.selected_plot = plot
            self.harvest_crop(plot['PlotId'])
            return True
        if plot['Status'] == 'Withered':
            if self.db.reset_plot(plot['PlotId']):
                self.add_message("Cleared withered crop", 2.0)
                self.load_plots()
                self.inventory_ui.load_inventory()
                return True
            self.add_message("Clear failed", 1.5)
            return False
        self.add_message("Axe can be used only on mature or withered crops", 1.5)
        return False
    
    def plant_crop(self, plot_id, preferred_variety=None):
        """Plant crop"""
        # Check if there are seeds
        inventory = self.db.get_farm_inventory(self.farm_data['FarmId'])
        seeds = [item for item in inventory if item['ItemType'] == 'Seed' and item['Quantity'] > 0]
        
        if not seeds:
            self.add_message("No seeds to plant!", 2.0)
            return

        target_variety = preferred_variety
        if preferred_variety:
            seeds = [s for s in seeds if s['ItemId'] == preferred_variety['SeedItemId']]
            if not seeds:
                self.add_message("No matching seed in inventory", 2.0)
                return
        
        # Use first available seed
        seed = seeds[0]
        
        # Find corresponding crop variety
        crop_variety = target_variety or self.seed_item_to_variety.get(seed['ItemId'])
        
        if not crop_variety:
            self.add_message("Crop variety not found!", 2.0)
            return
        
        # Deduct seed
        if self.db.update_inventory(self.farm_data['FarmId'], seed['ItemId'], -1):
            # Plant
            if self.db.plant_crop(plot_id, crop_variety['CropVarietyId']):
                self.add_message(f"Planted {crop_variety['Name']}!", 2.0)
                
                # Log action
                meta = json.dumps({
                    'PlotId': plot_id,
                    'CropVarietyId': crop_variety['CropVarietyId']
                }, ensure_ascii=False)
                self.db.log_action(self.player_data['PlayerId'], 
                                  self.farm_data['FarmId'], 
                                  'Plant', meta)
                
                # Reload plots
                self.load_plots()
                return True
            else:
                self.add_message("Planting failed!", 2.0)
                # Return seed
                self.db.update_inventory(self.farm_data['FarmId'], seed['ItemId'], 1)
        else:
            self.add_message("Insufficient seeds!", 2.0)
        return False
    
    def check_growth(self, plot):
        """Check growth progress"""
        if not plot['PlantedAt'] or not plot['GrowthHours']:
            return
        
        planted_time = plot['PlantedAt']
        growth_hours = plot['GrowthHours']
        
        # Calculate elapsed time
        now = datetime.utcnow()
        elapsed = (now - planted_time).total_seconds() / 3600  # Convert to hours
        
        progress = min(100, int(elapsed / growth_hours * 100))
        remaining = max(0, growth_hours - elapsed)
        
        self.add_message(
            f"{plot['CropName']}: {progress}% complete ({remaining:.1f}h left)",
            3.0
        )
    
    def harvest_crop(self, plot_id):
        """Harvest crop"""
        plot = self.selected_plot
        if not plot or not plot['CropVarietyId']:
            return
        
        # Find crop variety info
        crop_variety = None
        for cv in self.crop_varieties:
            if cv['CropVarietyId'] == plot['CropVarietyId']:
                crop_variety = cv
                break
        
        if not crop_variety:
            self.add_message("Crop info not found!", 2.0)
            return
        
        # Calculate yield (simplified version, considering soil quality)
        base_yield = crop_variety['BaseYield']
        soil_quality = self.farm_data['SoilQuality']
        water_level = plot['WaterLevel']
        fertilizer_level = plot['FertilizerLevel']
        
        yield_amount = int(base_yield * (1 + soil_quality / 200.0 + 
                                        water_level / 200.0 + 
                                        fertilizer_level / 100.0))
        yield_amount = max(1, yield_amount)
        
        # Add produce to inventory
        produce_item_id = crop_variety['ProduceItemId']
        if self.db.update_inventory(self.farm_data['FarmId'], produce_item_id, yield_amount):
            # Clear plot
            if self.db.harvest_plot(plot_id):
                self.add_message(f"Harvested {yield_amount} {plot['CropName']}!", 3.0)
                
                # Log action
                meta = json.dumps({
                    'PlotId': plot_id,
                    'Yield': yield_amount
                }, ensure_ascii=False)
                self.db.log_action(self.player_data['PlayerId'],
                                  self.farm_data['FarmId'],
                                  'Harvest', meta)
                
                # Reload
                self.load_plots()
                self.inventory_ui.load_inventory()
            else:
                self.add_message("Harvest failed!", 2.0)
        else:
            self.add_message("Inventory full!", 2.0)
    
    def clear_withered(self, plot_id):
        """Clear withered crop"""
        if self.db.reset_plot(plot_id):
            self.add_message("Cleared withered crop", 2.0)
            self.load_plots()
        else:
            self.add_message("Clear failed!", 2.0)
    
    def draw(self):
        """Draw scene"""
        # Draw background / TMX map
        if self.tilemap:
            self.screen.fill(COLOR_GREEN)
            self.tilemap.draw(self.screen, self.camera_x, self.camera_y)
        elif self.background_image:
            # Always clear the frame so semi-transparent pixels won't leave trails
            self.screen.fill(COLOR_GREEN)
            self.screen.blit(self.background_image, (-self.camera_x, -self.camera_y))
        else:
            # Draw tiled ground if available
            if self.ground_tile:
                self.draw_tiled_ground()
            else:
                self.screen.fill(COLOR_GREEN)
        
        # Draw decorations (layer 0 - behind player)
        self.draw_decorations(layer=0)
        
        # Draw plots
        self.draw_plots()
        
        # Draw dynamic entities (trees, apples, particles, player)
        self.draw_dynamic_entities()
        
        # Draw decorations (layer 1 - in front of player for depth effect)
        self.draw_decorations(layer=1)
        
        # Draw UI
        self.draw_ui()
        
        # Draw inventory
        self.inventory_ui.draw()

        # Draw overlay icons
        self.overlay_ui.draw()
        
        # Draw help
        if self.show_help:
            self.draw_help()

        if self.player.sleep:
            self.transition.play()
    
    def draw_tiled_ground(self):
        """Draw tiled ground background"""
        if not self.ground_tile:
            return
        
        tile_w = self.ground_tile.get_width()
        tile_h = self.ground_tile.get_height()
        
        # Calculate visible area
        start_x = max(0, int(self.camera_x // tile_w))
        start_y = max(0, int(self.camera_y // tile_h))
        end_x = int((self.camera_x + SCREEN_WIDTH) // tile_w) + 2
        end_y = int((self.camera_y + SCREEN_HEIGHT) // tile_h) + 2
        
        # Draw tiles
        for ty in range(start_y, end_y):
            for tx in range(start_x, end_x):
                screen_x = tx * tile_w - self.camera_x
                screen_y = ty * tile_h - self.camera_y
                self.screen.blit(self.ground_tile, (screen_x, screen_y))
    
    def draw_decorations(self, layer=0):
        """Draw environment decorations"""
        for dec in self.decorations:
            if dec['layer'] != layer:
                continue
            
            x = dec['x'] - self.camera_x
            y = dec['y'] - self.camera_y
            
            # Only draw if on screen
            if (x + dec['width'] < 0 or x > SCREEN_WIDTH or
                y + dec['height'] < 0 or y > SCREEN_HEIGHT):
                continue
            
            # Get decoration image
            dec_img = self.resources.objects_images.get(dec['type'])
            if dec_img:
                # Scale to desired size
                scaled_img = pygame.transform.scale(dec_img, (dec['width'], dec['height']))
                self.screen.blit(scaled_img, (x, y))

    def draw_dynamic_entities(self):
        """Draw trees/apples/particles along with the player, sorted by y."""
        sprites = list(self.environment_group.sprites())
        sprites.append(self.player)
        sprites.sort(key=lambda spr: (getattr(spr,'z', LAYERS['main']), spr.rect.bottom if hasattr(spr,'rect') else 0))
        for sprite in sprites:
            if sprite is self.player:
                self.player.draw(self.screen, self.camera_x, self.camera_y)
                if self.debug_draw:
                    self._draw_player_debug()
            else:
                dest = sprite.rect.move(-self.camera_x, -self.camera_y)
                self.screen.blit(sprite.image, dest)

    def _draw_player_debug(self):
        """Draw debug rectangles showing player sprite and hitbox."""
        offset_rect = self.player.rect.move(-self.camera_x, -self.camera_y)
        pygame.draw.rect(self.screen, (255, 0, 0), offset_rect, 2)
        hitbox_rect = self.player.hitbox.copy()
        hitbox_rect.center = offset_rect.center
        pygame.draw.rect(self.screen, (0, 200, 0), hitbox_rect, 2)
        dx, dy = PLAYER_TOOL_OFFSET.get(self.player.direction, (0, 0))
        target_pos = hitbox_rect.centerx + dx, hitbox_rect.centery + dy
        pygame.draw.circle(self.screen, (0, 120, 255), target_pos, 5)
    
    def draw_plots(self):
        """Draw all plots"""
        for plot in self.plots:
            plot_rect = plot.get('world_rect')
            if not plot_rect:
                continue
            x = plot_rect.x - self.camera_x
            y = plot_rect.y - self.camera_y
            
            # Only draw plots within screen
            if (x + TILE_SIZE < 0 or x > SCREEN_WIDTH or
                y + TILE_SIZE < 0 or y > SCREEN_HEIGHT):
                continue
            
            # Draw soil background
            self.draw_soil_tile(plot, x, y)
            
            # Border
            border_color = COLOR_YELLOW if plot == self.selected_plot else COLOR_BLACK
            border_width = 3 if plot == self.selected_plot else 1
            rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(self.screen, border_color, rect, border_width)
            
            # Draw crop info
            if plot['Status'] in ['Growing', 'Mature', 'Withered']:
                if plot['CropName']:
                    # Crop name
                    name_text = self.font_tiny.render(plot['CropName'], True, COLOR_BLACK)
                    name_rect = name_text.get_rect(center=(x + TILE_SIZE // 2, y + 15))
                    
                    # Text background
                    bg_rect = name_rect.inflate(4, 2)
                    pygame.draw.rect(self.screen, COLOR_WHITE, bg_rect)
                    self.screen.blit(name_text, name_rect)
                
                # Draw crop visual stage (simple graphics)
                self.draw_crop_visual(plot, x, y)
            
            # Draw coordinates (for debugging)
            coord_text = self.font_tiny.render(f"({plot['X']},{plot['Y']})", 
                                              True, COLOR_GRAY)
            self.screen.blit(coord_text, (x + 2, y + TILE_SIZE - 15))
    
    def draw_crop_visual(self, plot, x, y):
        """Draw crop visual effect"""
        status = plot['Status']
        crop_name = plot.get('CropName', '').lower()
        
        # Try to use real crop graphics
        crop_image = self.get_crop_image(plot)
        
        if crop_image:
            # Scale and center the crop image
            crop_rect = crop_image.get_rect()
            crop_rect.center = (x + TILE_SIZE // 2, y + TILE_SIZE // 2)
            self.screen.blit(crop_image, crop_rect)
        else:
            # Fallback to simple graphics
            center_x = x + TILE_SIZE // 2
            center_y = y + TILE_SIZE // 2 + 5
            
            if status == 'Growing':
                # Small sprout (green)
                pygame.draw.circle(self.screen, COLOR_DARK_GREEN, 
                                 (center_x, center_y), 8)
                pygame.draw.line(self.screen, COLOR_DARK_GREEN,
                               (center_x, center_y - 8),
                               (center_x, center_y - 18), 2)
            elif status == 'Mature':
                # Mature crop (golden)
                pygame.draw.circle(self.screen, COLOR_YELLOW,
                                 (center_x, center_y - 5), 12)
                pygame.draw.line(self.screen, COLOR_DARK_GREEN,
                               (center_x, center_y + 7),
                               (center_x, center_y + 15), 3)
                # Flashing effect
                if pygame.time.get_ticks() % 1000 < 500:
                    pygame.draw.circle(self.screen, COLOR_ORANGE,
                                     (center_x, center_y - 5), 14, 2)
            elif status == 'Withered':
                # Withered (gray)
                pygame.draw.line(self.screen, COLOR_GRAY,
                               (center_x - 8, center_y + 8),
                               (center_x + 8, center_y - 8), 2)
                pygame.draw.line(self.screen, COLOR_GRAY,
                               (center_x - 8, center_y - 8),
                               (center_x + 8, center_y + 8), 2)
    
    def draw_soil_tile(self, plot, x, y):
        """Draw soil tile with proper graphics"""
        status = plot['Status']
        rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        
        # Try to use real soil graphics
        if status != 'Empty' and 'o' in self.resources.soil_images:
            # Use the basic soil tile
            soil_img = self.resources.soil_images['o']
            scaled_soil = pygame.transform.scale(soil_img, (TILE_SIZE, TILE_SIZE))
            self.screen.blit(scaled_soil, (x, y))
            
            # If watered, add water overlay
            if plot.get('WaterLevel', 0) > 50:
                if self.resources.soil_water_images:
                    # Use animated water overlay
                    frame_idx = (pygame.time.get_ticks() // 200) % len(self.resources.soil_water_images)
                    water_img = self.resources.soil_water_images[frame_idx]
                    scaled_water = pygame.transform.scale(water_img, (TILE_SIZE, TILE_SIZE))
                    self.screen.blit(scaled_water, (x, y))
        else:
            # Fallback to colored rectangles
            color = PLOT_COLORS.get(status, COLOR_BROWN)
            pygame.draw.rect(self.screen, color, rect)
    
    def get_crop_image(self, plot):
        """Get crop image based on plot data"""
        if not plot or plot['Status'] == 'Empty':
            return None
        
        crop_name = plot.get('CropName', '').lower()
        status = plot['Status']
        
        # Determine growth stage (0-3 for most crops)
        if status == 'Withered':
            return None  # No specific image for withered
        
        growth_stage = 0
        if status == 'Growing':
            # Calculate growth progress
            if plot.get('PlantedAt') and plot.get('GrowthHours'):
                planted_time = plot['PlantedAt']
                growth_hours = plot['GrowthHours']
                now = datetime.utcnow()
                elapsed = (now - planted_time).total_seconds() / 3600
                progress = min(1.0, elapsed / growth_hours)
                # Map progress to stage 0-2 for growing
                growth_stage = min(2, int(progress * 3))
        elif status == 'Mature':
            growth_stage = 3  # Final stage
        
        # Try to get the crop image
        if '鐜夌背' in crop_name or 'corn' in crop_name:
            return self.resources.get_fruit_growth('corn', growth_stage)
        elif '鐣寗' in crop_name or 'tomato' in crop_name:
            return self.resources.get_fruit_growth('tomato', growth_stage)
        elif '鑻规灉' in crop_name or 'apple' in crop_name:
            if status == 'Mature':
                return self.resources.fruit_images.get('apple')
        
        return None
    
    def draw_ui(self):
        """Draw UI elements"""
        # Top info bar
        panel_height = 80
        panel_rect = pygame.Rect(0, 0, SCREEN_WIDTH, panel_height)
        panel_surface = pygame.Surface((SCREEN_WIDTH, panel_height))
        panel_surface.set_alpha(200)
        panel_surface.fill(COLOR_BLACK)
        self.screen.blit(panel_surface, (0, 0))
        
        # Player info
        y_pos = 10
        player_text = self.font_medium.render(
            f"Player: {self.player_data['Name']} (Lv.{self.player_data['Level']})",
            True, COLOR_WHITE
        )
        self.screen.blit(player_text, (20, y_pos))
        
        # Farm info
        farm_text = self.font_small.render(
            f"Farm: {self.farm_data['Name']} | Soil Quality: {self.farm_data['SoilQuality']}",
            True, COLOR_LIGHT_GRAY
        )
        self.screen.blit(farm_text, (20, y_pos + 30))
        
        # Currency info
        gold_text = self.font_medium.render(
            f"Gold: {self.player_data['CurrencyGold']:.2f}",
            True, COLOR_YELLOW
        )
        gold_rect = gold_text.get_rect(right=SCREEN_WIDTH - 150, y=y_pos)
        self.screen.blit(gold_text, gold_rect)
        
        gem_text = self.font_medium.render(
            f"Gem: {self.player_data['CurrencyGem']}",
            True, COLOR_BLUE
        )
        gem_rect = gem_text.get_rect(right=SCREEN_WIDTH - 20, y=y_pos)
        self.screen.blit(gem_text, gem_rect)
        
        # Shortcut hints
        shortcuts = self.font_small.render(
            "[Space]Tool [Ctrl]Seed [I]Inventory [H]Help [Q/E]Tool [Z/X]Seed [ESC]Exit",
            True, COLOR_LIGHT_GRAY
        )
        shortcuts_rect = shortcuts.get_rect(right=SCREEN_WIDTH - 20, y=y_pos + 35)
        self.screen.blit(shortcuts, shortcuts_rect)
        
        # Interaction hint
        if self.interaction_hint:
            hint_bg = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 80, 300, 40)
            pygame.draw.rect(self.screen, COLOR_BLACK, hint_bg, border_radius=5)
            pygame.draw.rect(self.screen, COLOR_WHITE, hint_bg, 2, border_radius=5)
            
            hint_text = self.font_small.render(self.interaction_hint, True, COLOR_WHITE)
            hint_rect = hint_text.get_rect(center=hint_bg.center)
            self.screen.blit(hint_text, hint_rect)
        
        # Message notifications
        msg_y = 100
        for msg in self.messages:
            alpha = min(255, int(msg['timer'] * 255))
            msg_surface = self.font_medium.render(msg['text'], True, COLOR_WHITE)
            msg_surface.set_alpha(alpha)
            
            # Background
            bg_rect = msg_surface.get_rect(center=(SCREEN_WIDTH // 2, msg_y))
            bg_rect.inflate_ip(20, 10)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
            bg_surface.set_alpha(alpha // 2)
            bg_surface.fill(COLOR_BLACK)
            self.screen.blit(bg_surface, bg_rect)
            
            self.screen.blit(msg_surface, (SCREEN_WIDTH // 2 - msg_surface.get_width() // 2, msg_y))
            msg_y += 40
    
    def draw_help(self):
        """Draw help info"""
        help_width = 400
        help_height = 350
        help_x = SCREEN_WIDTH - help_width - 20
        help_y = 100
        
        # Semi-transparent background
        help_surface = pygame.Surface((help_width, help_height))
        help_surface.set_alpha(220)
        help_surface.fill(COLOR_WHITE)
        self.screen.blit(help_surface, (help_x, help_y))
        
        # Border
        help_rect = pygame.Rect(help_x, help_y, help_width, help_height)
        pygame.draw.rect(self.screen, COLOR_BLACK, help_rect, 2, border_radius=5)
        
        # Title
        title = self.font_medium.render("Game Help [H]", True, COLOR_DARK_GREEN)
        self.screen.blit(title, (help_x + 20, help_y + 10))
        
        # Help content
        help_texts = [
            "Movement: WASD or Arrow Keys",
            "Use Tool: Space",
            "Use Seed: Left Ctrl",
            "Open Inventory: I",
            "Toggle Help: H",
            "Return to Login: ESC",
            "",
            "Gameplay:",
            "1. Press Q/E to select tool, Z/X to select seed",
            "2. Move in front of a plot, Space=tool, Ctrl=seed",
            "3. Hoe to improve soil; Water to irrigate; Axe to harvest/clear",
            "4. Wait until mature, then use Axe to harvest",
            "5. Press I to open inventory",
        ]
        y_offset = help_y + 50
        for text in help_texts:
            if text:
                help_line = self.font_small.render(text, True, COLOR_BLACK)
                self.screen.blit(help_line, (help_x + 20, y_offset))
            y_offset += 25





