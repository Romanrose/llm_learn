# NPC脚本
extends CharacterBody2D  # ⭐ 改为CharacterBody2D

# NPC信息
@export var npc_name: String = "张三"
@export var npc_title: String = "Python工程师"

# NPC外观配置
@export var sprite_frames: SpriteFrames = null  # 自定义精灵帧资源

# NPC移动配置 ⭐ 
@export var move_speed: float = 50.0  # 移动速度
@export var wander_enabled: bool = true  # 是否启用巡逻
@export var wander_range: float = 200.0  # 巡逻范围
@export var wander_interval_min: float = 3.0  # 最小巡逻间隔(秒)
@export var wander_interval_max: float = 8.0  # 最大巡逻间隔(秒)

# 当前对话内容(从后端获取)
var current_dialogue: String = ""

# 节点引用
@onready var animated_sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var interaction_area: Area2D = $InteractionArea
@onready var name_label: Label = $NameLabel
@onready var dialogue_label: Label = $DialogueLabel

# 交互提示 (可选节点,如果不存在也不会报错)
var interaction_hint: Label = null

# 玩家引用
var player: Node = null

# 巡逻相关变量 ⭐ 
var wander_target: Vector2 = Vector2.ZERO  # 巡逻目标位置
var wander_timer: float = 0.0  # 巡逻计时器
var is_wandering: bool = false  # 是否正在巡逻
var is_interacting: bool = false  # 是否正在与玩家交互
var spawn_position: Vector2 = Vector2.ZERO  # 出生位置

func _ready():
	# 添加到npcs组 ⭐ 
	add_to_group("npcs")

	# 设置NPC名字
	name_label.text = npc_name

	# 连接交互区域信号
	interaction_area.body_entered.connect(_on_body_entered)
	interaction_area.body_exited.connect(_on_body_exited)

	# 初始化对话标签
	dialogue_label.text = ""
	dialogue_label.visible = false

	# 尝试获取交互提示节点 (可选)
	interaction_hint = get_node_or_null("InteractionHint")
	if interaction_hint:
		interaction_hint.text = "按E交互"
		interaction_hint.visible = false
		print("[INFO] NPC交互提示已启用: ", npc_name)
	else:
		print("[WARN] NPC没有InteractionHint节点,交互提示已禁用: ", npc_name)

	# 设置自定义精灵帧 (如果有)
	if sprite_frames != null:
		animated_sprite.sprite_frames = sprite_frames
		print("[INFO] NPC使用自定义精灵: ", npc_name)

	# 播放默认动画
	if animated_sprite.sprite_frames != null and animated_sprite.sprite_frames.has_animation("idle"):
		animated_sprite.play("idle")

	# 记录出生位置 ⭐ 
	spawn_position = global_position

	# 初始化巡逻计时器 ⭐ 
	if wander_enabled:
		wander_timer = randf_range(wander_interval_min, wander_interval_max)
		choose_new_wander_target()

	Config.log_info("NPC初始化: " + npc_name)

func _on_body_entered(body: Node2D):
	"""玩家进入交互范围"""
	print("[DEBUG] NPC ", npc_name, " 检测到物体进入: ", body.name, " 是否在player组: ", body.is_in_group("player"))

	if body.is_in_group("player"):
		player = body
		print("[INFO] ✅ 玩家进入NPC范围: ", npc_name)

		if player.has_method("set_nearby_npc"):
			player.set_nearby_npc(self)
		else:
			print("[ERROR] 玩家没有set_nearby_npc方法!")

		# 显示提示
		show_interaction_hint()

func _on_body_exited(body: Node2D):
	"""玩家离开交互范围"""
	print("[DEBUG] NPC ", npc_name, " 检测到物体离开: ", body.name)

	if body.is_in_group("player"):
		print("[INFO] ❌ 玩家离开NPC范围: ", npc_name)

		if player != null and player.has_method("set_nearby_npc"):
			player.set_nearby_npc(null)
		player = null

		# 隐藏提示
		hide_interaction_hint()

func show_interaction_hint():
	"""显示交互提示"""
	if interaction_hint:
		interaction_hint.visible = true
		print("[INFO] 显示交互提示: ", npc_name)

func hide_interaction_hint():
	"""隐藏交互提示"""
	if interaction_hint:
		interaction_hint.visible = false
		print("[INFO] 隐藏交互提示: ", npc_name)

func update_dialogue(dialogue: String):
	"""更新NPC对话内容"""
	current_dialogue = dialogue
	dialogue_label.text = dialogue
	dialogue_label.visible = true

	# 10秒后隐藏对话 (增加显示时间)
	await get_tree().create_timer(10.0).timeout
	dialogue_label.visible = false

func get_npc_name() -> String:
	return npc_name

func get_npc_title() -> String:
	return npc_title

# ⭐ 物理更新 - 处理移动
func _physics_process(delta: float):
	"""物理更新 - 处理移动"""
	# 如果正在与玩家交互,停止移动
	if is_interacting:
		velocity = Vector2.ZERO
		move_and_slide()
		# 播放idle动画
		if animated_sprite.sprite_frames != null and animated_sprite.sprite_frames.has_animation("idle"):
			animated_sprite.play("idle")
		return

	# 如果未启用巡逻,不移动
	if not wander_enabled:
		return

	# 更新巡逻计时器
	wander_timer -= delta

	# 如果计时器结束,选择新目标并开始移动
	if wander_timer <= 0:
		choose_new_wander_target()
		wander_timer = randf_range(wander_interval_min, wander_interval_max)

	# 如果正在巡逻,移动到目标
	if is_wandering:
		# 检查是否到达目标
		if global_position.distance_to(wander_target) < 10:
			# 到达目标,停止移动
			is_wandering = false
			velocity = Vector2.ZERO
			move_and_slide()
			# 播放idle动画
			if animated_sprite.sprite_frames != null and animated_sprite.sprite_frames.has_animation("idle"):
				animated_sprite.play("idle")
		else:
			# 继续移动到目标
			var direction = (wander_target - global_position).normalized()
			velocity = direction * move_speed
			move_and_slide()
			# 更新动画
			update_animation(direction)
	else:
		# 停止移动
		velocity = Vector2.ZERO
		move_and_slide()
		# 播放idle动画
		if animated_sprite.sprite_frames != null and animated_sprite.sprite_frames.has_animation("idle"):
			animated_sprite.play("idle")

# ⭐ 选择新的巡逻目标
func choose_new_wander_target():
	"""选择新的巡逻目标"""
	# 在出生位置附近随机选择一个点
	var offset = Vector2(
		randf_range(-wander_range, wander_range),
		randf_range(-wander_range, wander_range)
	)
	wander_target = spawn_position + offset
	is_wandering = true

	Config.log_info("NPC %s 选择新目标: %s" % [npc_name, wander_target])

# ⭐ 更新动画
func update_animation(direction: Vector2):
	"""更新动画"""
	if animated_sprite.sprite_frames == null:
		return

	if direction.length() > 0:
		# 移动动画
		if abs(direction.x) > abs(direction.y):
			# 左右移动
			if direction.x > 0:
				if animated_sprite.sprite_frames.has_animation("walk_right"):
					animated_sprite.play("walk_right")
				elif animated_sprite.sprite_frames.has_animation("walk"):
					animated_sprite.play("walk")
					animated_sprite.flip_h = false
			else:
				if animated_sprite.sprite_frames.has_animation("walk_left"):
					animated_sprite.play("walk_left")
				elif animated_sprite.sprite_frames.has_animation("walk"):
					animated_sprite.play("walk")
					animated_sprite.flip_h = true
		else:
			# 上下移动
			if direction.y > 0:
				if animated_sprite.sprite_frames.has_animation("walk_down"):
					animated_sprite.play("walk_down")
				elif animated_sprite.sprite_frames.has_animation("walk"):
					animated_sprite.play("walk")
			else:
				if animated_sprite.sprite_frames.has_animation("walk_up"):
					animated_sprite.play("walk_up")
				elif animated_sprite.sprite_frames.has_animation("walk"):
					animated_sprite.play("walk")
	else:
		# 静止动画
		if animated_sprite.sprite_frames.has_animation("idle"):
			animated_sprite.play("idle")

# ⭐ 设置交互状态
func set_interacting(interacting: bool):
	"""设置交互状态"""
	is_interacting = interacting
	if interacting:
		Config.log_info("NPC %s 进入交互状态,停止移动" % npc_name)
	else:
		Config.log_info("NPC %s 退出交互状态,恢复移动" % npc_name)
