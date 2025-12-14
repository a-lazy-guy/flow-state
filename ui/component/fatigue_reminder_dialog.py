# -*- coding: utf-8 -*-
"""疲惫提醒弹窗UI"""

from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6 import QtCore as QtCore
    from PySide6 import QtGui as QtGui
    from PySide6 import QtWidgets as QtWidgets
else:
    try:
        from PySide6 import QtCore, QtGui, QtWidgets
        QT_LIB = "PySide6"
    except ImportError:
        from PyQt5 import QtCore, QtGui, QtWidgets
        QT_LIB = "PyQt5"


def qt_const(name: str) -> Any:
    """获取Qt常量"""
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


class RestSuggestionCard(QtWidgets.QWidget):
    """单个休息建议卡片"""
    
    clicked = QtCore.Signal()
    
    def __init__(self, suggestion: dict, parent=None):
        super().__init__(parent)
        self.suggestion = suggestion
        self.is_hovered = False
        
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setMouseTracking(True)
        
        # 布局
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)
        
        # 标题行（图标 + 标题 + 时长）
        title_layout = QtWidgets.QHBoxLayout()
        
        # 图标
        icon_label = QtWidgets.QLabel(suggestion['icon'])
        icon_label.setStyleSheet("font-size: 24px;")
        icon_label.setFixedWidth(30)
        title_layout.addWidget(icon_label)
        
        # 标题
        title_label = QtWidgets.QLabel(suggestion['title'])
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        title_layout.addWidget(title_label)
        
        # 时长
        duration_label = QtWidgets.QLabel(suggestion['duration'])
        duration_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #95a5a6;
                font-weight: 500;
            }
        """)
        duration_label.setAlignment(qt_const("AlignRight") | qt_const("AlignVCenter"))
        title_layout.addWidget(duration_label)
        
        layout.addLayout(title_layout)
        
        # 描述
        desc_label = QtWidgets.QLabel(suggestion['description'])
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #555555;
                line-height: 1.5;
            }
        """)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # 设置卡片样式
        self.setStyleSheet("""
            RestSuggestionCard {
                background-color: #ffffff;
                border: 1px solid #ecf0f1;
                border-radius: 8px;
            }
        """)
        
        self.setMaximumHeight(100)
    
    def enterEvent(self, event):
        """鼠标进入"""
        self.is_hovered = True
        self.setStyleSheet("""
            RestSuggestionCard {
                background-color: #f8f9fa;
                border: 2px solid #3498db;
                border-radius: 8px;
            }
        """)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """鼠标离开"""
        self.is_hovered = False
        self.setStyleSheet("""
            RestSuggestionCard {
                background-color: #ffffff;
                border: 1px solid #ecf0f1;
                border-radius: 8px;
            }
        """)
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """鼠标点击"""
        self.clicked.emit()
        super().mousePressEvent(event)


class FatigueReminderDialog(QtWidgets.QDialog):
    """疲惫提醒对话框
    
    当用户连续工作5小时后显示，提供休息建议
    """
    
    continue_working = QtCore.Signal()  # 继续工作
    snooze_clicked = QtCore.Signal(int)  # 延后提醒（分钟数）
    rest_selected = QtCore.Signal(str)  # 选择了某个休息建议
    
    def __init__(self, reminder_data: dict, parent=None):
        super().__init__(parent)
        self.reminder_data = reminder_data
        self.setModal(False)
        
        # 窗口属性
        self.setWindowFlags(
            qt_const("FramelessWindowHint")
            | qt_const("WindowStaysOnTopHint")
        )
        
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
        if screen is None:
            desktop = getattr(QtWidgets.QApplication, "desktop", None)
            screen = desktop() if callable(desktop) else None
        
        if screen is not None:
            geometry = screen.availableGeometry()
        else:
            geometry = QtCore.QRect(0, 0, 1200, 800)
        
        # 设置窗口大小和位置
        window_width = 800
        window_height = 700
        center_x = geometry.left() + (geometry.width() - window_width) // 2
        center_y = geometry.top() + (geometry.height() - window_height) // 2
        self.setGeometry(center_x, center_y, window_width, window_height)
        
        # 创建主UI
        self._setup_ui()
    
    def _setup_ui(self):
        """创建UI"""
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(qt_const("AlignCenter"))
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 容器背景
        container = QtWidgets.QWidget()
        container.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e8f4f8, stop:1 #f0f7ff);
                border-radius: 20px;
                border: 2px solid #3498db;
            }
        """)
        main_layout.addWidget(container)
        
        # 容器内布局
        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)
        
        # ========== 标题区域 ==========
        title_layout = QtWidgets.QHBoxLayout()
        
        # 警告图标
        warning_label = QtWidgets.QLabel("⏰")
        warning_label.setStyleSheet("font-size: 48px;")
        warning_label.setFixedSize(60, 60)
        warning_label.setAlignment(qt_const("AlignCenter"))
        title_layout.addWidget(warning_label)
        
        # 标题文本
        title_text_layout = QtWidgets.QVBoxLayout()
        
        main_title = QtWidgets.QLabel("你已经连续工作很久了")
        main_title.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: #e74c3c;
            }
        """)
        title_text_layout.addWidget(main_title)
        
        duration_label = QtWidgets.QLabel(
            f"工作时长: {self.reminder_data.get('duration_formatted', '未知')}"
        )
        duration_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #2980b9;
                font-weight: 500;
            }
        """)
        title_text_layout.addWidget(duration_label)
        
        title_layout.addLayout(title_text_layout)
        title_layout.addStretch()
        
        layout.addLayout(title_layout)
        
        # ========== 提示文本 ==========
        tip_label = QtWidgets.QLabel(
            "连续工作过久会导致疲劳、注意力下降，甚至影响身体健康。\n"
            "建议你立即休息一会儿，恢复精力会让你更高效！"
        )
        tip_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #555555;
                line-height: 1.6;
                background-color: #fff9e6;
                padding: 12px 16px;
                border-radius: 8px;
                border-left: 4px solid #f39c12;
            }
        """)
        tip_label.setWordWrap(True)
        layout.addWidget(tip_label)
        
        # ========== 建议列表 ==========
        suggestions_label = QtWidgets.QLabel("💡 推荐的休息方式：")
        suggestions_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        layout.addWidget(suggestions_label)
        
        # 建议卡片滚动区域
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 8px;
                background-color: #ecf0f1;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #95a5a6;
                border-radius: 4px;
            }
        """)
        
        scroll_content = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(10)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加建议卡片
        suggestions = self.reminder_data.get('suggestions', [])
        for suggestion in suggestions:
            card = RestSuggestionCard(suggestion)
            card.clicked.connect(lambda s=suggestion: self._on_suggestion_clicked(s))
            scroll_layout.addWidget(card)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        # ========== 按钮区域 ==========
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(12)
        
        # 继续工作按钮
        continue_btn = QtWidgets.QPushButton("继续工作")
        continue_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7a7b;
            }
        """)
        continue_btn.clicked.connect(self._on_continue_clicked)
        button_layout.addWidget(continue_btn)
        
        # 延后30分钟
        snooze_30_btn = QtWidgets.QPushButton("30分钟后提醒")
        snooze_30_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:pressed {
                background-color: #d35400;
            }
        """)
        snooze_30_btn.clicked.connect(lambda: self._on_snooze_clicked(30))
        button_layout.addWidget(snooze_30_btn)
        
        # 延后1小时
        snooze_60_btn = QtWidgets.QPushButton("1小时后提醒")
        snooze_60_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        snooze_60_btn.clicked.connect(lambda: self._on_snooze_clicked(60))
        button_layout.addWidget(snooze_60_btn)
        
        layout.addLayout(button_layout)
    
    def _on_suggestion_clicked(self, suggestion: dict):
        """处理建议卡片点击"""
        self.rest_selected.emit(suggestion['title'])
        self.close()
    
    def _on_continue_clicked(self):
        """继续工作"""
        self.continue_working.emit()
        self.close()
    
    def _on_snooze_clicked(self, minutes: int):
        """延后提醒"""
        self.snooze_clicked.emit(minutes)
        self.close()
