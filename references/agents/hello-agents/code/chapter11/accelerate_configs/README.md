# Accelerate配置文件说明

本目录包含用于分布式训练的Accelerate配置文件。

## 配置文件列表

### 1. multi_gpu_ddp.yaml
**数据并行(DDP)** - 最简单的多GPU训练方案

- **适用场景**: 单机多卡(2-8卡)
- **优点**: 简单、速度快
- **缺点**: 每个GPU需要完整模型副本
- **显存需求**: 与单GPU相同

**使用方法**:
```bash
accelerate launch --config_file accelerate_configs/multi_gpu_ddp.yaml train_script.py
```

### 2. deepspeed_zero2.yaml
**DeepSpeed ZeRO-2** - 优化器状态分片

- **适用场景**: 中等规模模型(1B-7B)
- **优点**: 降低显存占用,支持更大batch size
- **缺点**: 比DDP稍慢
- **显存节省**: ~30%

**使用方法**:
```bash
accelerate launch --config_file accelerate_configs/deepspeed_zero2.yaml train_script.py
```

### 3. deepspeed_zero3.yaml
**DeepSpeed ZeRO-3** - 完整模型分片

- **适用场景**: 大规模模型(>7B)
- **优点**: 最大程度降低显存占用
- **缺点**: 通信开销较大
- **显存节省**: ~50%

**使用方法**:
```bash
accelerate launch --config_file accelerate_configs/deepspeed_zero3.yaml train_script.py
```

## 快速开始

### 1. 安装依赖

```bash
pip install accelerate deepspeed
```

### 2. 配置Accelerate

**方式1: 使用配置文件**(推荐)
```bash
accelerate launch --config_file accelerate_configs/multi_gpu_ddp.yaml your_script.py
```

**方式2: 交互式配置**
```bash
accelerate config
```

**方式3: 命令行参数**
```bash
accelerate launch --num_processes 4 --mixed_precision fp16 your_script.py
```

### 3. 运行训练

```bash
# DDP训练(4卡)
accelerate launch --config_file accelerate_configs/multi_gpu_ddp.yaml 07_distributed_training.py

# DeepSpeed ZeRO-2训练(4卡)
accelerate launch --config_file accelerate_configs/deepspeed_zero2.yaml 07_distributed_training.py

# DeepSpeed ZeRO-3训练(4卡)
accelerate launch --config_file accelerate_configs/deepspeed_zero3.yaml 07_distributed_training.py
```

## 配置参数说明

### 通用参数

- `compute_environment`: 计算环境(LOCAL_MACHINE/AMAZON_SAGEMAKER等)
- `distributed_type`: 分布式类型(MULTI_GPU/DEEPSPEED/FSDP等)
- `num_processes`: 总进程数(通常等于GPU数量)
- `machine_rank`: 机器编号(主节点为0)
- `num_machines`: 机器数量
- `gpu_ids`: 使用的GPU ID(all表示使用所有GPU)
- `mixed_precision`: 混合精度训练(no/fp16/bf16)

### DeepSpeed参数

- `zero_stage`: ZeRO优化级别(1/2/3)
  - ZeRO-1: 优化器状态分片
  - ZeRO-2: 优化器状态+梯度分片
  - ZeRO-3: 优化器状态+梯度+模型参数分片

- `offload_optimizer_device`: 优化器状态卸载设备(none/cpu/nvme)
- `offload_param_device`: 模型参数卸载设备(none/cpu/nvme)
- `gradient_accumulation_steps`: 梯度累积步数
- `gradient_clipping`: 梯度裁剪阈值
- `zero3_init_flag`: ZeRO-3初始化标志

## 性能调优建议

### 1. Batch Size调整

分布式训练时,总batch size = `per_device_batch_size × num_gpus × gradient_accumulation_steps`

**示例**:
```python
# 单GPU: batch_size=4, gradient_accumulation=4, 总batch=16
# 4GPU DDP: batch_size=4, gradient_accumulation=1, 总batch=16
```

### 2. 学习率缩放

使用线性缩放规则:
```python
lr_new = lr_base × sqrt(total_batch_size_new / total_batch_size_base)
```

### 3. 混合精度训练

- **fp16**: 适合大多数场景,速度快
- **bf16**: 适合Ampere架构(A100/A6000),数值稳定性更好
- **no**: 不使用混合精度,精度最高但速度慢

### 4. 梯度累积

当显存不足时,可以增大`gradient_accumulation_steps`:
```yaml
deepspeed_config:
  gradient_accumulation_steps: 8  # 增大累积步数
```

## 常见问题

### Q1: 如何查看当前使用的配置?

```bash
accelerate env
```

### Q2: 多卡训练速度没有线性提升?

**可能原因**:
- 通信开销过大
- 数据加载瓶颈
- batch size太小

**解决方法**:
- 增大batch size
- 使用更快的数据加载器
- 检查网络带宽

### Q3: DeepSpeed训练卡住?

**可能原因**:
- 模型初始化问题
- 通信超时

**解决方法**:
```bash
# 启用调试日志
export ACCELERATE_LOG_LEVEL=INFO
export NCCL_DEBUG=INFO

# 增加超时时间
export NCCL_TIMEOUT=1800
```

### Q4: 如何在多节点上训练?

1. 在所有节点上安装相同的环境
2. 配置SSH免密登录
3. 修改配置文件中的`num_machines`和`main_process_ip`
4. 在每个节点上运行相同的命令

## 参考资源

- [Accelerate文档](https://huggingface.co/docs/accelerate)
- [DeepSpeed文档](https://www.deepspeed.ai/)
- [TRL分布式训练指南](https://huggingface.co/docs/trl/customization)

