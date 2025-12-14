# -*- coding: utf-8 -*-
"""疲惫提醒浮球模块 - 悬浮窗口显示工作状态和疲惫提醒"""

import sys
import time
from typing import Optional, Callable

try:
    from PySide6 import QtCore, QtGui, QtWidgets
    Signal = QtCore.Signal
    QT = "PySide6"
except ImportError:
    from PyQt5 import QtCore, QtGui, QtWidgets
    Signal = QtCore.pyqtSignal
    QT = "PyQt5"


class FatigueReminderBall(QtWidgets.QWidget):
    """疲惫提醒浮球
    
    功能：
    - 显示工作状态的视觉反馈（颜色变化）
    - 呼吸灯效果表示活跃状态
    - 点击触发疲惫提醒对话框
    - 支持拖动重新定位
    """
    
    # 信号定义
    touched = Signal()
    entered = Signal()
    positionChanged = Signal(QtCore.QPoint)
    left = Signal()
    fatigue_reminder_triggered = Signal(dict)  # 疲惫提醒信号
    
    # 状态常量
    STATE_IDLE = "idle"        # 闲置
    STATE_WORKING = "working"  # 工作中
    STATE_FATIGUED = "fatigued"  # 疲惫
    STATE_EXHAUSTED = "exhausted"  # 极度疲惫
    
    def __init__(self, size=64):
        super().__init__()
        
        # 窗口属性
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.Tool
            | QtCore.Qt.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setFixedSize(size, size)
        
        # 工作时间追踪
        self.work_session_start = None
        self.work_session_paused_at = None
        self.cumulative_work_time = 0.0
        self.is_working = False
        self.last_activity_time = None
        
        # 疲惫提醒配置（基于疲惫检测）
        self.fatigue_threshold = 5 * 3600  # 5小时后开始检测
        self.last_reminder_time = 0
        self.reminder_interval = 3600  # 提醒间隔1小时
        self.idle_threshold = 300  # 5分钟闲置判定为暂停
        
        # 状态管理
        self.current_state = self.STATE_IDLE
        self.current_work_duration = 0.0
        
        # 颜色配置
        self.colors = {
            self.STATE_IDLE: (QtGui.QColor(0, 100, 200), QtGui.QColor(0, 150, 255)),      # 蓝色
            self.STATE_WORKING: (QtGui.QColor(0, 200, 0), QtGui.QColor(0, 255, 0)),       # 绿色
            self.STATE_FATIGUED: (QtGui.QColor(255, 165, 0), QtGui.QColor(255, 200, 0)),  # 橙色
            self.STATE_EXHAUSTED: (QtGui.QColor(255, 0, 0), QtGui.QColor(255, 100, 100))  # 红色
        }
        
        self.color_a, self.color_b = self.colors[self.STATE_IDLE]
        self.border_width = 2
        self.border_alpha = 180
        self.border_color = QtGui.QColor(0, 0, 0, self.border_alpha)
        self.drag_offset = None
        
        # 呼吸灯相关属性
        self.breath_value = 0.0
        self.breath_direction = 1
        
        # 定时器
        self.breath_timer = QtCore.QTimer(self)
        self.breath_timer.timeout.connect(self.updateBreath)
        self.breath_timer.start(50)
        
        self.activity_check_timer = QtCore.QTimer(self)
        self.activity_check_timer.timeout.connect(self.checkIdleAndUpdate)
        self.activity_check_timer.start(1000)  # 每秒检查一次
        
        self.updateMask()
        self.moveToBottomRight()
    
    def mark_activity(self, activity_type: str = "input"):
        """标记用户活动（键盘或鼠标输入）"""
        current_time = time.time()
        
        # 如果没有工作会话，创建新的
        if not self.is_working:
            self._start_work_session(current_time)
        # 如果处于暂停状态，恢复工作
        elif self.work_session_paused_at is not None:
            self._resume_work_session(current_time)
        
        self.last_activity_time = current_time
        self._update_state()
    
    def _start_work_session(self, current_time):
        """启动工作会话"""
        self.work_session_start = current_time
        self.work_session_paused_at = None
        self.is_working = True
        self.cumulative_work_time = 0.0
        self.last_reminder_time = 0
    
    def _pause_work_session(self, current_time):
        """暂停工作会话"""
        if self.work_session_start is not None and self.work_session_paused_at is None:
            work_duration = current_time - self.work_session_start
            self.cumulative_work_time += work_duration
            self.work_session_paused_at = current_time
    
    def _resume_work_session(self, current_time):
        """恢复工作会话"""
        if self.work_session_paused_at is not None:
            self.work_session_start = current_time
            self.work_session_paused_at = None
    
    def checkIdleAndUpdate(self):
        """检查是否闲置，更新工作状态"""
        if not self.is_working or self.last_activity_time is None:
            return
        
        current_time = time.time()
        idle_time = current_time - self.last_activity_time
        
        # 如果闲置超过阈值，暂停工作计时
        if idle_time > self.idle_threshold and self.work_session_paused_at is None:
            self._pause_work_session(current_time)
        
        self._update_state()
    
    def get_work_duration(self) -> float:
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
        hours = int(duration_seconds // 3600)
        minutes = int((duration_seconds % 3600) // 60)
        
        return f"{hours}小时{minutes}分钟"
    
    def check_fatigue_reminder(self) -> Optional[dict]:
        """检查是否需要触发疲惫提醒（基于疲惫检测）"""
        if not self.is_working:
            return None
        
        current_time = time.time()
        work_duration = self.get_work_duration()
        
        # 只有在超过疲惫阈值且距离上次提醒已过提醒间隔才触发
        # 实际的疲惫检测应该在其他地方进行（如fatigue_detector）
        if work_duration >= self.fatigue_threshold:
            if current_time - self.last_reminder_time >= self.reminder_interval:
                self.last_reminder_time = current_time
                return {
                    'work_duration': work_duration,
                    'work_duration_formatted': self.get_work_duration_formatted(),
                    'timestamp': current_time,
                    'type': 'fatigue'
                }
        
        return None
    
    def _update_state(self):
        """更新当前状态并触发提醒"""
        work_duration = self.get_work_duration()
        self.current_work_duration = work_duration
        
        # 根据工作时长确定状态
        if not self.is_working:
            new_state = self.STATE_IDLE
        elif work_duration >= 7 * 3600:  # 7小时以上
            new_state = self.STATE_EXHAUSTED
        elif work_duration >= 5 * 3600:  # 5小时以上
            new_state = self.STATE_FATIGUED
        else:  # 少于5小时
            new_state = self.STATE_WORKING
        
        # 状态变化时更新颜色
        if new_state != self.current_state:
            self.current_state = new_state
            self.color_b, self.color_a = self.colors[new_state]
            self.update()
        
        # 检查是否需要提醒
        reminder = self.check_fatigue_reminder()
        if reminder:
            self.fatigue_reminder_triggered.emit(reminder)
    
    def reset_work_session(self):
        """重置工作会话"""
        self.work_session_start = None
        self.work_session_paused_at = None
        self.cumulative_work_time = 0.0
        self.is_working = False
        self.last_activity_time = None
        self.current_work_duration = 0.0
        self.current_state = self.STATE_IDLE
        self.last_reminder_time = 0
        self.color_b, self.color_a = self.colors[self.STATE_IDLE]
        self.update()

    def updateBreath(self):
        """
        更新呼吸灯状态。
        """
        step = 0.05
        self.breath_value += step * self.breath_direction
        
        # 边界检查与反转方向
        if self.breath_value >= 1.0:
            self.breath_value = 1.0
            self.breath_direction = -1
        elif self.breath_value <= 0.0:
            self.breath_value = 0.0
            self.breath_direction = 1
            
        self.update()  # 触发重绘

    def updateMask(self):
        r = QtCore.QRect(0, 0, self.width(), self.height())
        self.setMask(QtGui.QRegion(r, QtGui.QRegion.Ellipse))

    def moveToBottomRight(self):
        screen = QtGui.QGuiApplication.primaryScreen()
        geo = screen.availableGeometry()
        m = 20
        x = geo.right() - self.width() - m
        y = geo.bottom() - self.height() - m
        self.move(x, y)

    def enterEvent(self, event):
        """鼠标进入事件"""
        self.border_alpha = 0
        self.border_color.setAlpha(self.border_alpha)
        self.update()
        self.entered.emit()

    def leaveEvent(self, event):
        """鼠标离开事件"""
        self.border_alpha = 180
        self.border_color.setAlpha(self.border_alpha)
        self.update()
        self.left.emit()

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_offset = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            self.touched.emit()

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if event.buttons() & QtCore.Qt.LeftButton and self.drag_offset is not None:
            self.move(event.globalPos() - self.drag_offset)
            self.positionChanged.emit(self.pos())
            event.accept()

    def moveEvent(self, event):
        """窗口移动事件"""
        try:
            self.positionChanged.emit(self.pos())
        finally:
            super().moveEvent(event)

    def resizeEvent(self, event):
        self.updateMask()
        super().resizeEvent(event)

    def paintEvent(self, event):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing, True)
        rect = QtCore.QRectF(0, 0, self.width(), self.height())
        r = min(self.width(), self.height()) / 2.0
        cx = rect.center().x()
        cy = rect.center().y()
        p.setPen(QtCore.Qt.NoPen)
        
        # 绘制主体的渐变背景
        # 使用线性渐变，从上(0,0)到下(0, height)
        grad = QtGui.QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0.0, self.color_b)  # 顶部颜色
        grad.setColorAt(1.0, self.color_a)  # 底部颜色
        p.setBrush(QtGui.QBrush(grad))
        p.drawEllipse(rect)
        
        # 绘制呼吸灯光晕效果（确保在最上层绘制）
        # 计算光晕颜色：使用白色，根据 breath_value 调整透明度
        glow_color = QtGui.QColor(255, 255, 255)  # 纯白色光晕
        min_alpha = 30   # 最小透明度
        max_alpha = 180  # 最大透明度
        current_alpha = int(min_alpha + (max_alpha - min_alpha) * self.breath_value)
        glow_color.setAlpha(current_alpha)
        
        # 光晕渐变：外圈亮，向内透明
        glow_grad = QtGui.QRadialGradient(QtCore.QPointF(cx, cy), r)
        glow_grad.setColorAt(0.85, QtGui.QColor(255, 255, 255, 0))  # 内部完全透明
        glow_grad.setColorAt(0.95, glow_color)                      # 边缘发光
        glow_grad.setColorAt(1.0, QtGui.QColor(255, 255, 255, 0))   # 最外层渐隐
        
        p.setBrush(QtGui.QBrush(glow_grad))
        p.drawEllipse(rect)


# 向后兼容：保留旧的类名别名
TaijiBall = FatigueReminderBall
