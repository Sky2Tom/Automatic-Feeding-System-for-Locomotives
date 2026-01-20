import sys
import os
import time
import threading
import json
import logging
from flask import Flask, render_template, Response, jsonify, request, send_from_directory
import cv2
import numpy as np
try:
    from paddleocr import PaddleOCR
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logging.error("PaddleOCR not installed. Please install paddleocr and paddlepaddle.")

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

# ====== 视觉识别 (OCR) 全局状态 ======
LATEST_VISION_RESULT = {
    "train_no": "--",
    "model": "--",
    "dim_l": "--",
    "dim_w": "--",
    "dim_h": "--"
}

ocr_instance = None
if OCR_AVAILABLE:
    try:
        logging.info("Initializing PaddleOCR...")
        # 参照 shext.py 的初始化参数
        ocr_instance = PaddleOCR(use_angle_cls=False, lang='en', enable_mkldnn=True, 
                                 use_doc_unwarping=False, use_doc_orientation_classify=False)
        logging.info("PaddleOCR initialized successfully")
    except Exception as e:
        logging.error(f"PaddleOCR initialization failed: {e}")
        ocr_instance = None

class CameraManager:
    """单例摄像头管理器，支持 MJPEG 推流和后台 OCR"""
    def __init__(self, device_index=0):
        self.cap = cv2.VideoCapture(device_index)
        self.lock = threading.Lock()
        self.running = True
        self.latest_frame = None
        
        # 启动抓帧线程
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        
        # 启动 OCR 线程
        self.ocr_thread = threading.Thread(target=self._ocr_loop, daemon=True)
        self.ocr_thread.start()

    def _capture_loop(self):
        while self.running:
            success, frame = self.cap.read()
            if success:
                with self.lock:
                    self.latest_frame = frame
            time.sleep(0.03)  # 约 30fps

    def _ocr_loop(self):
        global LATEST_VISION_RESULT
        while self.running:
            if ocr_instance and self.latest_frame is not None:
                try:
                    # 复制当前帧进行处理
                    with self.lock:
                        img = self.latest_frame.copy()
                    
                    # 参照 shext.py 的处理逻辑
                    rgb_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    result = ocr_instance.ocr(rgb_frame)
                    
                    filtered_texts = []
                    if result:
                        for line in result:
                            if line:
                                # 严格参照 shext.py 的访问方式
                                try:
                                    text = line["rec_texts"]
                                    scores = line["rec_scores"]
                                    for i, confidence in enumerate(scores):
                                        if confidence >= 0.7:
                                            filtered_texts.append(text[i])
                                except (KeyError, TypeError):
                                    # 兼容标准 PaddleOCR 格式 [[[box], [text, score]], ...]
                                    if isinstance(line, list) and len(line) > 0:
                                        for res in line:
                                            if isinstance(res, list) and len(res) == 2:
                                                box, (txt, score) = res
                                                if score >= 0.7:
                                                    filtered_texts.append(txt)
                    
                    if filtered_texts:
                        final_text = "".join(filtered_texts)
                        LATEST_VISION_RESULT["train_no"] = final_text
                        
                        # 如果识别到特定的型号（如 C64），尝试从数据库或预设匹配
                        self._match_train_info(final_text)
                except Exception as e:
                    logging.error(f"OCR process error: {e}")
            
            time.sleep(1)  # OCR 识别不需要太频繁，每秒一次即可

    def _match_train_info(self, train_no):
        global LATEST_VISION_RESULT, db_manager
        import re
        
        # 1. 预处理：转大写并清理干扰字符
        train_no_upper = train_no.upper()
        
        # OCR 容错：处理常见的 'C' 被误识为 'G'、'0'、'6' 的情况
        # 货车编号通常以 C (敞车)、P (棚车)、N (平车) 等开头
        if re.match(r'^[G06](70|64|80|62)', train_no_upper):
            train_no_upper = 'C' + train_no_upper[1:]
        
        train_no_clean = re.sub(r'[^A-Z0-9]', '', train_no_upper)
        
        matched = False
        
        # 2. 预置车型尺寸库（涵盖更多型号及变体）
        defaults = {
            "C62": {"model": "C62", "dim_l": "12488 mm", "dim_w": "2798 mm", "dim_h": "2000 mm"},
            "C64": {"model": "C64", "dim_l": "12500 mm", "dim_w": "3200 mm", "dim_h": "2500 mm"},
            "C64K": {"model": "C64K", "dim_l": "12490 mm", "dim_w": "2890 mm", "dim_h": "2500 mm"},
            "C70": {"model": "C70", "dim_l": "13000 mm", "dim_w": "2892 mm", "dim_h": "2050 mm"},
            "C70H": {"model": "C70H", "dim_l": "13000 mm", "dim_w": "2892 mm", "dim_h": "2050 mm"},
            "C76": {"model": "C76", "dim_l": "10520 mm", "dim_w": "2974 mm", "dim_h": "--"},
            "C76A": {"model": "C76A", "dim_l": "10520 mm", "dim_w": "2974 mm", "dim_h": "--"},
            "C76B": {"model": "C76B", "dim_l": "10400 mm", "dim_w": "2974 mm", "dim_h": "--"},
            "C76C": {"model": "C76C", "dim_l": "10400 mm", "dim_w": "2974 mm", "dim_h": "--"},
            "C76H": {"model": "C76H", "dim_l": "10520 mm", "dim_w": "2974 mm", "dim_h": "--"},
            "C80": {"model": "C80", "dim_l": "10728 mm", "dim_w": "2946 mm", "dim_h": "3500 mm"},
            "C80A": {"model": "C80A", "dim_l": "10550 mm", "dim_w": "2876 mm", "dim_h": "2700 mm"},
            "C80B": {"model": "C80B", "dim_l": "10550 mm", "dim_w": "2876 mm", "dim_h": "2700 mm"},
            "C80C": {"model": "C80C", "dim_l": "10000 mm", "dim_w": "2700 mm", "dim_h": "--"},
            "NX70": {"model": "NX70", "dim_l": "13500 mm", "dim_w": "3000 mm", "dim_h": "--"},
            "P62": {"model": "P62", "dim_l": "16438 mm", "dim_w": "3200 mm", "dim_h": "4200 mm"}
        }
        
        # 排序：优先匹配较长的关键字（如 C70H 优先于 C70）
        sorted_keys = sorted(defaults.keys(), key=len, reverse=True)
        
        # 3. 匹配策略：先尝试前缀匹配，再尝试包含匹配
        # 首先尝试前缀匹配
        for key in sorted_keys:
            if train_no_clean.startswith(key):
                LATEST_VISION_RESULT.update(defaults[key])
                matched = True
                logging.info(f"车型前缀匹配成功: {train_no} -> {key}")
                break
        
        # 如果前缀没匹配上，尝试子串匹配
        if not matched:
            for key in sorted_keys:
                if key in train_no_clean:
                    LATEST_VISION_RESULT.update(defaults[key])
                    matched = True
                    logging.info(f"车型子串匹配成功: {train_no} -> {key}")
                    break
        
        # 4. 如果本地库未匹配，尝试数据库查询
        if not matched and db_manager:
            try:
                # 这里的查询逻辑取决于数据库表结构，暂按 ID 模糊匹配
                with db_manager._connect() as conn:
                    cur = conn.cursor()
                    # 尝试匹配 TrainTypeID
                    for key in ["C64", "C70", "C80", "P62"]:
                        if key in train_no.upper():
                            cur.execute(f"SELECT * FROM [dbo].[Train Model Table] WHERE TrainTypeID = '{key}'")
                            row = cur.fetchone()
                            if row:
                                cols = [d[0] for d in cur.description]
                                r = dict(zip(cols, row))
                                LATEST_VISION_RESULT.update({
                                    "model": f"型号: {r['TrainTypeID']}",
                                    "dim_l": f"{r['ExLength']} mm",
                                    "dim_w": f"{r['ExWidth']} mm",
                                    "dim_h": f"{r['ExHeight']} mm"
                                })
                                matched = True
                                break
            except Exception as e:
                logging.error(f"Database lookup failed during OCR match: {e}")

        if not matched:
            LATEST_VISION_RESULT.update({
                "model": "未知型号",
                "dim_l": "--", "dim_w": "--", "dim_h": "--"
            })

    def get_frame_bytes(self):
        if self.latest_frame is None:
            return None
        with self.lock:
            # 可以在这里在画面上画出识别结果，类似 shext.py
            display_frame = self.latest_frame.copy()
            if LATEST_VISION_RESULT["train_no"] != "--":
                cv2.putText(display_frame, f"TRAIN: {LATEST_VISION_RESULT['train_no']}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            success, buffer = cv2.imencode('.jpg', display_frame)
            if success:
                return buffer.tobytes()
        return None

# 初始化摄像头管理器
camera_mgr = CameraManager(0)

# ====== 路由定义 ======

HISTORY_FILE = os.path.join(current_dir, "feeding_history.json")

def load_history_from_json():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"加载历史数据失败: {e}")
        return []

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
            
            # 注入真实的视觉识别结果
            snap["vision_result"] = LATEST_VISION_RESULT
            
            return jsonify(snap)
        else:
            return jsonify({"error": "Backend not available", "all_data_dict": {}, "vision_result": LATEST_VISION_RESULT})
            
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
    """获取下料历史，从JSON文件读取并支持过滤"""
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    feeder_id = request.args.get('feeder_id')
    locomotive_id = request.args.get('locomotive_id')

    all_history = load_history_from_json()
    filtered_history = []

    for item in all_history:
        # 时间过滤
        if start_time and item['time'] < start_time:
            continue
        if end_time and item['time'] > end_time:
            continue
        # 下料机号过滤
        if feeder_id and feeder_id != item['feeder_id']:
            continue
        # 车号过滤
        if locomotive_id and locomotive_id not in item['locomotive_id']:
            continue
        
        filtered_history.append(item)

    # 按时间倒序
    filtered_history.sort(key=lambda x: x['time'], reverse=True)
    
    return jsonify(filtered_history)

# 摄像头串流 (MJPEG)
def gen_frames():
    while True:
        frame_bytes = camera_mgr.get_frame_bytes()
        if frame_bytes is None:
            time.sleep(0.1)
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """摄像头实时视频流接口"""
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/control', methods=['POST'])
def control_machine():
    """下料机控制接口 (调用 Modbus 写操作)"""
    if not BACKEND_AVAILABLE or not backend_app:
        return jsonify({"status": "error", "message": "Backend not available"}), 503
        
    data = request.json
    cmd = data.get('command')
    print(f"接收到控制指令: {cmd}")
    
    # 根据指令类型调用写函数
    # 映射示例：将前端指令转为具体的 Modbus 地址和值
    try:
        if cmd == 'VALVE_OPEN':
            # 假设地址 12 是阀门控制线圈，0xFF00 表示打开
            DATAS.add_write_task('write_valve_open', 2, 5, 12, 0xFF00)
        elif cmd == 'VALVE_CLOSE':
            DATAS.add_write_task('write_valve_close', 2, 5, 12, 0x0000)
        elif cmd == 'LIFT_UP':
            # 假设地址 16 是升降高度寄存器
            DATAS.add_write_task('write_lift_up', 2, 6, 13, 2000)
        elif cmd == 'LIFT_DOWN':
            DATAS.add_write_task('write_lift_down', 2, 6, 13, 0)
        else:
            print(f"接收到未知控制指令: {cmd}")
            return jsonify({"status": "error", "message": f"Unknown command: {cmd}"})
            
        return jsonify({"status": "success", "command_queued": cmd})
    except Exception as e:
        logging.error(f"发送控制指令失败: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

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

