"""
Usage:
    modal run modal_execute.py
    modal run modal_execute.py --module lecture_06
"""

import glob
import os
import modal

app = modal.App("cs336-edtrace-execute")

IGNORE = [".venv", "__pycache__", "var", ".git", "node_modules"]

# Files to copy back after execution (glob patterns relative to /root/lectures)
def output_patterns(module: str) -> list[str]:
    return [
        f"var/traces/{module}.json",
        "var/*-ptx.txt",
        "var/profiles.txt",
    ]

def _ignore(path) -> bool:
    return any(p in IGNORE for p in str(path).split("/"))

image = (
    modal.Image.from_registry("nvidia/cuda:13.2.0-cudnn-devel-ubuntu24.04", add_python="3.11")
    .pip_install("torch", "numpy", "sympy", "einops", "requests", "beautifulsoup4")
    .add_local_dir("edtrace/backend", "/root/edtrace_backend", copy=True)
    .run_commands("pip install /root/edtrace_backend")
    .add_local_dir(".", "/root/lectures", ignore=_ignore)
)


@app.function(
    image=image,
    #gpu="H100",
    gpu="B200:4",
    timeout=600,
)
def execute(module: str) -> dict[str, str]:
    import subprocess

    os.chdir("/root/lectures")
    os.makedirs("var/traces", exist_ok=True)

    result = subprocess.run(
        ["python", f"{module}.py"],
        #["python", "-m", "edtrace.execute", "-m", module],
        #["uv", "run", "nsys", "profile", "-w", "true", "-t", "cuda,ntvx", "python", "-m", "edtrace.execute", "-m", module],
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        print("STDERR:", result.stderr)
        raise RuntimeError(f"edtrace.execute failed with exit code {result.returncode}")

    # Collect all output files matching the patterns
    files = {}
    for pattern in output_patterns(module):
        for path in glob.glob(pattern):
            files[path] = open(path).read()
    return files


@app.local_entrypoint()
def main(module: str = "lecture_07"):
    print(f"Running edtrace.execute on Modal for: {module}")
    files = execute.remote(module)

    for path, content in files.items():
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        print(f"Saved {path} ({len(content):,} bytes)")
