# 快速开始指南

## ? 5分钟启动游戏

### 第一步：安装依赖

双击运行 `setup.bat` 或在终端执行：

```bash
pip install -r requirements.txt
```

### 第二步：配置数据库

1. 打开 `config.py`
2. 修改数据库连接信息：

```python
DB_CONFIG = {
    'server': 'localhost',        # 改为你的服务器地址
    'user': 'sa',                 # 改为你的用户名
    'password': 'your_password',  # 改为你的密码
    'database': 'FarmGameDB',
    'charset': 'utf8'
}
```

### 第三步：确保数据库已准备好

确保已经在SQL Server中执行了以下脚本（按顺序）：

1. `SQLQuery0.sql` - 删除旧数据库（如果存在）
2. `SQLQuery1.sql` - 创建数据库
3. `SQLQuery2.sql` - 创建表结构
4. `SQLQuery3.sql` - 添加扩展字段
5. `insert1.sql` - 插入游戏数据

### 第四步：启动游戏

双击运行 `run_game.bat` 或在终端执行：

```bash
python main.py
```

## ? 开始游戏

### 登录界面
1. 选择一个玩家（阿农、小叶或老王）
2. 选择该玩家的农场
3. 点击"进入农场"按钮

### 游戏操作
- **WASD** 或 **方向键**：移动角色
- **空格**：种植/收获作物
- **I键**：打开背包
- **H键**：显示帮助
- **ESC**：返回登录界面

### 游戏提示
- 移动到空地块旁边按空格键种植作物
- 金黄色闪烁的作物表示已成熟，可以收获
- 按I键查看背包中的物品

## ? 常见问题

### 问题1：连接数据库失败
**解决方案：**
- 检查SQL Server是否运行
- 确认config.py中的配置正确
- 测试数据库连接

### 问题2：没有种子
**解决方案：**
- 检查数据库中是否有初始数据
- 重新运行 `insert1.sql` 脚本

### 问题3：游戏窗口太大/太小
**解决方案：**
- 修改 `config.py` 中的 `SCREEN_WIDTH` 和 `SCREEN_HEIGHT`

## ? 获取帮助

如有问题，请检查：
1. README.md - 完整文档
2. config.py - 配置说明
3. 游戏内按H键 - 游戏帮助

祝游戏愉快！?

