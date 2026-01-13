import sys
import os
import time
import threading
import json
import logging
from flask import Flask, render_template, Response, jsonify, request, send_from_directory

# 配置日志
logging.basicConfig(filename='web_error.log', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s: %(message)s')

# 重定向 stdout 和 stderr，防止脱离进程时崩溃
class LoggerWriter:
    def __init__(self, level):
        self.level = level
    def write(self, message):
        if message.strip():
            self.level(message.strip())
    def flush(self):
        pass

sys.stdout = LoggerWriter(logging.info)
sys.stderr = LoggerWriter(logging.error)

# 设置路径以导入 Back_end 目录下的模块
current_dir = os.path.dirname(os.path.abspath(__file__))
# 网页代码现在在 Web 文件夹中，后端在上一级目录
parent_dir = os.path.dirname(current_dir)
back_end_path = os.path.join(parent_dir, "Back_end")
sys.path.append(parent_dir)  # 添加根目录
sys.path.append(back_end_path)

logging.info(f"Current dir: {current_dir}")
logging.info(f"Back_end path: {back_end_path}")

# 导入后端核心模块
try:
    from train_group_reader_oop import DATAS, TrainGroupReaderApp
    from data12 import TrainDatabaseManager
    BACKEND_AVAILABLE = True
    logging.info("Backend modules loaded successfully")
except Exception as e:
    logging.error(f"后端模块加载失败: {e}")
    BACKEND_AVAILABLE = False

app = Flask(__name__)

# 将 Flask 日志也记录到文件中
log = logging.getLogger('werkzeug')
log.setLevel(logging.DEBUG)
log.addHandler(logging.FileHandler('web_error.log'))

# ====== 全局配置 ======
START_BACKEND = True
ACTIVE_PORT   = "COM6"
PASSIVE_PORT  = "COM6"
BAUDRATE      = 9600

# 数据库配置
DB_CONFIG = {
    "server": "WIN-DNI5FVM376E",
    "database": "RailwayCoalManagement",
    "username": "sa",
    "password": "220242236"
}

# ====== 初始化后端服务 ======
backend_app = None
db_manager = None

if BACKEND_AVAILABLE:
    def run_qt_backend():
        """在后台线程中启动 Qt 事件循环，驱动 Modbus 轮询"""
        global backend_app
        from PyQt5.QtWidgets import QApplication
        
        # 1. 必须在线程内创建一个 QApplication 实例
        qt_app = QApplication.instance()
        if qt_app is None:
            qt_app = QApplication(sys.argv)
        
        try:
            logging.info("Initializing Modbus Backend with Qt Loop...")
            # 2. 实例化后端
            backend_app = TrainGroupReaderApp(ACTIVE_PORT, PASSIVE_PORT, BAUDRATE)
            # 3. 启动内部的所有定时器
            backend_app.start()
            
            print(f"Modbus 后端已启动 (串口: {ACTIVE_PORT})，正在轮询激光数据...")
            # 4. 关键：进入 Qt 事件循环，这会让 QTimer 开始跳动
            qt_app.exec_()
        except Exception as e:
            logging.error(f"Modbus 后端运行异常: {e}")

    if START_BACKEND:
        # 使用守护线程启动 Qt 循环
        backend_thread = threading.Thread(target=run_qt_backend, daemon=True)
        backend_thread.start()
        # 给后端一点启动时间
        time.sleep(1)

    try:
        logging.info("Initializing DB Manager...")
        db_manager = TrainDatabaseManager(**DB_CONFIG)
        logging.info("DB Manager ready")
    except Exception as e:
        logging.error(f"数据库连接失败: {e}")

# ====== 路由定义 ======

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def login():
    """简单的登录接口"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if username == "1" and password == "1":
        return jsonify({"status": "success", "message": "Login successful"})
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401

@app.route('/api/snapshot')
def get_snapshot():
    """获取实时的 Modbus 数据快照，强制返回真实数据"""
    try:
        if BACKEND_AVAILABLE:
            # 1. 直接从数据仓库获取最新快照
            snap = DATAS.snapshot()
            
            # 2. 调试打印：在服务器控制台输出当前真实数据内容，方便排查
            real_data = snap.get("all_data_dict", {})
            
            # 打印最近收到的任何帧（用于排查被动接收）
            last_func = snap.get("function_name", "None")
            last_addr = snap.get("RxAddr", 0)
            last_data = snap.get("RxData", [])
            print(f"--- [API Debug] 最近一帧来自: {last_func}, 地址: {last_addr}, 数据长度: {len(last_data)} ---")
            
            # 打印激光数据
            if "read_laser_sensor" in real_data:
                laser_val = real_data["read_laser_sensor"].get("laser_decimal")
                print(f"--- 接口正在推送真实激光数据: {laser_val} mm ---")
            elif "passive_rx" == last_func and last_addr == 4:
                print(f"--- 警告：收到地址 4 (激光传感器) 的被动帧，但尚未进入解析逻辑 ---")
            
            # 打印料位计数据
            if "read_level_gauge_sensor" in real_data:
                level_val = real_data["read_level_gauge_sensor"].get("material_level")
                print(f"--- 接口正在推送真实料位计数据: {level_val} m ---")
            elif "passive_rx" == last_func and last_addr == 3:
                print(f"--- 警告：收到地址 3 (料位计) 的被动帧，但尚未进入解析逻辑 ---")
            
            if not real_data:
                print("--- 警告：后端尚未存入任何汇总解析数据 (all_data_dict 为空) ---")
            
            # 3. 即使数据暂时为空，也直接返回 snap，不再使用 get_mock_snapshot 覆盖
            # 这样如果没数据，界面会显示 "--"，而不是显示误导性的假数据
            return jsonify(snap)
        else:
            return jsonify({"error": "Backend not available", "all_data_dict": {}})
            
    except Exception as e:
        logging.error(f"get_snapshot 接口出错: {e}")
        print(f"API Error: {e}")
        return jsonify({"error": str(e), "all_data_dict": {}})

def get_mock_snapshot():
    """生成科技感十足的模拟快照数据"""
    return {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "all_data_dict": {
            "read_coils_0_21": {
                "loading_type": 1, "is_in_place": 1, "tractor_status": 1, 
                "is_overspeed": 0, "is_alarm": 0, "is_full": 0, "bin_gate_status": 1
            },
            "read_holding_registers_16_24": {
                "train_speed": 0.25,
                "positioning_distance": 1200,
                "bin_gate_opening_status": 45,
                "lifting_height_status": 1500,
                "lower_flap_angle_status": 30
            },
            "read_level_gauge_sensor": {
                "material_level": 4.25
            },
            "read_laser_sensor": {
                "laser_decimal": 24788
            }
        },
        "vision_result": {
            "train_no": "C64 880256",
            "model": "通用敞车 C64",
            "dim_l": "12500 mm",
            "dim_w": "3200 mm",
            "dim_h": "3500 mm"
        }
    }

@app.route('/api/train_models', methods=['GET'])
def get_train_models():
    """获取火车型号列表，若数据库连接失败则返回假数据"""
    if db_manager:
        try:
            with db_manager._connect() as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM [dbo].[Train Model Table]")
                rows = cur.fetchall()
                cols = [d[0] for d in cur.description]
                result = [dict(zip(cols, [str(v) if v is not None else "" for v in r])) for r in rows]
                return jsonify(result)
        except Exception:
            pass # 发生错误则跳转到下方的假数据逻辑
            
    # 假数据列表
    mock_models = [
        {"TrainTypeID": "C64", "ExLength": "12500", "ExWidth": "3200", "ExHeight": "3500", "Volume": "60", "LoadWeight": "64"},
        {"TrainTypeID": "C70", "ExLength": "13976", "ExWidth": "3180", "ExHeight": "3600", "Volume": "70", "LoadWeight": "70"},
        {"TrainTypeID": "C80", "ExLength": "12000", "ExWidth": "3200", "ExHeight": "3800", "Volume": "80", "LoadWeight": "80"},
        {"TrainTypeID": "P62", "ExLength": "16438", "ExWidth": "3200", "ExHeight": "4200", "Volume": "120", "LoadWeight": "60"}
    ]
    return jsonify(mock_models)

@app.route('/api/history', methods=['GET'])
def get_history():
    """获取下料历史，若数据库连接失败则返回假数据"""
    if db_manager:
        try:
            minutes = request.args.get('minutes', default=60, type=int)
            with db_manager._connect() as conn:
                cur = conn.cursor()
                query = f"SELECT TOP 100 * FROM [dbo].[Layoff History Table] WHERE [Time] >= DATEADD(MINUTE, -{minutes}, GETDATE()) ORDER BY [Time] DESC"
                cur.execute(query)
                rows = cur.fetchall()
                cols = [d[0] for d in cur.description]
                result = [dict(zip(cols, [str(v) if v is not None else "" for v in r])) for r in rows]
                return jsonify(result)
        except Exception:
            pass

    # 假历史记录
    mock_history = [
        {"Time": "2025-12-25 16:30:05", "MaterialID": "M001", "WarehouseID": "WH111", "TrainTypeID": "C64", "LayoffWeight": "15.5"},
        {"Time": "2025-12-25 16:15:20", "MaterialID": "M002", "WarehouseID": "WH111", "TrainTypeID": "C70", "LayoffWeight": "22.3"},
        {"Time": "2025-12-25 15:55:45", "MaterialID": "M001", "WarehouseID": "WH112", "TrainTypeID": "C80", "LayoffWeight": "30.1"},
        {"Time": "2025-12-25 15:20:10", "MaterialID": "M003", "WarehouseID": "WH111", "TrainTypeID": "C64", "LayoffWeight": "12.8"}
    ]
    return jsonify(mock_history)

# 摄像头串流 (MJPEG)
import cv2
def gen_frames():
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # 可以在这里添加 OCR 逻辑，或者直接推流
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    camera.release()

@app.route('/video_feed')
def video_feed():
    """摄像头实时视频流接口"""
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/control', methods=['POST'])
def control_machine():
    """下料机控制接口 (模拟 Modbus 写操作)"""
    # 实际应用中应调用 backend_app 提供的写接口
    data = request.json
    print(f"接收到控制指令: {data}")
    return jsonify({"status": "success", "data_received": data})

if __name__ == '__main__':
    # 仅支持本地打开 (localhost)
    logging.info("Starting Flask app...")
    print("========================================")
    print("火车加料智能监控系统 - Web 版已就绪")
    print("请在浏览器中访问: http://127.0.0.1:5001")
    print("========================================")
    try:
        app.run(host='127.0.0.1', port=5001, debug=False, threaded=True, use_reloader=False)
    except Exception as e:
        logging.error(f"Flask failed to start: {e}")

