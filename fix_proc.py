import os

def fix_file(path):
    with open(path, 'r') as f:
        lines = f.readlines()

    new_lines = []
    skip = False
    for line in lines:
        if 'def check_process' in line:
            new_lines.append('def check_process(name, is_python=False):\n')
            new_lines.append('    try:\n')
            new_lines.append('        if sys.platform == "win32":\n')
            new_lines.append('            cmd = ["tasklist", "/FI", f"IMAGENAME eq {name}"] if not is_python else ["powershell", "-Command", f"Get-Process | Where-Object {{ $_.CommandLine -like \'*{name}*\' }}"]\n')
            new_lines.append('            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)\n')
            new_lines.append('            return name.lower() in result.stdout.lower()\n')
            new_lines.append('        else:\n')
            new_lines.append('            cmd = f"pgrep -af {name}" if is_python else f"pgrep -x {name}"\n')
            new_lines.append('            result = subprocess.run(cmd, shell=True, capture_output=True)\n')
            new_lines.append('            return result.returncode == 0\n')
            new_lines.append('    except:\n')
            new_lines.append('        return False\n')
            skip = True
        elif skip and line.startswith('    ') or line.strip() == '':
            continue
        elif skip:
            skip = False
            new_lines.append(line)
        else:
            new_lines.append(line)

    with open(path, 'w') as f:
        f.writelines(new_lines)

import sys
# Make sure sys is imported in the files
def add_import_sys(path):
    with open(path, 'r') as f:
        content = f.read()
    if 'import sys' not in content:
        content = 'import sys\n' + content
        with open(path, 'w') as f:
            f.write(content)

add_import_sys('miner_web_unified.py')
add_import_sys('miner_kanban.py')
# Actually fix_file is a bit risky with complex logic, let's just manually rewrite the function using sed or cat.
