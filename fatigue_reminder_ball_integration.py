# -*- coding: utf-8 -*-
"""
疲惫提醒浮球集成示例

这个示例展示了如何在应用中集成 FatigueReminderBall 浮球模块
"""

from PySide6 import QtWidgets, QtCore
from ui.component.float_ball import FatigueReminderBall
from ui.component.fatigue_reminder_dialog import FatigueReminderDialog


class FatigueReminderSystem:
    """疲惫提醒系统集成器"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        
        # 创建浮球实例
        self.ball = FatigueReminderBall(size=64)
        self.ball.show()
        
        # 连接信号
        self._connect_signals()
        
        # 安装事件过滤器用于全局键盘/鼠标监听
        self._install_event_filters()
    
    def _connect_signals(self):
        """连接所有信号"""
        # 连接疲惫提醒信号
        self.ball.fatigue_reminder_triggered.connect(self.on_fatigue_reminder)
        
        # 连接浮球点击信号
        self.ball.touched.connect(self.on_ball_clicked)
        
        # 连接鼠标进入/离开信号
        self.ball.entered.connect(self.on_ball_entered)
        self.ball.left.connect(self.on_ball_left)
    
    def _install_event_filters(self):
        """安装全局事件过滤器"""
        # 为主窗口安装事件过滤器
        event_filter = ActivityEventFilter(self.ball)
        self.main_window.installEventFilter(event_filter)
    
    def on_fatigue_reminder(self, reminder_data):
        """处理疲惫提醒"""
        work_duration = reminder_data['work_duration_formatted']
        
        # 显示提醒对话框
        dialog = FatigueReminderDialog(
            work_duration=work_duration,
            fatigue_reminder=None
        )
        
        result = dialog.exec()
        
        if result == QtWidgets.QDialog.Accepted:
            # 用户点击了"休息"按钮
            self.ball.reset_work_session()
    
    def on_ball_clicked(self):
        """当浮球被点击时"""
        # 显示工作时长信息
        duration = self.ball.get_work_duration_formatted()
        print(f"当前工作时长: {duration}")
    
    def on_ball_entered(self):
        """当鼠标进入浮球时"""
        print("鼠标进入浮球")
    
    def on_ball_left(self):
        """当鼠标离开浮球时"""
        print("鼠标离开浮球")
    
    def get_work_status(self):
        """获取当前工作状态"""
        return {
            'is_working': self.ball.is_working,
            'work_duration': self.ball.get_work_duration(),
            'work_duration_formatted': self.ball.get_work_duration_formatted(),
            'current_state': self.ball.current_state
        }


class ActivityEventFilter(QtCore.QObject):
    """活动事件过滤器 - 监听键盘和鼠标事件"""
    
    def __init__(self, fatigue_ball):
        super().__init__()
        self.fatigue_ball = fatigue_ball
    
    def eventFilter(self, obj, event):
        """事件过滤"""
        # 监听键盘按下事件
        if event.type() == QtCore.QEvent.KeyPress:
            self.fatigue_ball.mark_activity(activity_type="keypress")
        
        # 监听鼠标点击事件
        elif event.type() == QtCore.QEvent.MouseButtonPress:
            self.fatigue_ball.mark_activity(activity_type="click")
        
        # 监听鼠标移动事件（可选，用于更精细的活动追踪）
        elif event.type() == QtCore.QEvent.MouseMove:
            # 可能会产生过多事件，使用节流
            pass
        
        return super().eventFilter(obj, event)


# 使用示例
if __name__ == '__main__':
    import sys
    
    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()
    main_window.setWindowTitle("疲惫提醒系统示例")
    main_window.setGeometry(100, 100, 800, 600)
    
    # 初始化疲惫提醒系统
    reminder_system = FatigueReminderSystem(main_window)
    
    # 显示主窗口
    main_window.show()
    
    sys.exit(app.exec())
