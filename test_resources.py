# -*- coding: utf-8 -*-
"""
测试资源加载
"""
import pygame
import sys

# 初始化 pygame
pygame.init()
pygame.display.set_mode((1,1))
# 导入资源管理器
from resource_manager import get_resources

print("\n开始测试资源加载...")
print("="*60)

try:
    # 获取资源管理器
    resources = get_resources()
    
    print("\n? 资源管理器初始化成功")
    
    # 测试角色动画
    print(f"\n角色动画数量: {len(resources.character_animations)}")
    if resources.character_animations:
        print("角色动画键:", list(resources.character_animations.keys())[:5], "...")
        down_frames = resources.character_animations.get('down', [])
        print(f"'down' 动画帧数: {len(down_frames)}")
        if down_frames:
            print(f"  第一帧尺寸: {down_frames[0].get_size()}")
    
    # 测试土壤图片
    print(f"\n土壤图片数量: {len(resources.soil_images)}")
    if resources.soil_images:
        print("土壤类型:", list(resources.soil_images.keys())[:10])
        soil_o = resources.soil_images.get('o')
        if soil_o:
            print(f"  'o' 土壤尺寸: {soil_o.get_size()}")
            # 检查是否是占位符（洋红色）
            test_color = soil_o.get_at((0, 0))
            if test_color[:3] == (255, 0, 255):
                print("  ?? 警告: 土壤图片是占位符（加载失败）")
            else:
                print(f"  ? 土壤图片加载成功，颜色: {test_color[:3]}")
    
    # 测试作物图片
    print(f"\n作物图片: {list(resources.fruit_images.keys())}")
    corn_frames = resources.fruit_images.get('corn', [])
    if isinstance(corn_frames, list):
        print(f"玉米生长阶段数: {len(corn_frames)}")
        if corn_frames:
            print(f"  第一阶段尺寸: {corn_frames[0].get_size()}")
    
    # 测试环境装饰
    print(f"\n环境物品数量: {len(resources.objects_images)}")
    if resources.objects_images:
        print("环境物品:", list(resources.objects_images.keys()))
    
    # 测试地面贴图
    print(f"\n世界贴图数量: {len(resources.world_images)}")
    if 'ground' in resources.world_images:
        ground = resources.world_images['ground']
        print(f"地面贴图尺寸: {ground.get_size()}")
    
    print("\n" + "="*60)
    print("? 资源加载测试完成！")
    
except Exception as e:
    print(f"\n? 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

pygame.quit()

