# 按钮图片自定义指南

## 功能说明

游戏登录界面的按钮现在支持自定义图片！你可以为以下三个按钮设置自己的图片：

1. **左箭头按钮（BUTTON_PREV_IMAGE）** - 切换到上一个玩家
2. **右箭头按钮（BUTTON_NEXT_IMAGE）** - 切换到下一个玩家  
3. **开始游戏按钮（BUTTON_START_IMAGE）** - 进入游戏

## 使用方法

### 步骤 1：准备按钮图片

准备你想使用的按钮图片文件，支持以下格式：
- PNG（推荐，支持透明背景）
- JPG/JPEG
- BMP
- GIF

**图片建议：**
- 左右箭头按钮建议尺寸：60x60 像素（正方形）
- 开始游戏按钮建议尺寸：300x50 像素（长方形）
- 使用 PNG 格式可以实现圆角或不规则形状的按钮
- 图片会自动缩放到按钮大小，但建议使用接近目标尺寸的图片以获得最佳效果

### 步骤 2：放置图片文件

将按钮图片放到游戏目录下的 `assets` 文件夹中：

```
farm_game/
├── assets/
│   ├── btn_prev.png      # 左箭头按钮图片
│   ├── btn_next.png      # 右箭头按钮图片
│   └── btn_start.png     # 开始游戏按钮图片
├── config.py
└── ...
```

### 步骤 3：配置图片路径

打开 `config.py` 文件，找到"Button Image Configuration"部分（大约在第29-39行），修改配置：

```python
# Button Image Configuration
BUTTON_PREV_IMAGE = r'assets\btn_prev.png'    # 左箭头按钮
BUTTON_NEXT_IMAGE = r'assets\btn_next.png'    # 右箭头按钮  
BUTTON_START_IMAGE = r'assets\btn_start.png'  # 开始游戏按钮
```

**路径说明：**
- **相对路径**（推荐）：`r'assets\btn_prev.png'` 或 `'assets/btn_prev.png'`
- **绝对路径**：`r'D:\桌面\爆炸\farm_game\assets\btn_prev.png'`
- 如果不想使用自定义图片，保持 `None` 即可使用默认的彩色矩形按钮

### 步骤 4：运行游戏

运行游戏，按钮图片会自动加载：

```batch
run_game.bat
```

或

```batch
python main.py
```

## 示例配置

### 示例 1：使用相对路径（推荐）

```python
BUTTON_PREV_IMAGE = r'assets\btn_prev.png'
BUTTON_NEXT_IMAGE = r'assets\btn_next.png'
BUTTON_START_IMAGE = r'assets\btn_start.png'
```

### 示例 2：使用绝对路径

```python
BUTTON_PREV_IMAGE = r'D:\图片\游戏按钮\left_arrow.png'
BUTTON_NEXT_IMAGE = r'D:\图片\游戏按钮\right_arrow.png'
BUTTON_START_IMAGE = r'D:\图片\游戏按钮\start_button.png'
```

### 示例 3：混合使用（部分自定义，部分默认）

```python
BUTTON_PREV_IMAGE = r'assets\btn_prev.png'  # 使用自定义图片
BUTTON_NEXT_IMAGE = r'assets\btn_next.png'  # 使用自定义图片
BUTTON_START_IMAGE = None  # 使用默认矩形按钮
```

### 示例 4：全部使用默认样式

```python
BUTTON_PREV_IMAGE = None
BUTTON_NEXT_IMAGE = None
BUTTON_START_IMAGE = None
```

## 高级功能

### 悬停效果

按钮图片会自动生成悬停效果：
- 当鼠标悬停在按钮上时，图片会自动变亮
- 无需准备单独的悬停状态图片

### 文字叠加

即使使用了自定义按钮图片，按钮文字仍会显示在图片上方：
- 左箭头按钮显示 "<"
- 右箭头按钮显示 ">"
- 开始游戏按钮显示 "Enter Game"

如果你希望图片本身已经包含文字，可以通过编辑 `login_scene.py` 中的按钮创建代码来移除文字。

### 调试信息

运行游戏时，控制台会显示按钮图片的加载状态：
- `Loaded button image: D:\...\btn_prev.png` - 加载成功
- `Button image not found: ...` - 图片文件不存在
- `Failed to load button image: ...` - 图片加载失败（可能是格式不支持）

## 常见问题

### Q1: 图片没有显示，仍然是默认按钮？

**可能原因：**
1. 图片路径错误或文件不存在
2. 图片格式不支持
3. 配置文件修改后没有重新启动游戏

**解决方法：**
- 检查控制台输出的错误信息
- 确认图片文件确实存在于指定路径
- 完全关闭游戏后重新运行

### Q2: 图片显示了但是尺寸不对？

图片会自动缩放到按钮大小，但可能会变形。建议使用接近目标尺寸的图片：
- 箭头按钮：60x60 像素
- 开始按钮：300x50 像素

### Q3: 如何制作透明背景的按钮？

使用 PNG 格式保存图片，并在图像编辑软件中设置透明背景。

### Q4: 能否更改按钮的尺寸？

可以！在 `login_scene.py` 的 `create_buttons` 方法中修改：
- `arrow_size = 60` - 修改箭头按钮尺寸
- `BUTTON_WIDTH` 和 `BUTTON_HEIGHT` - 在 `config.py` 中修改开始按钮尺寸

### Q5: 如何移除按钮上的文字？

编辑 `login_scene.py` 中的 `Button.draw` 方法，注释掉最后三行绘制文字的代码：

```python
# text_surface = self.font.render(self.text, True, self.text_color)
# text_rect = text_surface.get_rect(center=self.rect.center)
# surface.blit(text_surface, text_rect)
```

## 制作提示

如果你想自己制作按钮图片，这里有一些建议：

### 推荐工具
- **Photoshop** - 专业图像编辑
- **GIMP** - 免费开源替代品
- **Paint.NET** - 轻量级Windows工具
- **在线工具** - Canva, Pixlr 等

### 设计建议
1. 使用高对比度的颜色让按钮清晰可见
2. 箭头符号要简洁明了
3. 保持视觉风格与游戏主题一致
4. 测试悬停效果（自动变亮）是否明显

## 技术细节

按钮图片加载流程：
1. 从 `config.py` 读取图片路径
2. 自动转换相对路径为绝对路径
3. 使用 `pygame.image.load()` 加载图片
4. 自动缩放到按钮尺寸
5. 生成悬停效果图片（自动增亮）
6. 如果加载失败，自动回退到默认矩形按钮

---

如有任何问题，请查看控制台的调试输出信息！

