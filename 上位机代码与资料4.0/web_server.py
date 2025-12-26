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
back_end_path = os.path.join(current_dir, "Back_end")
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
ACTIVE_PORT   = "COM4"
PASSIVE_PORT  = "COM2"
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
    if START_BACKEND:
        try:
            logging.info("Initializing Modbus Backend...")
            backend_app = TrainGroupReaderApp(ACTIVE_PORT, PASSIVE_PORT, BAUDRATE)
            # 在独立线程中启动后端，避免阻塞 Flask
            backend_thread = threading.Thread(target=backend_app.start, daemon=True)
            backend_thread.start()
            logging.info("Modbus Backend thread started")
        except Exception as e:
            logging.error(f"Modbus 后端启动失败: {e}")

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
    """获取实时的 Modbus 数据快照，若无数据则返回模拟数据"""
    if BACKEND_AVAILABLE:
        snap = DATAS.snapshot()
        # 如果 snap 中没有实际数据，则提供模拟数据
        if not snap.get("all_data_dict"):
            snap = get_mock_snapshot()
    else:
        snap = get_mock_snapshot()
    return jsonify(snap)

def get_mock_snapshot():
    """生成科技感十足的模拟快照数据"""
    return {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "all_data_dict": {
            "read_coils_0_13": {"RxData": [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
            "read_holding_registers_32_39": {"RxData": ["001A", "002B", "000F", "03E8", "0000", "0000", "0000", "0000"]}
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
    print("请在浏览器中访问: http://127.0.0.1:5000")
    print("========================================")
    try:
        app.run(host='127.0.0.1', port=5000, debug=False, threaded=True, use_reloader=False)
    except Exception as e:
        logging.error(f"Flask failed to start: {e}")

