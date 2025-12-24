# -*- coding: utf-8 -*-
"""
Game Configuration File
"""
import os
import sys

# Font Configuration - Support Chinese
FONT_PATH = None
if sys.platform == 'win32':
    # Common Windows Chinese fonts
    chinese_fonts = [
        r'C:\Windows\Fonts\msyh.ttc',      # Microsoft YaHei (best)
        r'C:\Windows\Fonts\simhei.ttf',    # SimHei
        r'C:\Windows\Fonts\simsun.ttc',    # SimSun
        r'C:\Windows\Fonts\simkai.ttf',    # KaiTi
    ]
    for font in chinese_fonts:
        if os.path.exists(font):
            FONT_PATH = font
            print(f"Using Chinese font: {font}")
            break

# Background Image Configuration
# Set your custom background image path here
# Example: r'D:\Images\farm_bg.jpg' or r'C:\Users\YourName\Pictures\background.png'
LOGIN_BG_IMAGE = r'assets\bkg_login2.jpg'  # Login screen background
# Use the high-resolution world map as the default farm background.
FARM_BG_IMAGE = None  # When using TMX maps, keep this None
FARM_BG_SCALE_TO_SCREEN = False  # Keep original resolution so the world map can be explored

# TMX map / layered world configuration
USE_TMX_MAP = True  # Toggle to False to fall back to static background rendering
TMX_MAP_PATH = 'map.tmx'
LAYERS = {
    'water': 0,
    'ground': 1,
    'soil': 2,
    'soil water': 3,
    'rain floor': 4,
    'house bottom': 5,
    'ground plant': 6,
    'main': 7,
    'house top': 8,
    'fruit': 9,
    'rain drops': 10
}

APPLE_SPAWN_CHANCE = 0.8
APPLE_POS = {
    'Small': [(18, 17), (30, 37), (12, 50), (30, 45), (20, 30), (30, 10)],
    'Large': [(30, 24), (60, 65), (50, 50), (16, 40), (45, 50), (42, 70)]
}

# obstacle rects: 
# Player/world alignment on the custom background
FARM_PLAYER_SPAWN = (1600, 1800)  # Starting position once the farm scene loads
FARM_PLOT_OFFSET = (800, 1500)   # Top-left corner where database plots should be drawn
FARM_OBSTACLE_RECTS = [
    # (x, y, width, height) rectangles that block player movement
    (1350, 260, 420, 260),   # top housing/platform
    (1820, 1150, 320, 320),  # center log storage
    (460, 1380, 520, 520),   # left forest edge
    (0, 1950, 1100, 610),    # bottom-left void
    (2050, 520, 320, 260), 
    #(568,2168,1933,325)  # top-right pond/void
    #(2567,2085,193,2255)

]

# Button Image Configuration
# Set custom button images here (set to None to use default colored rectangles)
# You can use relative paths (like 'assets\button.png') or absolute paths
BUTTON_PREV_IMAGE = None  # Left arrow button
BUTTON_NEXT_IMAGE = None  # Right arrow button  
BUTTON_START_IMAGE = None  # Start game button

# All buttons now use the same blue button style!
# You can set different images for each button if you want:
# BUTTON_PREV_IMAGE = r'assets\buttons\btn_left.png'
# BUTTON_NEXT_IMAGE = r'assets\buttons\btn_right.png'
# BUTTON_START_IMAGE = r'assets\buttons\btn_start.png'

# Login Screen Layout Configuration
# Adjust these values to position UI elements around your background character
# Layout presets: 'center' (default), 'left', 'right', 'top', 'bottom'
LOGIN_LAYOUT_PRESET = 'center'  # Change to adjust overall layout

# Or customize individual positions:
LOGIN_TITLE_Y = 80           # Title "Farm Game" Y position
LOGIN_CARD_X_OFFSET = 0      # Card horizontal offset from center (-200 to 200)
LOGIN_CARD_Y = 200           # Card vertical position
LOGIN_CARD_WIDTH = 400       # Card width
LOGIN_CARD_HEIGHT = 280      # Card height
LOGIN_CARD_ALPHA = 220       # Card transparency (0-255, lower = more transparent)

# Common presets examples:
# 'left' layout: Person on right, UI on left
# LOGIN_CARD_X_OFFSET = -200

# 'right' layout: Person on left, UI on right  
# LOGIN_CARD_X_OFFSET = 200

# 'top' layout: Person at bottom, UI at top
# LOGIN_CARD_Y = 100

# Database Configuration
DB_CONFIG = {
    'server': '.',
    'user': 'ADMINISTART\谈烨',
    'password': 'ty2004517',
    'database': 'FarmGameDB',
    'charset': 'utf8'
}

# Window Configuration
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
# SCREEN_WIDTH = 3200
# SCREEN_HEIGHT = 2560
FPS = 60
GAME_TITLE = "Farm Game" # 鏍囬 
#GAME_TITLE = "閫夋嫨浣犵殑鍐滃満鍜岀帺瀹? # 鏍囬 

# Colors
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GREEN = (34, 139, 34)
COLOR_BROWN = (139, 69, 19)
COLOR_YELLOW = (255, 215, 0)
COLOR_GRAY = (128, 128, 128)
COLOR_LIGHT_GRAY = (200, 200, 200)
COLOR_BLUE = (70, 130, 180)
COLOR_RED = (220, 20, 60)
COLOR_DARK_GREEN = (0, 100, 0)
COLOR_LIGHT_GREEN = (144, 238, 144)
COLOR_ORANGE = (255, 165, 0)

# Graphics Configuration
GRAPHICS_PATH = 'graphics'  # Path to graphics folder

# Plot Configuration
TILE_SIZE = 64
PLOT_COLORS = {
    'Empty': COLOR_BROWN,
    'Growing': COLOR_LIGHT_GREEN,
    'Mature': COLOR_YELLOW,
    'Withered': COLOR_GRAY
}

# Player Configuration
PLAYER_SIZE = 128  # Larger sprite for better visibility
PLAYER_SPEED = 200
PLAYER_COLOR = COLOR_BLUE
_PLAYER_TOOL_OFFSET_RATIO = {
    'up': (0.0, -0.70),
    'down': (0.0, 0.90),
    'left': (-0.9, 0.10),
    'right': (0.9, 0.10)
}
PLAYER_TOOL_OFFSET = {
    direction: (int(PLAYER_SIZE * offsets[0]), int(PLAYER_SIZE * offsets[1]))
    for direction, offsets in _PLAYER_TOOL_OFFSET_RATIO.items()
}

# Animation Configuration
ANIMATION_SPEED = 0.15  # Seconds per frame
WATER_ANIMATION_SPEED = 0.2  # For water tiles

# UI Configuration
FONT_SIZE_LARGE = 48
FONT_SIZE_MEDIUM = 32
FONT_SIZE_SMALL = 24
FONT_SIZE_TINY = 18

# Button Configuration
BUTTON_WIDTH = 300
BUTTON_HEIGHT = 50
BUTTON_COLOR = COLOR_GREEN
BUTTON_HOVER_COLOR = (50, 180, 50)
BUTTON_TEXT_COLOR = COLOR_WHITE

