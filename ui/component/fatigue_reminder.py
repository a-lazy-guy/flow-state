# -*- coding: utf-8 -*-
"""疲惫提醒系统 - 管理连续工作时间并触发提醒"""

import time
from typing import Optional, Callable

try:
    from PySide6 import QtCore
    Signal = QtCore.Signal
except ImportError:
    from PyQt5 import QtCore
    Signal = QtCore.pyqtSignal


class FatigueReminder(QtCore.QObject):
    """疲惫提醒系统
    
    功能：
    - 追踪连续工作时间
    - 5小时后触发疲惫提醒
    - 支持暂停/恢复计时
    - 提醒间隔控制（防止频繁提醒）
    """
    
    # 信号定义
    fatigue_reminder_triggered = Signal(dict)  # 发送包含工作时长的提醒数据
    work_started = Signal()  # 工作开始
    work_paused = Signal()  # 工作暂停
    work_resumed = Signal()  # 工作恢复
    
    # 常量定义
    FATIGUE_THRESHOLD = 5 * 3600  # 5小时（秒）
    REMINDER_INTERVAL = 3600  # 提醒间隔1小时
    IDLE_THRESHOLD = 300  # 闲置5分钟判定为工作结束
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 工作时间追踪
        self.work_session_start = None  # 当前工作会话开始时间
        self.work_session_paused_at = None  # 暂停时间
        self.cumulative_work_time = 0  # 累计工作时间（秒）
        self.is_working = False  # 是否正在工作
        
        # 提醒控制
        self.last_reminder_time = 0  # 上次提醒时间
        self.reminder_disabled = False  # 提醒是否被禁用
        self.snooze_until_time = 0  # 延后提醒的截止时间
        
        # 是否已提醒的标志
        self.has_reminded_at_5h = False  # 5小时是否已提醒
        self.has_reminded_at_6h = False  # 6小时是否已提醒
        self.has_reminded_at_7h = False  # 7小时是否已提醒
        
        # 最后活动时间
        self.last_activity_time = None
        
    def mark_activity(self):
        """标记活动（由键盘/鼠标输入调用）"""
        current_time = time.time()
        
        # 如果没有工作会话，创建新的
        if not self.is_working:
            self._start_work_session(current_time)
        # 如果处于暂停状态，恢复工作
        elif self.work_session_paused_at is not None:
            self._resume_work_session(current_time)
        
        self.last_activity_time = current_time
    
    def _start_work_session(self, current_time):
        """启动工作会话"""
        self.work_session_start = current_time
        self.work_session_paused_at = None
        self.is_working = True
        self.cumulative_work_time = 0
        
        # 重置提醒标志
        self.has_reminded_at_5h = False
        self.has_reminded_at_6h = False
        self.has_reminded_at_7h = False
        self.last_reminder_time = 0
        
        self.work_started.emit()
    
    def _pause_work_session(self, current_time):
        """暂停工作会话"""
        if self.work_session_start is not None and self.work_session_paused_at is None:
            work_duration = current_time - self.work_session_start
            self.cumulative_work_time += work_duration
            self.work_session_paused_at = current_time
            self.work_paused.emit()
    
    def _resume_work_session(self, current_time):
        """恢复工作会话"""
        if self.work_session_paused_at is not None:
            self.work_session_start = current_time
            self.work_session_paused_at = None
            self.work_resumed.emit()
    
    def check_idle_and_update(self):
        """检查是否闲置，更新工作状态"""
        if not self.is_working or self.last_activity_time is None:
            return
        
        current_time = time.time()
        idle_time = current_time - self.last_activity_time
        
        # 如果闲置超过阈值，暂停工作计时
        if idle_time > self.IDLE_THRESHOLD and self.work_session_paused_at is None:
            self._pause_work_session(current_time)
    
    def get_work_duration(self) -> int:
        """获取当前工作时长（秒）"""
        if not self.is_working:
            return self.cumulative_work_time
        
        if self.work_session_start is None:
            return self.cumulative_work_time
        
        current_time = time.time()
        current_session_duration = current_time - self.work_session_start
        
        return self.cumulative_work_time + current_session_duration
    
    def get_work_duration_formatted(self) -> str:
        """获取格式化的工作时长"""
        duration_seconds = self.get_work_duration()
        hours = duration_seconds // 3600
        minutes = (duration_seconds % 3600) // 60
        
        return f"{int(hours)}小时{int(minutes)}分钟"
    
    def check_fatigue_reminder(self) -> Optional[dict]:
        """检查是否需要触发疲惫提醒
        
        Returns:
            提醒数据字典或None
        """
        if not self.is_working or self.reminder_disabled:
            return None
        
        current_time = time.time()
        
        # 检查延后提醒
        if current_time < self.snooze_until_time:
            return None
        
        work_duration = self.get_work_duration()
        
        # 5小时提醒
        if work_duration >= self.FATIGUE_THRESHOLD and not self.has_reminded_at_5h:
            if current_time - self.last_reminder_time >= self.REMINDER_INTERVAL:
                self.has_reminded_at_5h = True
                self.last_reminder_time = current_time
                return self._create_reminder_data(work_duration, '5小时')
        
        # 6小时提醒
        elif work_duration >= self.FATIGUE_THRESHOLD + 3600 and not self.has_reminded_at_6h:
            if current_time - self.last_reminder_time >= self.REMINDER_INTERVAL:
                self.has_reminded_at_6h = True
                self.last_reminder_time = current_time
                return self._create_reminder_data(work_duration, '6小时')
        
        # 7小时提醒
        elif work_duration >= self.FATIGUE_THRESHOLD + 7200 and not self.has_reminded_at_7h:
            if current_time - self.last_reminder_time >= self.REMINDER_INTERVAL:
                self.has_reminded_at_7h = True
                self.last_reminder_time = current_time
                return self._create_reminder_data(work_duration, '7小时')
        
        return None
    
    def _create_reminder_data(self, duration: int, milestone: str) -> dict:
        """创建提醒数据"""
        hours = duration // 3600
        minutes = (duration % 3600) // 60
        
        return {
            'duration': duration,
            'duration_formatted': f"{hours}小时{minutes}分钟",
            'milestone': milestone,
            'suggestions': self._get_rest_suggestions()
        }
    
    def _get_rest_suggestions(self) -> list:
        """获取休息建议列表"""
        return [
            {
                'title': '散步',
                'description': '到户外走一走，呼吸新鲜空气，放松身心',
                'duration': '10-15分钟',
                'icon': '🚶'
            },
            {
                'title': '小睡',
                'description': '舒服地躺着闭眼休息，让大脑得到充分恢复',
                'duration': '15-20分钟',
                'icon': '😴'
            },
            {
                'title': '伸展运动',
                'description': '做简单的颈部、肩部和腰部拉伸，缓解肌肉疲劳',
                'duration': '5-10分钟',
                'icon': '🧘'
            },
            {
                'title': '眼部放松',
                'description': '看看远处，眨眨眼睛，做眼睛保健操',
                'duration': '3-5分钟',
                'icon': '👀'
            },
            {
                'title': '营养补充',
                'description': '喝杯水或吃点水果，补充体力和水分',
                'duration': '5分钟',
                'icon': '🥤'
            },
            {
                'title': '冥想静坐',
                'description': '找个安静的地方，深呼吸冥想，平复心绪',
                'duration': '5-10分钟',
                'icon': '🧖'
            }
        ]
    
    def snooze_reminder(self, minutes: int = 30):
        """延后提醒
        
        Args:
            minutes: 延后分钟数
        """
        self.snooze_until_time = time.time() + (minutes * 60)
    
    def dismiss_reminder(self):
        """关闭提醒并继续工作"""
        # 提醒已处理，继续工作
        pass
    
    def end_work_session(self):
        """结束工作会话"""
        if self.is_working:
            if self.work_session_paused_at is None and self.work_session_start is not None:
                current_time = time.time()
                self._pause_work_session(current_time)
            
            self.is_working = False
            
            # 重置所有状态
            self.work_session_start = None
            self.work_session_paused_at = None
            self.cumulative_work_time = 0
            self.last_activity_time = None
            self.has_reminded_at_5h = False
            self.has_reminded_at_6h = False
            self.has_reminded_at_7h = False
            self.last_reminder_time = 0
            self.snooze_until_time = 0
    
    def reset_session(self):
        """重置当前会话"""
        self.end_work_session()
        self.reminder_disabled = False
