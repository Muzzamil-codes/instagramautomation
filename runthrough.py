import subprocess
import os

PYTHON = "/home/ubuntu/instagramautomation/venv/bin/python3"

def run_program(command):
    process = subprocess.run(command, shell=True)
    if process.returncode != 0:
        print(f"Error: {command} failed.")
        exit(1)

run_program(f"{PYTHON} /home/ubuntu/instagramautomation/data.py")
run_program(f"{PYTHON} /home/ubuntu/instagramautomation/main.py")
run_program(f"{PYTHON} /home/ubuntu/instagramautomation/reelmaker.py")

try:
    os.remove("/home/ubuntu/instagramautomation/gif.gif")
except FileNotFoundError:
    print("gif.gif not found, skipping delete.")

print("All programs executed successfully.")
