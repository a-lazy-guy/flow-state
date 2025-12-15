"""
自动化测试弹窗显示
模拟鼠标悬停事件，不需要手动操作
"""
import sys
import os

try:
    from PySide6 import QtCore, QtGui, QtWidgets
except ImportError:
    from PyQt5 import QtCore, QtGui, QtWidgets

from ui.component.float_ball import SuspensionBall
from ui.interaction_logic.pop_up import CardPopup

def main():
    app = QtWidgets.QApplication(sys.argv)
    
    # 创建资源
    assets_dir = os.path.join(os.getcwd(), "assets")
    os.makedirs(assets_dir, exist_ok=True)
    card_path = os.path.join(assets_dir, "focus_card.png")
    
    if not os.path.exists(card_path):
        img = QtGui.QImage(300, 400, QtGui.QImage.Format_ARGB32)
        img.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(img)
        painter.setBrush(QtGui.QColor(40, 40, 40, 200))
        painter.drawRoundedRect(0, 0, 300, 400, 20, 20)
        painter.end()
        img.save(card_path)
    
    # 1. 创建悬浮球和弹窗
    ball = SuspensionBall()
    popup = CardPopup(card_path, ball_size=ball.height())
    
    ball.show()
    
    # 2. 连接信号
    def on_entered():
        print("\n✓ 信号已触发: ball.entered")
        if not popup.isVisible():
            print("  执行 popup.showFromBall()...")
            popup.showFromBall(ball)
            print(f"  执行完成，popup.isVisible() = {popup.isVisible()}")
        
        # 延迟 1 秒后关闭
        QtCore.QTimer.singleShot(1000, lambda: (
            print("\n → 1秒后，准备隐藏弹窗"),
            popup.hideToBall(ball),
            QtCore.QTimer.singleShot(500, app.quit)
        ))
    
    ball.entered.connect(on_entered)
    
    # 3. 自动模拟鼠标进入事件
    print("自动测试弹窗显示...")
    print("步骤：")
    print("1. 创建悬浮球和弹窗")
    print("2. 模拟鼠标进入悬浮球")
    print("3. 检查弹窗是否显示")
    print("-" * 50)
    
    def trigger_hover():
        print("\n[自动化测试] 触发悬浮球的 entered 信号...")
        ball.entered.emit()
    
    # 延迟 500ms 后触发悬停事件
    QtCore.QTimer.singleShot(500, trigger_hover)
    
    app.setQuitOnLastWindowClosed(False)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
