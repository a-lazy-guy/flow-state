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
    """娱乐提醒界面 - 简洁版本"""
    
    work_clicked = QtCore.Signal()
    snooze_clicked = QtCore.Signal()
    disable_clicked = QtCore.Signal()
    activity_selected = QtCore.Signal(str, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(False)
        self.setWindowFlags(
            qt_const("FramelessWindowHint")
            | qt_const("WindowStaysOnTopHint")
        )
        # 设为应用级模态，减少焦点切换导致的隐退
        try:
            self.setWindowModality(qt_const("ApplicationModal"))
        except Exception:
            pass
        
        # 强化窗口保持逻辑 - 已简化
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
                # 无法静态确认 screens 类型时，放弃该分支，使用后续兜底
                pass
        if screen is None:
            desktop = getattr(QtWidgets.QApplication, "desktop", None)
            screen = desktop() if callable(desktop) else None
        
        # 获取有效屏幕几何尺寸
        if screen is not None:
            geometry = screen.availableGeometry()
        else:
            geometry = QtCore.QRect(0, 0, 800, 600)
        
        # 设置窗口尺寸为屏幕可用区域大小，但限制最小值
        width = max(geometry.width(), 400)
        height = max(geometry.height(), 300)
        self.setGeometry(QtCore.QRect(geometry.left(), geometry.top(), width, height))
        
        # 主容器 - 简洁白色背景
        self.container = QtWidgets.QWidget(self)
        self.container.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
        """)
        
        # 主布局
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(qt_const("AlignCenter"))
        main_layout.addWidget(self.container)
        
        # 容器内布局
        layout = QtWidgets.QVBoxLayout(self.container)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        
        # 标题图标和主消息
        title_layout = QtWidgets.QHBoxLayout()
        self.icon_label = QtWidgets.QLabel("ℹ")
        self.icon_label.setStyleSheet("""
            QLabel {
                font-size: 48px;
                color: #333;
                font-weight: bold;
            }
        """)
        title_layout.addWidget(self.icon_label)
        
        self.main_message = QtWidgets.QLabel("休息一下")
        self.main_message.setStyleSheet("""
            QLabel {
                color: #333;
                font-size: 28px;
                font-weight: bold;
            }
        """)
        self.main_message.setAlignment(qt_const("AlignLeft"))
        self.main_message.setWordWrap(True)
        title_layout.addWidget(self.main_message, 1)
        layout.addLayout(title_layout)
        
        # 分割线
        separator1 = QtWidgets.QFrame()
        hline = getattr(QtWidgets.QFrame, "HLine", None)
        if hline is not None:
            separator1.setFrameShape(hline)
        else:
            try:
                separator1.setFrameShape(QtWidgets.QFrame.Shape.HLine)
            except Exception:
                separator1.setFrameShape(4)
        separator1.setStyleSheet("background-color: #eee;")
        separator1.setFixedHeight(1)
        layout.addWidget(separator1)
        
        # 主消息
        self.history_list = QtWidgets.QLabel()
        self.history_list.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 13px;
                line-height: 1.6;
                padding: 8px;
            }
        """)
        self.history_list.setWordWrap(True)
        self.history_list.setAlignment(qt_const("AlignLeft"))
        layout.addWidget(self.history_list)
        
        # 时间进度条
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #f5f5f5;
                color: #333;
                font-size: 12px;
                min-height: 20px;
            }
            QProgressBar::chunk {
                background: #4CAF50;
                border-radius: 3px;
            }
        """)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        layout.addWidget(self.progress_bar)
        
        # 分割线
        separator2 = QtWidgets.QFrame()
        hline2 = getattr(QtWidgets.QFrame, "HLine", None)
        if hline2 is not None:
            separator2.setFrameShape(hline2)
        else:
            try:
                separator2.setFrameShape(QtWidgets.QFrame.Shape.HLine)
            except Exception:
                separator2.setFrameShape(4)
        separator2.setStyleSheet("background-color: #eee;")
        separator2.setFixedHeight(1)
        layout.addWidget(separator2)
        
        # 鼓励语句
        self.encouragement = QtWidgets.QLabel()
        self.encouragement.setStyleSheet("""
            QLabel {
                color: #2196F3;
                font-size: 16px;
                font-weight: bold;
                padding: 12px;
                background-color: #f0f8ff;
                border-radius: 6px;
                border-left: 3px solid #2196F3;
            }
        """)
        self.encouragement.setAlignment(qt_const("AlignCenter"))
        self.encouragement.setWordWrap(True)
        layout.addWidget(self.encouragement)
        
        # 娱乐活动选项（带倒计时）
        activity_layout = QtWidgets.QHBoxLayout()
        activity_layout.setSpacing(8)
        
        # 定义娱乐活动
        self.activities = {
            'walk': {'name': '散步', 'duration': 15, 'color': '#FF6B9D'},
            'nap': {'name': '小睡', 'duration': 30, 'color': '#A29BFE'},
            'stretch': {'name': '拉伸', 'duration': 10, 'color': '#74B9FF'},
            'coffee': {'name': '喝水', 'duration': 15, 'color': '#DDA15E'}
        }
        
        self.activity_buttons = {}
        for key, activity in self.activities.items():
            btn = QtWidgets.QPushButton(f"{activity['name']}\n({activity['duration']}m)")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {activity['color']};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px;
                    font-size: 11px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    opacity: 0.8;
                }}
            """)
            btn.setFixedHeight(60)
            btn.clicked.connect(lambda checked, k=key: self.on_activity_selected(k))
            self.activity_buttons[key] = btn
            activity_layout.addWidget(btn)
        
        layout.addLayout(activity_layout)
        
        # 倒计时标签
        self.countdown_label = QtWidgets.QLabel()
        self.countdown_label.setStyleSheet("""
            QLabel {
                color: #FF6B9D;
                font-size: 32px;
                font-weight: bold;
                padding: 12px;
                text-align: center;
                font-family: 'Courier New', monospace;
            }
        """)
        self.countdown_label.setAlignment(qt_const("AlignCenter"))
        self.countdown_label.setText("")
        layout.addWidget(self.countdown_label)
        
        # 操作按钮栏
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.setAlignment(qt_const("AlignCenter"))
        
        # 按钮1：回去工作
        work_button = QtWidgets.QPushButton("继续工作")
        work_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        work_button.clicked.connect(self.on_work_button)
        button_layout.addWidget(work_button)
        
        # 按钮2：再休息5分钟
        snooze_button = QtWidgets.QPushButton("再休息5分钟")
        snooze_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        snooze_button.clicked.connect(self.on_snooze_button)
        button_layout.addWidget(snooze_button)
        
        # 按钮3：不需要提醒
        disable_button = QtWidgets.QPushButton("禁用提醒")
        disable_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        disable_button.clicked.connect(self.on_disable_button)
        button_layout.addWidget(disable_button)
        
        layout.addLayout(button_layout)
        
        # 不添加阴影效果 - 保持简洁
        
        # 点击关闭
        self.setCursor(qt_const("PointingHandCursor"))
        
        # 动画效果
        self.fade_animation = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(400)

        # 自动关闭配置：仅高级别提醒自动关闭，低/中级保留点击关闭
        self.auto_close_times = {
            'low': 30000,     # 30秒（仅点击关闭）
            'medium': 60000,  # 60秒（仅点击关闭）
            'high': 180000    # 180秒 = 3分钟（高级自动关闭）
        }
        
        # 倒计时相关
        self.countdown_timer = QtCore.QTimer()
        self.countdown_timer.timeout.connect(self._on_countdown_tick)
        self.countdown_seconds = 0

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
        if not self._is_closing:
            event.ignore()  # 保留窗口，但不强制显示
        else:
            super().hideEvent(event)
    
    def _ensure_visible(self):
        """定期检查（已禁用）"""
        pass
    
    def on_work_button(self):
        """用户点击'回去工作'按钮"""
        self.work_clicked.emit()
        self.close_reminder()
    
    def on_snooze_button(self):
        """用户点击'再休息5分钟'按钮"""
        self.snooze_clicked.emit()
        self.close_reminder()
    
    def on_disable_button(self):
        """用户点击'不需要提醒'按钮"""
        self.disable_clicked.emit()
        self.close_reminder()
    
    def on_activity_selected(self, activity_type: str):
        """用户选择娱乐活动"""
        if activity_type in self.activities:
            duration = self.activities[activity_type]['duration']
            self.activity_selected.emit(activity_type, duration)
            self._start_countdown(duration)
    
    def _start_countdown(self, minutes: int):
        """启动倒计时"""
        self.countdown_seconds = minutes * 60
        self.countdown_timer.start(1000)  # 每秒更新
        self._update_countdown_display()
    
    def _on_countdown_tick(self):
        """倒计时每秒触发"""
        self.countdown_seconds -= 1
        self._update_countdown_display()
        
        if self.countdown_seconds <= 0:
            self.countdown_timer.stop()
            self._on_countdown_finished()
    
    def _update_countdown_display(self):
        """更新倒计时显示"""
        if self.countdown_label:
            minutes = self.countdown_seconds // 60
            seconds = self.countdown_seconds % 60
            self.countdown_label.setText(f"{minutes:02d}:{seconds:02d}")
    
    def _on_countdown_finished(self):
        """倒计时结束"""
        # 显示完成提示，然后关闭
        self.encouragement.setText("✓ 活动时间到！继续加油！")
        if self.countdown_label:
            self.countdown_label.setText("")
        QtCore.QTimer.singleShot(3000, self.close_reminder)
    
    def close_reminder(self):
        """关闭提醒（可点击或定时）"""
        self._is_closing = True
        if hasattr(self, '_keep_alive_timer'):
            self._keep_alive_timer.stop()
        self.fade_out_and_close()
    
    def fade_out_and_close(self):
        """淡出动画"""
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        # 使用 hide() 而非 accept()，避免阻塞事件循环
        self.fade_animation.finished.connect(lambda: self.hide())
        self.fade_animation.start()
    
    def show_reminder(self, data: dict):
        """显示智能提醒"""
        # 显示窗口
        self.setWindowOpacity(1.0)
        self.show()
        self.raise_()
        self.activateWindow()
    
    def show_message(self, message: str):
        """兼容旧接口的简单消息显示 - 已禁用"""
        # 不显示任何窗口
        pass
    
    def show_encouragement_popup(self, message: str):
        """显示鼓励弹窗（简单模式，不模态）"""
        # 创建简单的鼓励提示窗口
        popup = QtWidgets.QMessageBox(self)
        popup.setWindowTitle("💫 加油！")
        popup.setText(message)
        popup.setIcon(QtWidgets.QMessageBox.Information)
        popup.setStyleSheet("""
            QMessageBox {
                background-color: rgba(20, 20, 30, 240);
            }
            QMessageBox QLabel {
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: rgba(76, 175, 80, 220);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: rgba(76, 175, 80, 250);
            }
        """)
        popup.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        popup.exec()
