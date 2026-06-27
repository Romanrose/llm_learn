# https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/a100/pdf/nvidia-a100-datasheet-us-nvidia-1758950-r4-web.pdf
a100_flop_per_sec = 312e12  # 312 TFLOP/s

# https://resources.nvidia.com/en-us-tensor-core/nvidia-tensor-core-gpu-datasheet
h100_flop_per_sec = 1979e12 / 2  # 1979 TFLOP/s with sparsity (BF16 tensor core)
