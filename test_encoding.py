# -*- coding: utf-8 -*-
"""
编码测试脚本 - 检测系统编码配置
"""
import sys
import locale

print("=" * 50)
print("System Encoding Test / 系统编码测试")
print("=" * 50)
print()

# 测试系统编码
print("1. System Information:")
print(f"   Platform: {sys.platform}")
print(f"   Python Version: {sys.version}")
print()

print("2. Encoding Settings:")
print(f"   sys.stdout.encoding: {sys.stdout.encoding}")
print(f"   sys.getdefaultencoding(): {sys.getdefaultencoding()}")
print(f"   locale.getpreferredencoding(): {locale.getpreferredencoding()}")
print()

# 测试中文输出
print("3. Chinese Text Test:")
try:
    print("   农场物语 - Farm Game")
    print("   Test Passed: Chinese characters OK")
except Exception as e:
    print(f"   Test Failed: {e}")
print()

# 测试数据库连接
print("4. Database Connection Test:")
try:
    from database import db
    if db.connect():
        print("   Database connection: OK")
        
        # 测试查询
        players = db.get_all_players()
        if players:
            print(f"   Found {len(players)} players")
            for player in players:
                try:
                    print(f"   - Player: {player['Name']} (Lv.{player['Level']})")
                except Exception as e:
                    print(f"   - Player name encoding error: {e}")
        else:
            print("   No players found in database")
        
        db.disconnect()
    else:
        print("   Database connection: FAILED")
        print("   Please check config.py settings")
except Exception as e:
    print(f"   Database test failed: {e}")
print()

# 测试Pygame
print("5. Pygame Test:")
try:
    import pygame
    pygame.init()
    print(f"   Pygame version: {pygame.version.ver}")
    print("   Pygame initialized: OK")
    pygame.quit()
except Exception as e:
    print(f"   Pygame test failed: {e}")
print()

print("=" * 50)
print("Test Complete / 测试完成")
print()
print("If you see errors above, please:")
print("1. Make sure all .py files are saved as UTF-8")
print("2. Check database connection in config.py")
print("3. Install dependencies: pip install -r requirements.txt")
print("=" * 50)

input("\nPress Enter to exit...")

