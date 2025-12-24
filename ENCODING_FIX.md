# 编码问题解决方案

## 问题描述

如果你在运行游戏时遇到以下错误：
- `UnicodeEncodeError`
- `UnicodeDecodeError`
- 中文显示为乱码或问号
- emoji表情符号无法显示

## 快速解决方案

### 方案1：使用修复后的版本（推荐）

游戏已经更新，移除了所有emoji表情符号，使用纯文本替代：
- ? → `Gold:`
- ? → `Gem:`

直接运行即可：
```bash
python main.py
```

### 方案2：运行编码测试

先运行测试脚本检测系统环境：
```bash
python test_encoding.py
```

这个脚本会测试：
- 系统编码设置
- 中文显示能力
- 数据库连接
- Pygame初始化

### 方案3：设置环境变量

在运行游戏前设置环境变量：

**Windows PowerShell:**
```powershell
$env:PYTHONIOENCODING="utf-8"
python main.py
```

**Windows CMD:**
```cmd
set PYTHONIOENCODING=utf-8
python main.py
```

### 方案4：修改代码页

在cmd中运行前先设置代码页：
```cmd
chcp 65001
python main.py
```

## 文件保存设置

确保所有Python文件都以UTF-8编码保存：

### VS Code
1. 打开文件
2. 点击右下角的编码
3. 选择"通过编码保存"
4. 选择"UTF-8"

### Notepad++
1. 编码 → 转为UTF-8（无BOM）
2. 保存文件

### PyCharm
1. File → Settings → Editor → File Encodings
2. 设置 Project Encoding 为 UTF-8
3. 设置 Default encoding for properties files 为 UTF-8

## 数据库编码

确保SQL Server数据库使用正确的字符集：

```sql
-- 检查数据库排序规则
SELECT name, collation_name 
FROM sys.databases 
WHERE name = 'FarmGameDB';

-- 如果需要，创建数据库时指定排序规则
CREATE DATABASE FarmGameDB
COLLATE Chinese_PRC_CI_AS;
```

## 游戏内显示问题

如果游戏能运行但中文显示为方块：

1. 这是Pygame字体不支持中文的问题
2. 可以在 `config.py` 中添加中文字体路径：

```python
# 在config.py中添加
import os
FONT_PATH = None  # 默认使用系统字体

# 如果需要，可以指定中文字体
# FONT_PATH = "C:/Windows/Fonts/simhei.ttf"  # 黑体
# FONT_PATH = "C:/Windows/Fonts/msyh.ttc"    # 微软雅黑
```

3. 然后在各个场景文件中使用：
```python
if FONT_PATH and os.path.exists(FONT_PATH):
    self.font_large = pygame.font.Font(FONT_PATH, FONT_SIZE_LARGE)
else:
    self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
```

## 常见错误及解决

### 错误1: UnicodeEncodeError in print()
```
UnicodeEncodeError: 'gbk' codec can't encode character
```

**解决：**
- main.py已添加编码设置代码
- 或使用 `python -X utf8 main.py`

### 错误2: Database query returns garbled text
```
玩家名称显示为乱码
```

**解决：**
- 检查 config.py 中的 charset 设置
- 确保设置为 `'charset': 'utf8'`
- 重新执行数据库脚本

### 错误3: Pygame font rendering issues
```
中文显示为方块 □□□
```

**解决：**
- Pygame默认字体不支持中文
- 方案已更新，使用英文标签
- 或按上述方法添加中文字体

## 测试清单

运行游戏前，确认以下项目：

- [ ] 所有.py文件以UTF-8编码保存
- [ ] config.py中数据库配置正确
- [ ] 运行 test_encoding.py 测试通过
- [ ] SQL Server正在运行
- [ ] 数据库FarmGameDB已创建并有数据
- [ ] Python依赖已安装 (pygame, pymssql)

## 仍然有问题？

1. 运行测试脚本：`python test_encoding.py`
2. 查看完整错误信息
3. 检查Python版本 (建议3.7+)
4. 尝试重新安装依赖：
   ```bash
   pip uninstall pygame pymssql
   pip install pygame pymssql
   ```

## 技术说明

游戏已做以下改进避免编码问题：
- 移除了emoji字符
- 添加了Windows编码处理
- 使用纯ASCII/中文字符
- 数据库连接指定UTF-8

现在应该可以在大多数Windows系统上正常运行了！

