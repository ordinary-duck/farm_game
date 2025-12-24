# 游戏背景图片自定义指南

## ? 功能说明

现在游戏支持自定义两个场景的背景图片：
1. **登录界面背景** - 玩家选择界面
2. **农场游戏背景** - 进入游戏后的农场场景

## ? 如何设置背景图片

### 步骤1：准备背景图片

将你的背景图片放到 `assets` 文件夹中，推荐使用：
- **格式**: JPG 或 PNG
- **分辨率**: 1024x768 像素（或更高，会自动缩放）
- **文件大小**: 建议 < 2MB

### 步骤2：修改配置文件

打开 `config.py` 文件，找到背景图片配置部分：

```python
# Background Image Configuration
LOGIN_BG_IMAGE = r'assets\bkg_game.jpg'  # 登录界面背景
FARM_BG_IMAGE = None  # 农场场景背景
```

### 步骤3：设置你的背景图片路径

#### 示例1：使用相对路径（推荐）
```python
LOGIN_BG_IMAGE = r'assets\login_background.jpg'
FARM_BG_IMAGE = r'assets\farm_background.jpg'
```

#### 示例2：使用绝对路径
```python
LOGIN_BG_IMAGE = r'D:\图片\我的背景\login.png'
FARM_BG_IMAGE = r'D:\图片\我的背景\farm.png'
```

#### 示例3：使用默认颜色（不用图片）
```python
LOGIN_BG_IMAGE = None  # 使用浅绿色背景
FARM_BG_IMAGE = None   # 使用深绿色背景
```

### 步骤4：运行游戏
```bash
python main.py
```

## ? 背景图片特点

? **自动缩放** - 图片会自动缩放以适应窗口大小  
? **灵活配置** - 可以分别设置登录和游戏背景  
? **容错机制** - 图片加载失败会使用默认颜色  
? **路径灵活** - 支持相对路径和绝对路径  

## ? 推荐的背景图片风格

### 登录界面背景
- 温馨、明亮的农场景色
- 卡通风格的田园场景
- 带有农场元素（房屋、田地、动物等）

### 游戏场景背景
- 草地、土地纹理
- 不要太花哨，避免干扰游戏元素
- 柔和的颜色，确保地块和角色清晰可见

## ? 故障排除

### 问题：背景图片没有显示

1. **检查文件路径是否正确**
   - 确保路径中没有中文（如果有问题的话）
   - Windows 路径使用 `r'路径'` 或 `\\`

2. **检查文件是否存在**
   - 确认图片文件在指定位置
   - 检查文件名大小写是否匹配

3. **查看控制台输出**
   - 运行游戏时看看有没有加载失败的提示
   - 如："Failed to load farm background image"

4. **尝试使用绝对路径测试**
   - 先用完整路径确保图片可以加载
   - 然后再改成相对路径

### 问题：背景图片显示模糊

- 使用更高分辨率的图片（至少 1024x768）
- 确保原图质量较好
- 尝试使用 PNG 格式

## ? 建议的文件结构

```
farm_game/
├── assets/
│   ├── login_bg.jpg         # 登录界面背景
│   ├── farm_bg.jpg          # 农场场景背景
│   ├── bkg_game.jpg         # 当前使用的背景
│   └── buttons/
│       └── button.png
├── config.py
├── main.py
└── farm_scene.py
```

## ? 免费背景素材资源

你可以在以下网站找到免费的游戏背景图：

1. **OpenGameArt.org**
   - 大量免费游戏素材
   - 搜索 "farm background" 或 "pixel art farm"

2. **itch.io**
   - 免费游戏资源包
   - 搜索 "free farm assets"

3. **Kenney.nl**
   - 高质量免费素材
   - 有很多农场/自然主题

4. **Pixabay / Unsplash**
   - 免费高清图片
   - 搜索 "farm field grass"

## ? 快速开始示例

1. 下载一张喜欢的农场背景图
2. 重命名为 `farm_background.jpg`
3. 放到 `assets` 文件夹
4. 修改 `config.py`:
   ```python
   FARM_BG_IMAGE = r'assets\farm_background.jpg'
   ```
5. 运行游戏！

享受你的自定义农场游戏！??

