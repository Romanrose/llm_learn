# 🎮 赛博小镇 - GDScript脚本说明

## 📁 脚本文件列表

```
scripts/
├── config.gd          # 全局配置
├── api_client.gd      # API通信客户端
├── player.gd          # 玩家控制
├── npc.gd            # NPC行为
├── dialogue_ui.gd    # 对话UI
└── main.gd           # 主场景逻辑
```

---

## 📄 脚本详解

### 1. config.gd (全局配置)
**用途**: 存储全局常量和配置

**关键配置**:
```gdscript
const API_BASE_URL = "http://localhost:8000"  # 后端API地址
const PLAYER_SPEED = 200.0                     # 玩家速度
const NPC_STATUS_UPDATE_INTERVAL = 30.0        # NPC更新间隔
```

**使用方法**:
```gdscript
# 在任何脚本中访问
Config.log_info("消息")
var speed = Config.PLAYER_SPEED
```

---

### 2. api_client.gd (API客户端)
**用途**: 与FastAPI后端通信

**主要方法**:
- `send_chat(npc_name, message)` - 发送对话
- `get_npc_status()` - 获取NPC状态
- `get_npc_list()` - 获取NPC列表

**信号**:
- `chat_response_received(npc_name, message)` - 收到对话回复
- `chat_error(error_message)` - 对话错误
- `npc_status_received(dialogues)` - 收到NPC状态

**使用示例**:
```gdscript
# 获取API客户端
var api = get_node("/root/APIClient")

# 发送对话
api.send_chat("张三", "你好")

# 监听回复
api.chat_response_received.connect(_on_response)

func _on_response(npc_name, message):
    print(npc_name + ": " + message)
```

---

### 3. player.gd (玩家控制)
**用途**: 处理玩家移动和交互

**关键功能**:
- WASD/方向键移动
- E键与NPC交互
- 检测附近的NPC

**节点要求**:
```
Player (CharacterBody2D)
├── Sprite2D
├── CollisionShape2D
└── Camera2D
```

**自定义参数**:
```gdscript
@export var speed: float = 200.0  # 在Inspector中可调整
```

---

### 4. npc.gd (NPC行为)
**用途**: NPC交互和状态显示

**关键功能**:
- 检测玩家进入/离开交互范围
- 显示NPC名字和对话
- 更新NPC状态

**节点要求**:
```
NPC (Node2D)
├── Sprite2D
├── InteractionArea (Area2D)
│   └── CollisionShape2D
├── NameLabel (Label)
└── DialogueLabel (Label)
```

**导出参数**:
```gdscript
@export var npc_name: String = "张三"
@export var npc_title: String = "Python工程师"
```

**使用方法**:
1. 在Inspector中设置NPC名字和职位
2. 脚本会自动处理交互逻辑

---

### 5. dialogue_ui.gd (对话UI)
**用途**: 对话界面管理

**关键功能**:
- 显示/隐藏对话框
- 处理玩家输入
- 显示对话历史
- 与API通信

**节点要求**:
```
DialogueUI (CanvasLayer)
└── Panel
    ├── NPCName (Label)
    ├── NPCTitle (Label)
    ├── DialogueText (RichTextLabel)
    ├── PlayerInput (LineEdit)
    ├── SendButton (Button)
    └── CloseButton (Button)
```

**使用方法**:
```gdscript
# 开始对话
get_tree().call_group("dialogue_system", "start_dialogue", "张三")
```

---

### 6. main.gd (主场景)
**用途**: 管理整个游戏场景

**关键功能**:
- 定时更新NPC状态
- 分发NPC对话到各个NPC节点
- 协调各个系统

**节点要求**:
```
Main (Node2D)
├── TileMapLayer (地图)
├── Player (实例化)
├── NPCs (Node2D)
│   ├── NPC_Zhang (实例化)
│   ├── NPC_Li (实例化)
│   └── NPC_Wang (实例化)
└── DialogueUI (实例化)
```

---

## 🔧 如何使用这些脚本

### 步骤1: 设置AutoLoad
在 `Project -> Project Settings -> AutoLoad` 中添加:
- `config.gd` -> 名称: `Config`
- `api_client.gd` -> 名称: `APIClient`

### 步骤2: 附加脚本到场景
- `player.tscn` -> 附加 `player.gd`
- `npc.tscn` -> 附加 `npc.gd`
- `dialogue_ui.tscn` -> 附加 `dialogue_ui.gd`
- `main.tscn` -> 附加 `main.gd`

### 步骤3: 配置节点
确保每个场景的节点结构与脚本要求一致。

### 步骤4: 设置参数
在Inspector中设置导出参数(如NPC名字、速度等)。

---

## 🐛 调试技巧

### 查看日志
所有脚本都使用 `Config.log_info()` 输出日志,在Godot的 **Output** 面板查看。

### 常见日志:
```
[INFO] API客户端初始化完成
[INFO] 玩家初始化完成
[INFO] NPC初始化: 张三
[INFO] 进入NPC范围: 张三
[API] POST /chat -> {"npc_name":"张三","message":"你好"}
[INFO] 收到NPC回复: 张三 -> 你好!我是Python工程师...
```

### 启用调试模式
在 `config.gd` 中:
```gdscript
const DEBUG_MODE = true  # 显示详细日志
const SHOW_INTERACTION_RANGE = true  # 显示交互范围
```

---

## 📊 信号流程图

```
玩家按E键
    ↓
player.gd: interact_with_npc()
    ↓
发送信号到 dialogue_system 组
    ↓
dialogue_ui.gd: start_dialogue(npc_name)
    ↓
显示对话框,玩家输入消息
    ↓
dialogue_ui.gd: send_message()
    ↓
api_client.gd: send_chat(npc_name, message)
    ↓
HTTP请求到FastAPI后端
    ↓
api_client.gd: _on_chat_request_completed()
    ↓
发出信号: chat_response_received
    ↓
dialogue_ui.gd: _on_chat_response_received()
    ↓
显示NPC回复
```

---

## 🎯 扩展建议

### 添加新NPC
1. 在 `main.tscn` 中实例化 `npc.tscn`
2. 设置NPC名字和位置
3. 在 `main.gd` 的 `get_npc_node()` 中添加映射

### 添加新功能
1. 在 `config.gd` 中添加配置
2. 在 `api_client.gd` 中添加新API方法
3. 在相应脚本中实现逻辑

### 优化性能
1. 减少 `NPC_STATUS_UPDATE_INTERVAL` 的更新频率
2. 使用对象池管理UI元素
3. 优化TileMap的碰撞层

---

## 📚 参考资源

- **Godot文档**: https://docs.godotengine.org/
- **GDScript教程**: https://gdscript.com/
- **FastAPI文档**: https://fastapi.tiangolo.com/

---

## ❓ 常见问题

**Q: 如何修改API地址?**
A: 编辑 `config.gd` 中的 `API_BASE_URL`

**Q: 如何添加更多NPC?**
A: 实例化 `npc.tscn`,设置参数,在 `main.gd` 中添加引用

**Q: 如何自定义对话框样式?**
A: 编辑 `dialogue_ui.tscn`,修改Panel和Label的主题

**Q: 如何禁用调试日志?**
A: 在 `config.gd` 中设置 `DEBUG_MODE = false`

