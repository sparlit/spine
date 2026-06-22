import sys
import os

filepath = "miner_web_unified.py"
with open(filepath, "r") as f:
    content = f.read()

old_func = """def check_process(name, is_python=False):
    try:
        if is_python:
            cmd = f"pgrep -af {name}"
        else:
            cmd = f"pgrep -x {name}"
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except:
        return False"""

new_func = """def check_process(name, is_python=False):
    try:
        if sys.platform == "win32":
            if is_python:
                # On Windows, we check if the name is in the command line of python processes
                cmd = f'powershell "Get-Process | Where-Object { $_.CommandLine -like \"*{{name}}*\" }"'
            else:
                cmd = f'tasklist /FI "IMAGENAME eq {{name}}"'
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return name.lower() in result.stdout.lower()
        else:
            if is_python:
                cmd = f"pgrep -af {name}"
            else:
                cmd = f"pgrep -x {name}"
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.returncode == 0
    except:
        return False"""

# Wait, the escaping in the string above might be messy. Let me do it more carefully.
