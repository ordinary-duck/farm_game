# 自定义登录背景图片教程

## 功能说明
现在可以将登录界面的绿色背景替换为你自己的图片！

## 使用步骤

### 方法1：使用完整路径（推荐）

1. **准备你的背景图片**
   - 支持格式：JPG、PNG、BMP、GIF 等
   - 建议尺寸：960x480（当前窗口大小）或更大
   - 图片会自动缩放到窗口大小

2. **打开 `config.py` 文件**

3. **找到这两行代码：**
   ```python
   LOGIN_BG_IMAGE = None  # Set to None to use default green background
   # LOGIN_BG_IMAGE = r'D:\桌面\爆炸\farm_game\assets\login_bg.jpg'  # Uncomment and modify this line
   ```

4. **修改为你的图片路径：**
   ```python
   # 注释掉第一行，启用第二行并修改路径
   # LOGIN_BG_IMAGE = None
   LOGIN_BG_IMAGE = r'D:\你的图片路径\background.jpg'
   ```

### 方法2：使用 assets 文件夹（推荐用于项目管理）

1. **在游戏文件夹中创建 `assets` 文件夹**
   ```
   farm_game/
   ├── assets/           # 创建这个文件夹
   │   └── login_bg.jpg  # 把图片放这里
   ├── main.py
   ├── config.py
   └── ...
   ```

2. **将你的背景图片复制到 `assets` 文件夹**
   - 重命名为 `login_bg.jpg` 或其他名字

3. **在 `config.py` 中设置：**
   ```python
   LOGIN_BG_IMAGE = r'assets\login_bg.jpg'
   ```
   或使用完整路径：
   ```python
   LOGIN_BG_IMAGE = r'D:\桌面\爆炸\farm_game\assets\login_bg.jpg'
   ```

## 示例配置

### 示例1：使用桌面上的图片
```python
LOGIN_BG_IMAGE = r'C:\Users\谈烨\Desktop\farm_background.jpg'
```

### 示例2：使用项目文件夹中的图片
```python
LOGIN_BG_IMAGE = r'D:\桌面\爆炸\farm_game\assets\bg.png'
```

### 示例3：使用相对路径
```python
LOGIN_BG_IMAGE = r'assets\login_bg.jpg'
```

### 示例4：恢复默认绿色背景
```python
LOGIN_BG_IMAGE = None
```

## 注意事项

1. **路径格式**
   - Windows 路径使用反斜杠 `\`
   - 在路径前加 `r` 表示原始字符串，避免转义问题
   - 例如：`r'D:\Pictures\bg.jpg'` 而不是 `'D:\\Pictures\\bg.jpg'`

2. **文件名中的中文**
   - 支持中文路径和文件名
   - 例如：`r'D:\图片\农场背景.jpg'` ?

3. **图片大小**
   - 图片会自动缩放到窗口大小（960x480）
   - 建议使用横版图片，避免变形
   - 文件大小建议在 5MB 以内

4. **支持的格式**
   - ? JPG / JPEG
   - ? PNG（支持透明，但背景会显示为黑色）
   - ? BMP
   - ? GIF
   - ? TGA、PCX 等

## 推荐的背景图片

适合农场游戏的背景主题：
- ? 农田风景
- ? 田园景色
- ? 日出/日落
- ? 农舍
- ? 天空
- ? 向日葵田

## 测试

修改完 `config.py` 后，重新运行游戏：
```bash
python main.py
```

或双击 `start.bat`

## 查看加载状态

启动游戏时，控制台会显示：
- 如果成功：`Loaded background image: D:\你的路径\图片.jpg`
- 如果失败：会显示错误信息并使用默认绿色背景

## 示例文件结构

```
farm_game/
├── assets/                    # 推荐创建这个文件夹
│   ├── login_bg.jpg          # 登录背景
│   ├── farm_bg.jpg           # 游戏背景（未来可用）
│   └── icon.png              # 图标（未来可用）
├── config.py                 # 在这里设置背景路径
├── login_scene.py            # 登录场景（自动加载背景）
├── main.py
└── ...
```

## 故障排除

### 问题1：图片不显示
**检查：**
- 文件路径是否正确
- 文件是否存在
- 文件格式是否支持
- 查看控制台错误信息

### 问题2：图片变形
**解决：**
- 使用横版图片（宽高比约 2:1）
- 或调整窗口大小以匹配图片比例

### 问题3：路径有中文但无法加载
**解决：**
- 确保路径前有 `r`：`r'D:\图片\bg.jpg'`
- 或使用英文路径

---

创建时间：2025-11-06
功能状态：? 已实现并测试

