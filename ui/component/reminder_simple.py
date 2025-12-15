from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6 import QtCore as QtCore  # type: ignore
    from PySide6 import QtGui as QtGui  # type: ignore
    from PySide6 import QtWidgets as QtWidgets  # type: ignore
else:
    try:
        from PySide6 import QtCore, QtGui, QtWidgets  # type: ignore
        QT_LIB = "PySide6"
    except ImportError:
        from PyQt5 import QtCore, QtGui, QtWidgets  # type: ignore
        QT_LIB = "PyQt5"

def qt_const(name: str) -> Any:
    qt = getattr(QtCore, "Qt", None)
    if qt is None:
        return None
    val = getattr(qt, name, None)
    if val is not None:
        return val
    for enum_name in ("WindowType", "WidgetAttribute", "CursorShape", "AlignmentFlag"):
        enum = getattr(qt, enum_name, None)
        if enum is not None:
            sub = getattr(enum, name, None)
            if sub is not None:
                return sub
    return None


class ReminderOverlay(QtWidgets.QDialog):
    """简单娱乐提醒界面 - 仅显示消息和三个操作按钮"""
    
    if hasattr(QtCore, 'Signal'):
        Signal = QtCore.Signal
    else:
        Signal = QtCore.pyqtSignal
        
    work_clicked = Signal()
    snooze_clicked = Signal()
    disable_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(False)
        self.setWindowFlags(
            qt_const("FramelessWindowHint")
            | qt_const("WindowStaysOnTopHint")
        )
        
        self._is_closing = False
        
        wa_translucent = qt_const("WA_TranslucentBackground")
        if wa_translucent is not None:
            self.setAttribute(wa_translucent)
        wa_no_activate = qt_const("WA_ShowWithoutActivating")
        if wa_no_activate is not None:
            self.setAttribute(wa_no_activate)
        
        # 获取屏幕尺寸
        app = QtWidgets.QApplication.instance()
        screen: Optional[Any] = None
        if app is not None:
            primary = getattr(app, "primaryScreen", None)
            if callable(primary):
                screen = primary()
            else:
                pass
        if screen is None:
            desktop = getattr(QtWidgets.QApplication, "desktop", None)
            screen = desktop() if callable(desktop) else None
        
        # 获取有效屏幕几何尺寸
        if screen is not None:
            geometry = screen.availableGeometry()
        else:
            geometry = QtCore.QRect(0, 0, 800, 600)
        
        # 设置窗口尺寸（更大、更舒适的提醒窗口）
        window_width = 800
        window_height = 600
        center_x = geometry.left() + (geometry.width() - window_width) // 2
        center_y = geometry.top() + (geometry.height() - window_height) // 2
        self.setGeometry(center_x, center_y, window_width, window_height)
        
        # 主容器 - 使用疲劳提醒的白色主题
        self.container = QtWidgets.QWidget(self)
        self.container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 20px;
                border: none;
            }
        """)
        
        # 主布局
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(qt_const("AlignCenter"))
        main_layout.addWidget(self.container)
        
        # 容器内布局 - 增加内边距和间距
        layout = QtWidgets.QVBoxLayout(self.container)
        layout.setContentsMargins(80, 60, 80, 60)
        layout.setSpacing(20)
        
        # 消息区域包装 - 仿照疲劳提醒的头部样式
        msg_frame = QtWidgets.QFrame()
        msg_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(248, 249, 250, 200);
                border-radius: 20px;
                border: 1px solid rgba(0, 0, 0, 0.03);
            }
            QFrame:hover {
                background-color: rgba(240, 242, 245, 220);
                border: 1px solid rgba(0, 0, 0, 0.08);
            }
        """)
        msg_layout = QtWidgets.QVBoxLayout(msg_frame)
        msg_layout.setContentsMargins(20, 20, 20, 20)
        
        # 主消息 - 深色文字
        self.main_message = QtWidgets.QLabel("该休息一下了")
        self.main_message.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 48px;
                font-weight: bold;
                letter-spacing: 2px;
                background: transparent;
                border: none;
            }
        """)
        self.main_message.setAlignment(qt_const("AlignCenter"))
        self.main_message.setWordWrap(True)
        self.main_message.setMinimumHeight(80)
        msg_layout.addWidget(self.main_message)
        layout.addWidget(msg_frame)
        
        # 鼓励语句 - 单独的浅灰色方框
        enc_frame = QtWidgets.QFrame()
        enc_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(248, 249, 250, 200);
                border-radius: 12px;
                border: 1px solid rgba(0, 0, 0, 0.03);
            }
        """)
        enc_layout = QtWidgets.QVBoxLayout(enc_frame)
        enc_layout.setContentsMargins(20, 15, 20, 15)

        self.encouragement = QtWidgets.QLabel("💪 坚持就是胜利，休息是为了走得更远")
        self.encouragement.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 18px;
                font-weight: bold;
                background: transparent;
                border: none;
            }
        """)
        self.encouragement.setAlignment(qt_const("AlignCenter"))
        self.encouragement.setWordWrap(True)
        enc_layout.addWidget(self.encouragement)
        layout.addWidget(enc_frame)
        
        # 添加伸缩空间
        layout.addStretch()
        
        # 操作按钮栏 - 更柔和的按钮样式
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(20)
        button_layout.setAlignment(qt_const("AlignCenter"))
        
        # 按钮1：继续工作 - 温暖的黄色
        work_button = QtWidgets.QPushButton("继续工作 💪")
        work_button.setMinimumHeight(60)
        work_button.setMinimumWidth(180)
        work_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fbbf24, stop:1 #f59e0b);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 14px 28px;
                font-size: 16px;
                font-weight: bold;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fcd34d, stop:1 #fbbf24);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f59e0b, stop:1 #d97706);
            }
        """)
        work_button.clicked.connect(self.on_work_button)
        button_layout.addWidget(work_button)
        
        # 按钮2：再休息5分钟 - 柔和的蓝色
        snooze_button = QtWidgets.QPushButton("再休息5分钟 ☕")
        snooze_button.setMinimumHeight(60)
        snooze_button.setMinimumWidth(180)
        snooze_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #60a5fa, stop:1 #3b82f6);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 14px 28px;
                font-size: 16px;
                font-weight: bold;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #93c5fd, stop:1 #60a5fa);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3b82f6, stop:1 #1d4ed8);
            }
        """)
        snooze_button.clicked.connect(self.on_snooze_button)
        button_layout.addWidget(snooze_button)
        
        # 按钮3：禁用提醒 - 柔和的灰色
        disable_button = QtWidgets.QPushButton("暂时禁用 ✕")
        disable_button.setMinimumHeight(60)
        disable_button.setMinimumWidth(180)
        disable_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #d1d5db, stop:1 #9ca3af);
                color: #374151;
                border: none;
                border-radius: 12px;
                padding: 14px 28px;
                font-size: 16px;
                font-weight: bold;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e5e7eb, stop:1 #d1d5db);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #9ca3af, stop:1 #6b7280);
            }
        """)
        disable_button.clicked.connect(self.on_disable_button)
        button_layout.addWidget(disable_button)
        
        layout.addLayout(button_layout)
        
        # 点击关闭
        self.setCursor(qt_const("PointingHandCursor"))
        
        # 动画效果
        self.fade_animation = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(400)

    def mousePressEvent(self, event):
        """点击关闭"""
        self.close_reminder()
    
    def keyPressEvent(self, event):
        """Esc 键关闭"""
        if event.key() == QtCore.Qt.Key_Escape:
            self.close_reminder()
        else:
            super().keyPressEvent(event)
    
    def hideEvent(self, event):
        """隐藏事件处理"""
        # 允许窗口正常隐藏，无需额外处理
        super().hideEvent(event)
    
    def on_work_button(self):
        """用户点击'回去工作'按钮"""
        # 显示激励语
        self.main_message.setText("太棒了！🎯")
        self.encouragement.setText("你做的很对，专注才能成就梦想！\n加油，我看好你！💪")
        self.work_clicked.emit()
        # 延迟关闭，让用户看到激励语
        QtCore.QTimer.singleShot(1500, self.close_reminder)
    
    def on_snooze_button(self):
        """用户点击'再休息5分钟'按钮"""
        # 显示激励语
        self.main_message.setText("好的，休息一下～ ☕")
        self.encouragement.setText("放松心情，5分钟后我们继续加油！\n你的坚持会有回报的！✨")
        self.snooze_clicked.emit()
        # 延迟关闭，让用户看到激励语
        QtCore.QTimer.singleShot(1500, self.close_reminder)
    
    def on_disable_button(self):
        """用户点击'禁用提醒'按钮"""
        # 显示激励语
        self.main_message.setText("理解你～")
        self.encouragement.setText("希望你能自觉安排时间。\n记住，自律是通往成功的钥匙！🔑")
        self.disable_clicked.emit()
        # 延迟关闭，让用户看到激励语
        QtCore.QTimer.singleShot(1500, self.close_reminder)
    
    def close_reminder(self):
        """关闭提醒"""
        self._is_closing = True
        self.fade_out_and_close()
    
    def fade_out_and_close(self):
        """淡出动画"""
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        # 断开所有之前的连接，避免重复触发
        try:
            self.fade_animation.finished.disconnect()
        except (RuntimeError, TypeError):
            pass
        # 淡出完后关闭窗口
        self.fade_animation.finished.connect(lambda: self.close())
        self.fade_animation.start()
    
    def show_reminder(self, data: dict):
        """显示智能提醒"""
        # 根据严重级别自定义消息
        severity = data.get('severity', 'low')
        duration = data.get('duration', 0)  # 持续时间（秒），需要转换为分钟
        # 确保至少显示 1 分钟，避免出现 "0 分钟"
        minutes = max(1, int(duration / 60)) if duration else 22
        
        # 温暖友好的提醒消息
        if severity == 'low':
            message = f"你已经看了 {minutes} 分钟视频啦～\n是不是被剧情吸引住了？没关系，\n要不要试试换件事做？✨"
            encouragement = "💪 休息一下，然后继续加油！"
        elif severity == 'medium':
            message = f"你已经娱乐 {minutes} 分钟了呢～\n时间过得可真快！\n不过是时候回到工作上了吧？😊"
            encouragement = "🎯 坚持一下，好事儿在后头！"
        else:  # high
            message = f"哇，{minutes} 分钟了！\n你真的很投入呢～\n但现在真的该认真工作了哦！"
            encouragement = "✨ 冲冲冲，你可以的！"
        
        self.main_message.setText(message)
        self.encouragement.setText(encouragement)
        
        # 显示窗口
        self.setWindowOpacity(1.0)
        self.show()
        self.raise_()
        self.activateWindow()
