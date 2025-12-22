import subprocess
from pathlib import Path
import sys

BASE_DIR = Path("D:/Projects/instagramautomation")

def run_program(script_path: Path):
    result = subprocess.run(
        [sys.executable, script_path],
        check=False
    )
    if result.returncode != 0:
        print(f"Error: {script_path.name} failed.")
        exit(1)

run_program(BASE_DIR / "data.py")
run_program(BASE_DIR / "main.py")
run_program(BASE_DIR / "reelmaker.py")

gif_path = BASE_DIR / "gif.gif"

try:
    gif_path.unlink()
except FileNotFoundError:
    print("gif.gif not found, skipping delete.")

print("All programs executed successfully.")
