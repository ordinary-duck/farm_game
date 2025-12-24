# -*- coding: utf-8 -*-
"""
资源管理器 - 加载和管理游戏图片资源
"""
import pygame
import os
from typing import Dict, List, Optional


class ResourceManager:
    """游戏资源管理器"""
    
    def __init__(self):
        """初始化资源管理器"""
        # 始终以当前脚本所在目录为基准，避免工作目录不同导致找不到资源
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.graphics_path = os.path.join(base_dir, "graphics")
        
        # 存储所有加载的资源
        self.character_animations = {}  # 角色动画
        self.environment_images = {}    # 环境物品
        self.fruit_images = {}          # 水果/作物
        self.objects_images = {}        # 物体（树、灌木等）
        self.overlay_images = {}        # 工具覆盖层
        self.soil_images = {}           # 土壤贴图
        self.soil_water_images = []     # 浇水土壤动画
        self.rain_floor = []            # 雨滴地面效果
        self.rain_drops = []            # 雨滴效果
        self.water_animation = []       # 水面动画
        self.world_images = {}          # 世界贴图
        
        # 加载所有资源
        self.load_all_resources()
    
    def load_image(self, path: str, convert_alpha=True) -> pygame.Surface:
        """加载单个图片"""
        try:
            full_path = os.path.join(self.graphics_path, path)
            if convert_alpha:
                return pygame.image.load(full_path).convert_alpha()
            else:
                return pygame.image.load(full_path).convert()
        except Exception as e:
            print(f"加载图片失败 {path}: {e}")
            # 返回一个占位符表面
            surf = pygame.Surface((64, 64))
            surf.fill((255, 0, 255))  # 洋红色表示缺失
            return surf
    
    def load_animation_frames(self, folder_path: str) -> List[pygame.Surface]:
        """加载动画序列帧"""
        frames = []
        full_path = os.path.join(self.graphics_path, folder_path)
        
        try:
            # 获取文件夹中的所有png文件并排序
            files = sorted([f for f in os.listdir(full_path) if f.endswith('.png')])
            for file in files:
                frame_path = os.path.join(folder_path, file)
                frames.append(self.load_image(frame_path))
        except Exception as e:
            print(f"加载动画序列失败 {folder_path}: {e}")
        
        return frames
    
    def load_character_animations(self):
        """加载角色所有动画"""
        print("正在加载角色动画...")
        
        # 所有角色动作和方向
        actions = [
            'down', 'down_idle', 'down_axe', 'down_hoe', 'down_water',
            'up', 'up_idle', 'up_axe', 'up_hoe', 'up_water',
            'left', 'left_idle', 'left_axe', 'left_hoe', 'left_water',
            'right', 'right_idle', 'right_axe', 'right_hoe', 'right_water'
        ]
        
        for action in actions:
            folder_path = os.path.join('character', action)
            self.character_animations[action] = self.load_animation_frames(folder_path)
            if self.character_animations[action]:
                print(f"  ? 加载 {action}: {len(self.character_animations[action])} 帧")
    
    def load_environment(self):
        """加载环境物品"""
        print("正在加载环境物品...")
        
        env_files = [
            'Bridge.png', 'Collision.png', 'Fences.png', 'Grass.png',
            'Hills.png', 'House Decoration.png', 'House.png',
            'interaction.png', 'Paths.png', 'Plant Decoration.png',
            'Water Decoration.png', 'Water.png'
        ]
        
        for file in env_files:
            name = file.replace('.png', '').replace(' ', '_').lower()
            self.environment_images[name] = self.load_image(os.path.join('environment', file))
            print(f"  ? 加载 {name}")
    
    def load_fruits(self):
        """加载水果/作物"""
        print("正在加载作物...")
        
        # 苹果
        self.fruit_images['apple'] = self.load_image(os.path.join('fruit', 'apple.png'))
        print("  ? 加载 apple")
        
        # 玉米生长阶段
        self.fruit_images['corn'] = self.load_animation_frames(os.path.join('fruit', 'corn'))
        print(f"  ? 加载 corn: {len(self.fruit_images['corn'])} 阶段")
        
        # 番茄生长阶段
        self.fruit_images['tomato'] = self.load_animation_frames(os.path.join('fruit', 'tomato'))
        print(f"  ? 加载 tomato: {len(self.fruit_images['tomato'])} 阶段")
    
    def load_objects(self):
        """加载物体"""
        print("正在加载物体...")
        
        obj_files = [
            'bush.png', 'flower.png', 'merchant.png', 'mushroom.png',
            'mushrooms.png', 'stump_medium.png', 'stump_small.png',
            'sunflower.png', 'tree_medium.png', 'tree_small.png'
        ]
        
        for file in obj_files:
            name = file.replace('.png', '')
            self.objects_images[name] = self.load_image(os.path.join('objects', file))
            print(f"  ? 加载 {name}")
    
    def load_overlay(self):
        """加载工具覆盖层图标"""
        print("正在加载工具图标...")
        
        tools = ['axe', 'corn', 'hoe', 'tomato', 'water']
        
        for tool in tools:
            self.overlay_images[tool] = self.load_image(os.path.join('overlay', f'{tool}.png'))
            print(f"  ? 加载 {tool}")
    
    def load_soil(self):
        """加载土壤贴图"""
        print("正在加载土壤贴图...")
        
        # 土壤的所有状态
        soil_types = [
            'b', 'bl', 'bm', 'br', 'l', 'lm', 'lr', 'lrb', 'lrt',
            'o', 'r', 'rm', 'soil', 't', 'tb', 'tbl', 'tbr',
            'tl', 'tm', 'tr', 'x'
        ]
        
        for soil_type in soil_types:
            path = os.path.join('soil', f'{soil_type}.png')
            self.soil_images[soil_type] = self.load_image(path)
        
        print(f"  ? 加载 {len(self.soil_images)} 种土壤贴图")
        
        # 浇水后的土壤动画
        self.soil_water_images = self.load_animation_frames('soil_water')
        print(f"  ? 加载浇水动画: {len(self.soil_water_images)} 帧")
    
    def load_effects(self):
        """加载特效"""
        print("正在加载特效...")
        
        # 雨滴效果
        self.rain_drops = self.load_animation_frames(os.path.join('rain', 'drops'))
        print(f"  ? 加载雨滴: {len(self.rain_drops)} 帧")
        
        # 雨滴地面效果
        self.rain_floor = self.load_animation_frames(os.path.join('rain', 'floor'))
        print(f"  ? 加载雨滴地面: {len(self.rain_floor)} 帧")
        
        # 水面动画
        self.water_animation = self.load_animation_frames('water')
        print(f"  ? 加载水面动画: {len(self.water_animation)} 帧")
    
    def load_world(self):
        """加载世界贴图"""
        print("正在加载世界贴图...")
        
        self.world_images['ground'] = self.load_image(os.path.join('world', 'ground.png'))
        print("  ? 加载 ground")
    
    def load_all_resources(self):
        """加载所有资源"""
        print("\n" + "="*50)
        print("开始加载游戏资源...")
        print("="*50)
        
        self.load_character_animations()
        self.load_environment()
        self.load_fruits()
        self.load_objects()
        self.load_overlay()
        self.load_soil()
        self.load_effects()
        self.load_world()
        
        print("="*50)
        print("资源加载完成！")
        print("="*50 + "\n")
    
    def get_character_animation(self, action: str) -> List[pygame.Surface]:
        """获取角色动画"""
        return self.character_animations.get(action, [])
    
    def get_fruit_growth(self, fruit_name: str, stage: int) -> pygame.Surface:
        """获取作物生长阶段图片"""
        if fruit_name in self.fruit_images:
            fruit_data = self.fruit_images[fruit_name]
            if isinstance(fruit_data, list) and len(fruit_data) > 0:
                # 确保stage在有效范围内
                stage = min(stage, len(fruit_data) - 1)
                return fruit_data[stage]
            else:
                return fruit_data
        return None
    
    def get_soil_image(self, soil_type: str) -> pygame.Surface:
        """获取土壤贴图"""
        return self.soil_images.get(soil_type, self.soil_images.get('o'))


# 全局资源管理器实例
resources = None

def init_resources():
    """初始化全局资源管理器"""
    global resources
    if resources is None:
        resources = ResourceManager()
    return resources

def get_resources() -> ResourceManager:
    """获取资源管理器实例"""
    global resources
    if resources is None:
        resources = init_resources()
    return resources

