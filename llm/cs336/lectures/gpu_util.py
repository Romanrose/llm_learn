import torch

def cuda_if_available(index: int = 0) -> torch.device:
    """Try to use the GPU if possible, otherwise, use CPU."""
    if torch.cuda.is_available():
        return torch.device(f"cuda:{index}")
    else:
        return torch.device("cpu")


def get_max_memory_usage(func):
    """Measure how much memmory calling `func` uses."""
    if not torch.cuda.is_available():
        return 0  # Can't measure it without GPUs!

    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    func()
    return torch.cuda.max_memory_allocated()