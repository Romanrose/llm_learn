#!/usr/bin/env python3
"""
InnoCore AI - Simple Setup Script
"""

import subprocess
import sys
from pathlib import Path

def main():
    print("InnoCore AI - Quick Setup")
    print("=" * 30)
    
    # Install basic dependencies without version conflicts
    basic_deps = [
        "fastapi",
        "uvicorn[standard]",
        "python-multipart",
        "python-dotenv"
    ]
    
    print("Installing basic dependencies...")
    for dep in basic_deps:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"[OK] {dep}")
        except subprocess.CalledProcessError:
            print(f"[SKIP] {dep} (may already exist)")
    
    # Create .env file
    env_file = Path(".env")
    if not env_file.exists():
        env_content = """# InnoCore AI Configuration
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///./innocore.db
SECRET_KEY=your_secret_key_here_change_this_in_production
DEBUG=True
"""
        env_file.write_text(env_content)
        print("[OK] .env file created")
    else:
        print("[OK] .env file exists")
    
    # Create directories
    Path("data").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    print("[OK] Directories created")
    
    print("\n[SUCCESS] Setup completed!")
    print("Next steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Run: python run.py")
    print("3. Open: http://localhost:8000")

if __name__ == "__main__":
    main()