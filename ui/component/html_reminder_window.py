"""
Qt 提醒窗口：纯 Qt 实现，支持疲劳提醒和休息建议。
关闭窗口时直接销毁，不留任何残留。
"""

try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtCore import Qt, QTimer, QPropertyAnimation
    from PySide6.QtGui import QFont
except ImportError:
    from PyQt5 import QtCore, QtGui, QtWidgets
    from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation
    from PyQt5.QtGui import QFont


class SuggestionCard(QtWidgets.QWidget):
    """休息建议卡片"""
    clicked = QtCore.Signal(str, int)
    
    def __init__(self, icon, title, description, duration_text, parent=None):
        super().__init__(parent)
        self.icon = icon
        self.title = title
        self.description = description
        self.duration_text = duration_text
        self.is_active = False
        self.countdown_timer = None
        self.remaining_seconds = 0
        
        self.setFixedHeight(100)
        self.setCursor(Qt.PointingHandCursor)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(20)
        
        icon_label = QtWidgets.QLabel(icon)
        icon_label.setFont(QFont("Arial", 28))
        icon_label.setFixedSize(50, 50)
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        text_layout = QtWidgets.QVBoxLayout()
        title_label = QtWidgets.QLabel(title)
        title_label.setFont(QFont("Microsoft YaHei", 15, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        text_layout.addWidget(title_label)
        
        desc_label = QtWidgets.QLabel(description)
        desc_label.setFont(QFont("Microsoft YaHei", 13))
        desc_label.setStyleSheet("color: #555;")
        desc_label.setWordWrap(True)
        text_layout.addWidget(desc_label)
        
        self.countdown_label = QtWidgets.QLabel("")
        self.countdown_label.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        self.countdown_label.setStyleSheet("color: #27ae60;")
        text_layout.addWidget(self.countdown_label)
        
        layout.addLayout(text_layout, 1)
        
        duration_label = QtWidgets.QLabel(duration_text)
        duration_label.setFont(QFont("Microsoft YaHei", 12))
        duration_label.setStyleSheet("color: #95a5a6;")
        duration_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        layout.addWidget(duration_label)
        
        self.update_style()
    
    def update_style(self):
        """更新样式"""
        if self.is_active:
            self.setStyleSheet("SuggestionCard { background: #e8f8f5; border: 2px solid #27ae60; border-radius: 12px; }")
        else:
            self.setStyleSheet("""
                SuggestionCard {
                    background: white;
                    border: 1px solid #ecf0f1;
                    border-radius: 12px;
                }
                SuggestionCard:hover {
                    background: #f8f9fa;
                    border: 2px solid #3498db;
                }
            """)
    
    def start_countdown(self, minutes):
        """开始倒计时"""
        self.is_active = True
        self.remaining_seconds = minutes * 60
        self.update_style()
        
        if self.countdown_timer:
            self.countdown_timer.stop()
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self._update_countdown)
        self.countdown_timer.start(1000)
        self._update_countdown()
    
    def _update_countdown(self):
        """更新倒计时显示"""
        if self.remaining_seconds <= 0:
            if self.countdown_timer:
                self.countdown_timer.stop()
            self.countdown_label.setText("")
            self.is_active = False
            self.update_style()
        else:
            mins = self.remaining_seconds // 60
            secs = self.remaining_seconds % 60
            self.countdown_label.setText(f"倒计时: {mins}分{secs}秒")
            self.remaining_seconds -= 1
    
    def stop_countdown(self):
        """停止倒计时"""
        if self.countdown_timer:
            self.countdown_timer.stop()
        self.countdown_label.setText("")
        self.is_active = False
        self.update_style()
    
    def mousePressEvent(self, event):
        """点击卡片"""
        if not self.is_active:
            import re
            match = re.search(r'(\d+)', self.duration_text)
            minutes = int(match.group(1)) if match else 10
            self.clicked.emit(self.title, minutes)


class QtReminderWindow(QtWidgets.QWidget):
    """Qt 实现的疲劳提醒窗口"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("疲惫提醒")
        self.setGeometry(100, 100, 1000, 800)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("QtReminderWindow { background-color: transparent; }")
        
        self.active_card = None
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.dialog = QtWidgets.QWidget()
        self.dialog.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e8f4f8, stop:1 #f0f7ff);
                border: 2px solid #3498db;
                border-radius: 20px;
            }
        """)
        
        dialog_layout = QtWidgets.QVBoxLayout(self.dialog)
        dialog_layout.setContentsMargins(50, 50, 50, 50)
        dialog_layout.setSpacing(24)
        
        close_btn = QtWidgets.QPushButton("✕")
        close_btn.setFixedSize(40, 40)
        close_btn.setStyleSheet("QPushButton { background: transparent; border: none; color: #999; font-size: 24px; } QPushButton:hover { color: #e74c3c; }")
        close_btn.clicked.connect(self.close_window)
        close_btn_container = QtWidgets.QHBoxLayout()
        close_btn_container.addStretch()
        close_btn_container.addWidget(close_btn)
        close_btn_container.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addLayout(close_btn_container)
        
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setSpacing(20)
        
        icon_label = QtWidgets.QLabel("⏰")
        icon_label.setFont(QFont("Arial", 36))
        icon_label.setFixedSize(60, 60)
        icon_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(icon_label)
        
        title_layout = QtWidgets.QVBoxLayout()
        self.title = QtWidgets.QLabel("你已经连续工作很久了")
        self.title.setFont(QFont("Microsoft YaHei", 22, QFont.Bold))
        self.title.setStyleSheet("color: #e74c3c;")
        title_layout.addWidget(self.title)
        
        self.duration_label = QtWidgets.QLabel("工作时长: 5小时0分钟")
        self.duration_label.setFont(QFont("Microsoft YaHei", 16))
        self.duration_label.setStyleSheet("color: #2980b9;")
        title_layout.addWidget(self.duration_label)
        
        header_layout.addLayout(title_layout, 1)
        dialog_layout.addLayout(header_layout)
        
        tip_label = QtWidgets.QLabel("连续工作过久会导致疲劳、注意力下降，甚至影响身体健康。建议你立即休息一会儿，恢复精力会让你更高效！")
        tip_label.setFont(QFont("Microsoft YaHei", 14))
        tip_label.setStyleSheet("QLabel { background-color: #fff9e6; border-left: 4px solid #f39c12; padding: 16px 20px; border-radius: 8px; color: #555; }")
        tip_label.setWordWrap(True)
        tip_label.setMinimumHeight(80)
        dialog_layout.addWidget(tip_label)
        
        suggestion_title = QtWidgets.QLabel("💡 推荐的休息方式：")
        suggestion_title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        suggestion_title.setStyleSheet("color: #2c3e50;")
        dialog_layout.addWidget(suggestion_title)
        
        self.suggestions_widget = QtWidgets.QWidget()
        self.suggestions_layout = QtWidgets.QVBoxLayout(self.suggestions_widget)
        self.suggestions_layout.setSpacing(10)
        
        suggestions_data = [
            ("🚶", "散步", "到户外走一走，呼吸新鲜空气，放松身心", "10-15分钟"),
            ("😴", "小睡", "舒服地躺着闭眼休息，让大脑得到充分恢复", "15-20分钟"),
            ("🧘", "伸展运动", "做简单的颈部、肩部和腰部拉伸，缓解肌肉疲劳", "5-10分钟"),
            ("👀", "眼部放松", "看看远处，眨眨眼睛，做眼睛保健操", "3-5分钟"),
            ("🥤", "营养补充", "喝杯水或吃点水果，补充体力和水分", "5分钟"),
            ("🧖", "冥想静坐", "找个安静的地方，深呼吸冥想，平复心绪", "5-10分钟"),
        ]
        
        self.suggestion_cards = []
        for icon, title, desc, duration in suggestions_data:
            card = SuggestionCard(icon, title, desc, duration)
            card.clicked.connect(self._on_suggestion_clicked)
            self.suggestion_cards.append(card)
            self.suggestions_layout.addWidget(card)
        
        suggestions_scroll = QtWidgets.QScrollArea()
        suggestions_scroll.setWidget(self.suggestions_widget)
        suggestions_scroll.setWidgetResizable(True)
        suggestions_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        suggestions_scroll.setFixedHeight(450)
        dialog_layout.addWidget(suggestions_scroll)
        
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.setAlignment(Qt.AlignCenter)
        
        continue_btn = self._create_button("继续工作 💪", "#95a5a6", "#7f8c8d")
        continue_btn.clicked.connect(self._on_continue)
        button_layout.addWidget(continue_btn)
        
        snooze_30_btn = self._create_button("30分钟后提醒", "#f39c12", "#e67e22")
        snooze_30_btn.clicked.connect(lambda: self._on_snooze(30))
        button_layout.addWidget(snooze_30_btn)
        
        snooze_60_btn = self._create_button("1小时后提醒", "#e74c3c", "#c0392b")
        snooze_60_btn.clicked.connect(lambda: self._on_snooze(60))
        button_layout.addWidget(snooze_60_btn)
        
        dialog_layout.addLayout(button_layout)
        
        self.info_label = QtWidgets.QLabel("")
        self.info_label.setFont(QFont("Microsoft YaHei", 11))
        self.info_label.setStyleSheet("QLabel { background-color: #e8f4f8; border: 1px solid #3498db; border-radius: 8px; padding: 15px; color: #2c3e50; }")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setVisible(False)
        dialog_layout.addWidget(self.info_label)
        
        main_layout.addWidget(self.dialog)
        
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(350)
    
    def _create_button(self, text, bg_color, hover_color):
        """创建样式化按钮"""
        btn = QtWidgets.QPushButton(text)
        btn.setMinimumHeight(52)
        btn.setMinimumWidth(160)
        btn.setFont(QFont("Microsoft YaHei", 13, QFont.Bold))
        btn.setStyleSheet(f"QPushButton {{ background-color: {bg_color}; color: white; border: none; border-radius: 10px; padding: 12px 24px; }} QPushButton:hover {{ background-color: {hover_color}; }}")
        return btn
    
    def _on_suggestion_clicked(self, title, minutes):
        """建议卡片点击"""
        if self.active_card and self.active_card != self.sender():
            self.active_card.stop_countdown()
        
        card = self.sender()
        card.start_countdown(minutes)
        self.active_card = card
        
        self._show_info(f"已开始{title}，请准时完成！")
    
    def _on_continue(self):
        """继续工作"""
        for card in self.suggestion_cards:
            card.stop_countdown()
        self.active_card = None
        self.title.setText("太棒了！🎯")
        self.duration_label.setText("你做的很对，专注才能成就梦想！\n加油，我看好你！💪")
        self._show_info("好的，继续工作。记住定期活动一下身体！")
        QTimer.singleShot(1500, self.close_window)
    
    def _on_snooze(self, minutes):
        """暂停提醒"""
        for card in self.suggestion_cards:
            card.stop_countdown()
        self.active_card = None
        self.title.setText(f"好的，{minutes}分钟后见～")
        self.duration_label.setText(f"已设置{minutes}分钟后提醒。继续加油！")
        self._show_info(f"已设置{minutes}分钟后提醒。")
        QTimer.singleShot(1500, self.close_window)
    
    def _show_info(self, message):
        """显示信息"""
        self.info_label.setText(message)
        self.info_label.setVisible(True)
        QTimer.singleShot(3000, lambda: self.info_label.setVisible(False))
    
    def close_window(self):
        """关闭窗口"""
        for card in self.suggestion_cards:
            card.stop_countdown()
        
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        try:
            self.fade_animation.finished.disconnect()
        except (RuntimeError, TypeError):
            pass
        self.fade_animation.finished.connect(self.close)
        self.fade_animation.start()
    
    def show_reminder(self, duration=0):
        """显示提醒窗口"""
        hours = int(duration / 3600)
        mins = int((duration % 3600) / 60)
        self.duration_label.setText(f"工作时长: {hours}小时{mins}分钟")
        self.setWindowOpacity(1.0)
        self.show()
        self.raise_()
        self.activateWindow()


class ReminderOverlayWebBased(QtWidgets.QWidget):
    """包装 QtReminderWindow，提供与其他提醒组件兼容的接口。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.window = None

    def show_reminder(self, duration=0):
        """显示提醒窗口。"""
        self.window = QtReminderWindow()
        self.window.show_reminder(duration)
