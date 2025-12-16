import time
import threading
import sys
import os
from typing import Callable, Dict, Optional, Tuple

print("[INIT] Starting imports...", file=sys.stderr)
sys.stderr.flush()

# Optional: cv2
CV2_AVAILABLE = False
try:
    import cv2  # type: ignore
    print("[INIT] cv2 imported", file=sys.stderr)
    sys.stderr.flush()
    CV2_AVAILABLE = True
except Exception as e:
    print(f"[INIT] cv2 not available: {e}", file=sys.stderr)
    sys.stderr.flush()
    cv2 = None

try:
    import numpy as np  # type: ignore
    print("[INIT] numpy imported", file=sys.stderr)
    sys.stderr.flush()
except Exception as e:
    print(f"[INIT] numpy import failed: {e}", file=sys.stderr)
    sys.stderr.flush()
    np = None

# Optional: mss for fast screen capture
MSS_AVAILABLE = False
try:
    from mss import mss  # type: ignore
    print("[INIT] mss imported", file=sys.stderr)
    sys.stderr.flush()
    MSS_AVAILABLE = True
except Exception as e:
    print(f"[INIT] mss not available: {e}", file=sys.stderr)
    sys.stderr.flush()
    mss = None

# 导入 API 模块
print("[INIT] Importing API module...", file=sys.stderr)
try:
    from ai.model import API
    print("[INIT] API imported successfully", file=sys.stderr)
except ImportError:
    # 尝试相对导入（如果在 IDE 中直接运行 tool.py）
    try:
        import sys
        sys.path.append('..')
        from model import API
        print("[INIT] API imported (relative) successfully", file=sys.stderr)
    except Exception as e:
        print(f"[INIT] Warning: Could not import API module: {e}", file=sys.stderr)
        API = None

print("[INIT] All imports completed", file=sys.stderr)

def _get_analysis_safe(payload: dict) -> dict:
    if API and hasattr(API, 'get_analysis'):
        return API.get_analysis(payload)
    return {'status': 'unknown', 'duration': 0, 'message': 'API.get_analysis not available'}

class CameraAnalyzer:
    """
    摄像头分析类：使用 OpenCV 调用摄像头并捕获画面。
    
    功能：
    1. 调用摄像头捕获画面。
    2. 提供基础图像分析（如亮度、边缘检测等）。
    """
    def __init__(self, camera_id=0):
        self.camera_id = camera_id
        self.cap = None

    def start(self):
        """启动摄像头"""
        if not CV2_AVAILABLE:
            print("[CameraAnalyzer] OpenCV not available.", file=sys.stderr)
            return False
        
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            if not self.cap.isOpened():
                print(f"[CameraAnalyzer] Failed to open camera {self.camera_id}", file=sys.stderr)
                return False
            print(f"[CameraAnalyzer] Camera {self.camera_id} started.", file=sys.stderr)
            return True
        except Exception as e:
            print(f"[CameraAnalyzer] Error starting camera: {e}", file=sys.stderr)
            return False

    def stop(self):
        """释放摄像头资源"""
        if self.cap:
            self.cap.release()
            self.cap = None
        print("[CameraAnalyzer] Camera stopped.", file=sys.stderr)

    def capture_frame(self):
        """
        捕获当前摄像头画面
        :return: OpenCV 格式的图像帧 (BGR) 或 None
        """
        if not self.cap or not self.cap.isOpened():
            return None
        try:
            ret, frame = self.cap.read()
            if not ret:
                print("[CameraAnalyzer] Failed to grab frame", file=sys.stderr)
                return None
            return frame
        except Exception as e:
            print(f"[CameraAnalyzer] Frame capture failed: {e}", file=sys.stderr)
            return None

    def analyze_frame(self, frame):
        """
        对图像帧进行分析
        
        当前实现：
        1. 计算平均亮度。
        2. 使用 Canny 算法检测边缘，评估画面复杂度。
        
        :param frame: OpenCV 图像帧 或 None
        :return: 包含分析结果的字典
        """
        if frame is None or not CV2_AVAILABLE:
            return {
                "resolution": (0, 0),
                "average_brightness": 0,
                "edge_density": 0.0,
                "is_complex_scene": False
            }

        try:
            # 1. 转换为灰度图，减少计算量
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # 2. 边缘检测 (Canny)
            edges = cv2.Canny(gray, 100, 200)

            # 3. 简单的亮度分析 (0-255)
            avg_brightness = np.mean(gray)
            
            # 4. 画面变化率/复杂度分析（边缘像素占比）
            edge_density = np.count_nonzero(edges) / edges.size
            
            analysis_result = {
                "resolution": frame.shape[:2],
                "average_brightness": avg_brightness,
                "edge_density": edge_density,
                "is_complex_scene": edge_density > 0.05 # 简单判定
            }
            
            return analysis_result
        except Exception as e:
            print(f"[CameraAnalyzer] Frame analysis failed: {e}", file=sys.stderr)
            return None

    def detect_content_type(self, current_frame, prev_frame):
        """
        基于画面变化率判断动态程度
        
        :param current_frame: 当前帧
        :param prev_frame: 上一帧
        :return: 判定结果字符串, 变化率数值
        """
        if current_frame is None or prev_frame is None or not CV2_AVAILABLE:
            return "未知", 0.0

        try:
            # 1. 转灰度
            curr_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
            prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

            # 2. 计算差异
            diff = cv2.absdiff(curr_gray, prev_gray)

            # 3. 二值化
            _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

            # 4. 计算比例
            total_pixels = curr_gray.size
            changed_pixels = cv2.countNonZero(thresh)
            change_ratio = changed_pixels / total_pixels

            # 5. 判定
            if change_ratio > 0.10: # 摄像头画面通常噪点更多，阈值稍微调高
                return "高动态", change_ratio
            elif change_ratio > 0.02:
                return "中动态", change_ratio
            else:
                return "静止", change_ratio
        except Exception as e:
            print(f"[CameraAnalyzer] Content detection failed: {e}", file=sys.stderr)
            return "未知", 0.0

class ScreenAnalyzer:
    """
    屏幕分析类：使用 mss 进行快速截屏并计算画面变化率。
    """
    def __init__(self):
        self.sct = None
        if MSS_AVAILABLE:
            self.sct = mss()
        self.last_frame = None

    def get_change_rate(self, monitor_id=1):
        """
        获取屏幕变化率 (0.0 - 1.0)
        """
        if not self.sct or not CV2_AVAILABLE:
            return 0.0

        try:
            # 1. 用mss截屏
            if monitor_id > len(self.sct.monitors) - 1:
                monitor_id = 1 # Fallback to primary monitor
            
            monitor = self.sct.monitors[monitor_id]
            screenshot = self.sct.grab(monitor)
            
            # 2. 转为numpy数组
            img = np.array(screenshot)
            
            # 3. 压缩到1/4分辨率（提速）
            h, w = img.shape[:2]
            img = cv2.resize(img, (w//2, h//2))
            
            # 4. 转灰度
            gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
            
            # 5. 首次运行
            if self.last_frame is None:
                self.last_frame = gray
                return 0.0
            
            # 6. 计算帧差
            diff = cv2.absdiff(self.last_frame, gray)
            
            # 7. 平均差异比率 (0.0 - 1.0)
            change_rate = np.mean(diff) / 255
            
            self.last_frame = gray
            
            return change_rate
        except Exception as e:
            print(f"[ScreenAnalyzer] Error: {e}", file=sys.stderr)
            return 0.0

# ========== 便于外部调用的封装函数 ==========

def gather_sample(
    analyzer: CameraAnalyzer,
    prev_frame,
) -> Tuple[Dict, object]:
    """采集一次摄像头数据，返回 (payload, current_frame)."""
    
    frame = analyzer.capture_frame()
    analysis_stats = analyzer.analyze_frame(frame)
    content_type, change_val = analyzer.detect_content_type(frame, prev_frame)

    payload = {
        "screen_change_rate": change_val, # 这里语义变了，变成了camera_change_rate
        "content_type": content_type,
        "is_complex_scene": bool(analysis_stats.get("is_complex_scene", False)) if analysis_stats else False,
        "average_brightness": analysis_stats.get("average_brightness") if analysis_stats else None,
        "edge_density": analysis_stats.get("edge_density") if analysis_stats else None,
        "source": "camera"
    }

    return payload, frame

def stream_monitoring(
    interval: float,
    on_sample: Callable[[Dict], None],
    stop_event: Optional[threading.Event] = None,
    camera_id: int = 0
):
    """持续采样摄像头数据，并将 payload 交给回调 on_sample。"""
    analyzer = CameraAnalyzer(camera_id)
    if not analyzer.start():
        print("[ERROR] Failed to start camera monitoring.", file=sys.stderr)
        return

    prev_frame = None

    try:
        while True:
            if stop_event and stop_event.is_set():
                break
            payload, prev_frame = gather_sample(analyzer, prev_frame)
            on_sample(payload)
            time.sleep(interval)
    finally:
        analyzer.stop()
