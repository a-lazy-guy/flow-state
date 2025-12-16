"""
[正在使用]
番茄钟确认弹窗。
"""
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

class TomatoClockDialog(QtWidgets.QDialog):
    """番茄钟开启确认弹窗 - 沿用娱乐提醒的暖黄风格"""
    
    if hasattr(QtCore, 'Signal'):
        Signal = QtCore.Signal
    else:
        Signal = QtCore.pyqtSignal
        
    start_tomato_clicked = Signal()
    cancel_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True) # 模态对话框
        self.setWindowFlags(
            qt_const("FramelessWindowHint")
            | qt_const("WindowStaysOnTopHint")
        )
        
        wa_translucent = qt_const("WA_TranslucentBackground")
        if wa_translucent is not None:
            self.setAttribute(wa_translucent)
            
        # 尺寸设置 (比提醒弹窗小一点)
        self.setFixedSize(500, 350)
        
        # 主容器 - 学生版暖黄主题
        self.container = QtWidgets.QWidget(self)
        self.container.setObjectName("TomatoDialog")
        self.container.setStyleSheet("""
            QWidget#TomatoDialog {
                background-color: #E8F5E9;  /* 淡绿背景，护眼 */
                border: 2px solid #A5D6A7; /* 柔和边框 */
                border-radius: 20px;
            }
        """)
        
        # 主布局
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.container)
        
        # 容器内布局
        layout = QtWidgets.QVBoxLayout(self.container)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # 标题
        self.title_label = QtWidgets.QLabel("需要开番茄钟吗？")
        self.title_label.setAlignment(qt_const("AlignCenter"))
        self.title_label.setStyleSheet("""
            QLabel { 
                color: #F57C00;      /* 橙红标题 */ 
                font-size: 26px; 
                font-weight: bold; 
                background: transparent;
                border: none;
            } 
        """)
        layout.addWidget(self.title_label)
        
        # 说明文字
        self.desc_label = QtWidgets.QLabel("开启番茄钟，让我们专注25分钟，\n效率倍增！🍅")
        self.desc_label.setAlignment(qt_const("AlignCenter"))
        self.desc_label.setStyleSheet("""
            QLabel { 
                color: #5D4037;      /* 深棕文字 */ 
                font-size: 18px; 
                background: transparent;
                border: none;
            } 
        """)
        layout.addWidget(self.desc_label)
        
        # 按钮栏
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(30)
        button_layout.setAlignment(qt_const("AlignCenter"))
        
        # 按钮：是 (开启)
        yes_button = QtWidgets.QPushButton("是 (开启)")
        yes_button.setMinimumHeight(50)
        yes_button.setMinimumWidth(140)
        yes_button.setCursor(qt_const("PointingHandCursor"))
        yes_button.setStyleSheet("""
            QPushButton { 
                background: #66BB6A; /* 自然绿 */ 
                color: white; 
                border-radius: 12px; 
                font-size: 18px;
                font-weight: bold;
                border: none;
            } 
            QPushButton:hover {
                background: #4CAF50;
            }
            QPushButton:pressed {
                background: #388E3C;
            }
        """)
        yes_button.clicked.connect(self.on_yes)
        button_layout.addWidget(yes_button)
        
        # 按钮：否 (取消)
        no_button = QtWidgets.QPushButton("否 (不用了)")
        no_button.setMinimumHeight(50)
        no_button.setMinimumWidth(140)
        no_button.setCursor(qt_const("PointingHandCursor"))
        no_button.setStyleSheet("""
            QPushButton { 
                background: transparent; 
                color: #FF7043; 
                border: 2px solid #FF7043; 
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
            } 
            QPushButton:hover {
                background: rgba(255, 112, 67, 0.1);
            }
            QPushButton:pressed {
                background: rgba(255, 112, 67, 0.2);
            }
        """)
        no_button.clicked.connect(self.on_no)
        button_layout.addWidget(no_button)
        
        layout.addLayout(button_layout)
        
    def on_yes(self):
        self.start_tomato_clicked.emit()
        self.accept()
        
    def on_no(self):
        self.cancel_clicked.emit()
        self.reject()
