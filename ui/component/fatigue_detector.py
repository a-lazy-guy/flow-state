# -*- coding: utf-8 -*-
"""疲劳检测器"""

import time

class FatigueDetector:
    """疲劳检测器"""
    
    def __init__(self):
        self.keypress_times = []
        self.mouse_times = []
        self.work_start_time = None
    
    def record_keypress(self):
        """记录键盘输入"""
        self.keypress_times.append(time.time())
        # 清除5分钟前的记录
        cutoff = time.time() - 300
        self.keypress_times = [t for t in self.keypress_times if t > cutoff]
    
    def record_mouse_click(self):
        """记录鼠标点击"""
        self.mouse_times.append(time.time())
        # 清除5分钟前的记录
        cutoff = time.time() - 300
        self.mouse_times = [t for t in self.mouse_times if t > cutoff]
    
    def calculate_fatigue_level(self, work_duration: float, input_frequency: float, 
                               pattern_change: float) -> str:
        """计算疲劳等级"""
        # 简化版本：只看工作时长
        if work_duration < 30:
            return 'fresh'  # 精力充沛
        elif work_duration < 60:
            return 'fatigued'  # 有点疲劳
        else:
            return 'exhausted'  # 非常疲劳
