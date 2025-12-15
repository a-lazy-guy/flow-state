# -*- coding: utf-8 -*-
"""
工作疲劳提醒系统
运行后30秒自动触发疲劳提醒
"""

import sys
import os
import time

try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QFont, QColor
    from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QProgressBar, QFrame
except ImportError:
    from PyQt5 import QtCore, QtGui, QtWidgets
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtGui import QFont, QColor
    from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QProgressBar, QFrame


class FatigueReminderDialog(QDialog):
    """工作疲劳提醒对话框"""
    
    def __init__(self, severity='medium', duration=120, parent=None):
        super().__init__(parent)
        self.severity = severity
        self.duration = duration
        
        self.setWindowTitle("工作疲劳提醒")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(500, 600)
        
        self.setup_ui()
        
    def setup_ui(self):
        """构建UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 背景框架
        self.bg_frame = QFrame()
        self.bg_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 20px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        bg_layout = QVBoxLayout()
        bg_layout.setContentsMargins(40, 40, 40, 40)
        bg_layout.setSpacing(25)
        
        # 关闭按钮
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(40, 40)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 24px;
                color: #999;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #e74c3c;
            }
        """)
        close_btn.clicked.connect(self.accept)
        
        # 标题区域
        header_layout = QHBoxLayout()
        
        # 图标
        icon_label = QLabel("⚠️")
        icon_label.setFont(QFont("Arial", 48))
        icon_label.setFixedSize(80, 80)
        
        # 标题和描述
        title_layout = QVBoxLayout()
        title_layout.setSpacing(8)
        
        title = QLabel("你需要休息一下了")
        title.setFont(QFont("Microsoft YaHei", 22, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        
        severity_text = self._get_severity_text()
        severity_label = QLabel(severity_text)
        severity_label.setFont(QFont("Microsoft YaHei", 13))
        severity_label.setStyleSheet("color: #7f8c8d;")
        
        title_layout.addWidget(title)
        title_layout.addWidget(severity_label)
        
        header_layout.addWidget(icon_label)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addWidget(close_btn, alignment=Qt.AlignTop)
        
        bg_layout.addLayout(header_layout)
        
        # 分割线
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("border: 1px solid #ecf0f1;")
        bg_layout.addWidget(divider)
        
        # 统计信息区域
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(30)
        
        # 持续时长
        duration_widget = self._create_stat_widget(
            "⏱️",
            "连续工作",
            f"{self.duration}分钟",
            "#3498db"
        )
        stats_layout.addWidget(duration_widget)
        
        # 严重程度
        severity_widget = self._create_stat_widget(
            "⚡",
            "疲劳程度",
            self._get_severity_cn(),
            self._get_severity_color()
        )
        stats_layout.addWidget(severity_widget)
        
        bg_layout.addLayout(stats_layout)
        
        # 进度条
        progress_label = QLabel("疲劳指数")
        progress_label.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        progress_label.setStyleSheet("color: #2c3e50;")
        
        self.progress = QProgressBar()
        self.progress.setMaximum(100)
        self.progress.setValue(self._calculate_fatigue_score())
        self.progress.setFixedHeight(8)
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background-color: #ecf0f1;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {self._get_severity_color()};
                border-radius: 4px;
            }}
        """)
        
        bg_layout.addWidget(progress_label)
        bg_layout.addWidget(self.progress)
        
        # 建议文本
        suggestion = QLabel(self._get_suggestion())
        suggestion.setFont(QFont("Microsoft YaHei", 12))
        suggestion.setStyleSheet("color: #34495e; line-height: 1.6;")
        suggestion.setWordWrap(True)
        suggestion.setFixedHeight(60)
        
        bg_layout.addWidget(suggestion)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        rest_btn = QPushButton("立即休息")
        rest_btn.setFixedHeight(45)
        rest_btn.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        rest_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        rest_btn.clicked.connect(self.accept)
        
        continue_btn = QPushButton("继续工作")
        continue_btn.setFixedHeight(45)
        continue_btn.setFont(QFont("Microsoft YaHei", 12))
        continue_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #5d6d7b;
            }
        """)
        continue_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(rest_btn)
        btn_layout.addWidget(continue_btn)
        
        bg_layout.addLayout(btn_layout)
        
        self.bg_frame.setLayout(bg_layout)
        main_layout.addWidget(self.bg_frame)
        
        self.setLayout(main_layout)
        
    def _create_stat_widget(self, icon: str, label: str, value: str, color: str):
        """创建统计小部件"""
        widget = QtWidgets.QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Arial", 28))
        icon_label.setAlignment(Qt.AlignCenter)
        
        label_widget = QLabel(label)
        label_widget.setFont(QFont("Microsoft YaHei", 10))
        label_widget.setStyleSheet("color: #7f8c8d;")
        label_widget.setAlignment(Qt.AlignCenter)
        
        value_widget = QLabel(value)
        value_widget.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        value_widget.setStyleSheet(f"color: {color};")
        value_widget.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(icon_label)
        layout.addWidget(label_widget)
        layout.addWidget(value_widget)
        
        widget.setLayout(layout)
        return widget
    
    def _get_severity_text(self) -> str:
        """获取严重程度文本"""
        if self.severity == 'low':
            return "你已经连续工作有一段时间了，不如稍作休息"
        elif self.severity == 'medium':
            return "你已经工作了很久，建议停下来活动一下身体"
        else:  # high
            return "你已经工作太久了！必须立即休息，保护颈椎和眼睛"
    
    def _get_severity_cn(self) -> str:
        """获取严重程度中文"""
        return {'low': '低', 'medium': '中', 'high': '高'}.get(self.severity, '未知')
    
    def _get_severity_color(self) -> str:
        """获取严重程度颜色"""
        colors = {
            'low': '#3498db',
            'medium': '#f39c12',
            'high': '#e74c3c'
        }
        return colors.get(self.severity, '#95a5a6')
    
    def _calculate_fatigue_score(self) -> int:
        """计算疲劳指数"""
        if self.severity == 'low':
            return 30
        elif self.severity == 'medium':
            return 60
        else:
            return 90
    
    def _get_suggestion(self) -> str:
        """获取建议"""
        suggestions = {
            'low': '💡 建议：站起来走动走动，做个简单的拉伸运动，放松颈椎。',
            'medium': '💡 建议：立即停下来！离开电脑，眨眼休息，转动颈椎和肩膀。',
            'high': '💡 建议：必须休息！停止所有工作，做眼保健操，走出去呼吸新鲜空气。'
        }
        return suggestions.get(self.severity, '💡 建议：适当休息，保持健康。')


def show_reminder_after_30s():
    """30秒后显示疲劳提醒"""
    app = QApplication(sys.argv)
    
    # 30秒后显示提醒
    def trigger_reminder():
        # 随机选择严重程度
        import random
        severity = random.choice(['low', 'medium', 'high'])
        durations = {'low': 30, 'medium': 120, 'high': 240}
        
        dialog = FatigueReminderDialog(severity=severity, duration=durations[severity])
        dialog.exec()
        app.quit()
    
    timer = QTimer()
    timer.timeout.connect(trigger_reminder)
    timer.setSingleShot(True)
    timer.start(30000)  # 30秒
    
    sys.exit(app.exec())


if __name__ == '__main__':
    show_reminder_after_30s()
