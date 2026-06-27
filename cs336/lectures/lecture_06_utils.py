import torch
from torch_util import get_device

# util files moved here to de-clutter the lecture debugger steps..  

def check_equal(f1, f2):
    x = torch.randn(2048, device=get_device())
    y1 = f1(x)
    y2 = f2(x)
    assert torch.allclose(y1, y2, atol=1e-6)


def check_equal2(f1, f2):
    x = torch.randn(2048, 2048, device=get_device())
    y1 = f1(x)
    y2 = f2(x)
    assert torch.allclose(y1, y2, atol=1e-6)


def get_local_url(path: str) -> str:
    #return f"http://localhost:8000/{path}"
    return "https://github.com/stanford-cs336/spring2025-lectures/blob/main/" + path;


def round1(x: float) -> float:
    """Round to 1 decimal place."""
    return round(x, 1)


def mean(x: list[float]) -> float:
    return sum(x) / len(x)