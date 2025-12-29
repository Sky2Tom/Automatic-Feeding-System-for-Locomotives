import subprocess
import os
import sys

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
script_path = os.path.join(current_dir, "web_server.py")

print(f"Starting {script_path}...")

# 在不同平台上启动脱离控制台的进程
try:
    if sys.platform == "win32":
        DETACHED_PROCESS = 0x00000008
        process = subprocess.Popen(
            [sys.executable, script_path],
            creationflags=DETACHED_PROCESS,
            close_fds=True,
            cwd=current_dir
        )
    else:
        # macOS/Linux
        process = subprocess.Popen(
            [sys.executable, script_path],
            close_fds=True,
            cwd=current_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
    print(f"Process started with PID: {process.pid}")
except Exception as e:
    print(f"Failed to start process: {e}")



