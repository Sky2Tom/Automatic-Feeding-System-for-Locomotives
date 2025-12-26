import subprocess
import os
import sys
import time
import webbrowser

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
script_path = os.path.join(current_dir, "web_server.py")

print(f"正在启动服务器: {script_path}")

# 在 Windows 上启动脱离控制台的进程
try:
    DETACHED_PROCESS = 0x00000008
    process = subprocess.Popen(
        [sys.executable, script_path],
        creationflags=DETACHED_PROCESS,
        close_fds=True,
        cwd=current_dir
    )
    print(f"服务器已在后台启动，PID: {process.pid}")
    
    # 等待服务器启动
    print("等待服务器初始化 (5秒)...")
    time.sleep(5)
    
    # 使用 Python 打开网页
    url = "http://127.0.0.1:5000"
    print(f"正在尝试打开网页: {url}")
    webbrowser.open(url)
    print("操作完成。如果浏览器未弹出，请检查 web_error.log 或手动访问 http://127.0.0.1:5000")

except Exception as e:
    print(f"启动失败: {e}")



