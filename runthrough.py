import subprocess
import os

def run_program(command):
    process = subprocess.run(command, shell=True)
    if process.returncode != 0:
        print(f"Error: {command} failed.")
        exit(1)  # Exit if a program fails

run_program("python data.py")
run_program("python main.py")
run_program("python reelmaker.py")

os.remove("gif.gif")

print("All programs executed successfully.")
