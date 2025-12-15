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
        self.setFixedSize(500, 720)
        
        self.setup_ui()
        self._center_window()
        
    def _center_window(self):
        """将窗口居中显示"""
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            x = geometry.x() + (geometry.width() - self.width()) // 2
            y = geometry.y() + (geometry.height() - self.height()) // 2
            self.move(x, y)
        
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
                border: none;
            }
        """)
        
        bg_layout = QVBoxLayout()
        bg_layout.setContentsMargins(40, 20, 40, 40)  # 减少顶部边距 (40 -> 20)
        bg_layout.setSpacing(15)  # 减少整体控件间距 (25 -> 15)
        
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
        
        # 顶部区域 (关闭按钮)
        top_layout = QHBoxLayout()
        top_layout.addStretch()
        top_layout.addWidget(close_btn)
        
        # 将顶部布局插入到主背景布局的最开始，并且不添加额外的间距
        bg_layout.addLayout(top_layout)
        
        # 头部整体区域（图标+标题）
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_frame.setStyleSheet("""
            QFrame#headerFrame {
                background-color: rgba(248, 249, 250, 200);
                border-radius: 20px;
                border: 1px solid rgba(0, 0, 0, 0.03);
            }
            QFrame#headerFrame:hover {
                background-color: rgba(240, 242, 245, 220);
                border: 1px solid rgba(0, 0, 0, 0.08);
            }
        """)
        
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 20, 20, 20)
        header_layout.setSpacing(10)
        
        # 图标 (居中)
        icon_label = QLabel("⚠️")
        icon_label.setFont(QFont("Arial", 48))
        icon_label.setFixedSize(100, 100)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("background: transparent; border: none;")
        header_layout.addWidget(icon_label, alignment=Qt.AlignCenter)
        
        # 标题 (居中)
        title = QLabel("你需要休息一下了")
        title.setFont(QFont("Microsoft YaHei", 22, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; background: transparent; border: none;")
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title)
        
        # 描述文本 (在方框外)
        severity_text = self._get_severity_text()
        severity_label = QLabel(severity_text)
        severity_label.setFont(QFont("Microsoft YaHei", 13))
        severity_label.setStyleSheet("color: #7f8c8d; background: transparent; border: none;")
        severity_label.setAlignment(Qt.AlignCenter)
        
        # 使用负边距将整体向上拉
        bg_layout.addSpacing(-20)
        bg_layout.addWidget(header_frame)
        bg_layout.addWidget(severity_label)
        
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
        score_layout = QHBoxLayout()
        score_layout.setSpacing(10)
        
        progress_label = QLabel("疲劳指数")
        progress_label.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        progress_label.setStyleSheet("color: #2c3e50;")
        
        score_val = self._calculate_fatigue_score()
        score_label = QLabel(f"{score_val}%")
        score_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        score_label.setStyleSheet(f"color: {self._get_severity_color()};")
        
        score_layout.addWidget(progress_label)
        score_layout.addWidget(score_label)
        score_layout.addStretch()
        
        bg_layout.addLayout(score_layout)
        
        self.progress = QProgressBar()
        self.progress.setMaximum(100)
        self.progress.setValue(score_val)
        self.progress.setFixedHeight(8)
        self.progress.setTextVisible(False)  # 隐藏进度条上的文字
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
        
        bg_layout.addWidget(self.progress)
        
        # 建议文本区域
        suggestion_frame = QFrame()
        suggestion_frame.setObjectName("suggestionFrame")
        suggestion_frame.setStyleSheet("""
            QFrame#suggestionFrame {
                background-color: rgba(248, 249, 250, 200);
                border-radius: 16px;
                border: 1px solid rgba(0, 0, 0, 0.03);
            }
            QFrame#suggestionFrame:hover {
                background-color: rgba(240, 242, 245, 220);
                border: 1px solid rgba(0, 0, 0, 0.08);
            }
        """)
        
        sugg_layout = QVBoxLayout(suggestion_frame)
        sugg_layout.setContentsMargins(20, 15, 20, 15)
        
        suggestion = QLabel(self._get_suggestion())
        suggestion.setFont(QFont("Microsoft YaHei", 12))
        suggestion.setStyleSheet("color: #34495e; line-height: 1.6; background: transparent; border: none;")
        suggestion.setWordWrap(True)
        suggestion.setAlignment(Qt.AlignCenter)
        
        sugg_layout.addWidget(suggestion)
        bg_layout.addWidget(suggestion_frame)
        
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
        widget.setObjectName("statWidget")
        widget.setStyleSheet("""
            QWidget#statWidget {
                background-color: rgba(248, 249, 250, 200);
                border-radius: 16px;
                border: 1px solid rgba(0, 0, 0, 0.03);
            }
            QWidget#statWidget:hover {
                background-color: rgba(240, 242, 245, 220);
                border: 1px solid rgba(0, 0, 0, 0.08);
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(10, 15, 10, 15)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Arial", 28))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setMinimumHeight(50)
        icon_label.setStyleSheet("background: transparent; border: none;")
        
        label_widget = QLabel(label)
        label_widget.setFont(QFont("Microsoft YaHei", 10))
        label_widget.setStyleSheet("color: #7f8c8d; background: transparent; border: none;")
        label_widget.setAlignment(Qt.AlignCenter)
        
        value_widget = QLabel(value)
        value_widget.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        value_widget.setStyleSheet(f"color: {color}; background: transparent; border: none;")
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
    timer.start(3000)  # 30秒
    
    sys.exit(app.exec())


if __name__ == '__main__':
    show_reminder_after_30s()
