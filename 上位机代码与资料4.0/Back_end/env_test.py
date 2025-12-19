import sys
import platform


def main():
    print("=" * 60)
    print("Python 环境自检脚本（env_test.py）")
    print("=" * 60)
    print(f"Python 可执行文件: {sys.executable}")
    print(f"Python 版本: {sys.version.split()[0]}")
    print(f"平台: {platform.system()} {platform.release()}")
    print()

    # 尝试导入项目中常用的关键库
    modules = [
        "PyQt5",
        "PyQt5.QtWidgets",
        "PyQt5.QtSerialPort",
        "pyodbc",
        "cv2",
    ]

    for name in modules:
        try:
            __import__(name)
            print(f"[OK ] 成功导入模块: {name}")
        except Exception as e:
            print(f"[FAIL] 导入模块失败: {name} -> {e}")

    print()
    print("如果上面关键模块大部分是 [OK]，说明 Python 环境基本配置成功。")
    print("如有 [FAIL]，请在该模块名后安装依赖，例如：")
    print("  conda install pyqt pyodbc opencv  或  pip install pyqt5 pyodbc opencv-python")
    print("=" * 60)


if __name__ == "__main__":
    main()


