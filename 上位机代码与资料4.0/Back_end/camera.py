# camera_worker.py
import cv2
from PyQt5.QtCore import QThread, pyqtSignal  # PyQt6: from PyQt6.QtCore import QThread, Signal as pyqtSignal
from PyQt5.QtGui import QImage                # PyQt6: from PyQt6.QtGui import QImage

class CameraThread(QThread):
    frameReady = pyqtSignal(QImage)    # 每帧回调到主线程
    startedOk = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, device_index=0, width=None, height=None, fps=30, parent=None):
        super().__init__(parent)
        self.device_index = device_index
        self.width = width
        self.height = height
        self.fps = max(1, int(fps))
        self._running = False
        self._cap = None

    def run(self):
        try:
            self._cap = cv2.VideoCapture(self.device_index, cv2.CAP_DSHOW)
            if not self._cap.isOpened():
                raise RuntimeError(f"Cannot open camera (index={self.device_index})")
            if self.width:
                self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            if self.height:
                self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        except Exception as e:
            self.error.emit(str(e))
            return

        self.startedOk.emit()
        self._running = True

        # 控制采样间隔（尽量接近目标 fps）
        interval_ms = int(1000 / self.fps)

        while self._running:
            ok, frame = self._cap.read()
            if not ok or frame is None:
                continue

            # BGR -> RGB
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)

            # 把图送回界面（Qt 自动在线程间派发信号，slot 在主线程执行）
            self.frameReady.emit(qimg)

            # 轻微节流，避免占满CPU
            QThread.msleep(interval_ms)

        # 清理
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    def stop(self, wait_timeout_ms=1000):
        self._running = False
        # 优雅退出线程
        self.wait(wait_timeout_ms)

def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()  # 运行main函数
