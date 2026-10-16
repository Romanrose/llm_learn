#!/usr/bin/env python3
"""
InnoCore AI - Installation Script
研创·智核 - 安装脚本
"""

import subprocess
import sys
from pathlib import Path

def install_core_deps():
    """Install only core dependencies"""
    print("Installing core dependencies...")
    
    core_deps = [
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "python-multipart==0.0.6",
        "python-dotenv==1.0.0",
        "pydantic==2.5.0",
        "httpx==0.25.2",
        "requests==2.31.0"
    ]
    
    for dep in core_deps:
        try:
            print(f"  Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"  [OK] {dep} installed")
        except subprocess.CalledProcessError as e:
            print(f"  [ERROR] Failed to install {dep}: {e}")
            return False
    
    print("[OK] Core dependencies installed successfully")
    return True

def create_env_file():
    """Create .env file"""
    env_file = Path(".env")
    if not env_file.exists():
        print("Creating .env file...")
        env_content = """# InnoCore AI Configuration
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///./innocore.db
SECRET_KEY=your_secret_key_here_change_this_in_production
DEBUG=True
"""
        env_file.write_text(env_content)
        print("[OK] .env file created")
        print("[WARNING] Please edit .env file and add your OpenAI API key")
    else:
        print("[OK] .env file already exists")

def create_directories():
    """Create necessary directories"""
    dirs = ["data", "logs"]
    for dir_path in dirs:
        Path(dir_path).mkdir(exist_ok=True)
    print("[OK] Directories created")

def main():
    print("InnoCore AI - Installation")
    print("=" * 40)
    
    # Install core dependencies
    if not install_core_deps():
        print("[ERROR] Installation failed")
        return
    
    # Create environment file
    create_env_file()
    
    # Create directories
    create_directories()
    
    print("\n[SUCCESS] Installation completed!")
    print("Next steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Run: python run.py")
    print("3. Open: http://localhost:8000")

if __name__ == "__main__":
    main()