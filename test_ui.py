#!/usr/bin/env python3
"""
快速 UI 测试：只显示悬浮球和弹窗，无需 AI 后端。
"""
import sys
import os

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtGui import QImage, QPainter, QColor, QFont

# 导入 UI 组件
from ui.component.float_ball import SuspensionBall
from ui.interaction_logic.pop_up import CardPopup

def ensure_card_png(path):
    """生成占位图片"""
    if not os.path.exists(path):
        try:
            img = QImage(300, 400, QImage.Format.Format_ARGB32)
            img.fill(QColor(0, 0, 0, 0))
            painter = QPainter(img)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            painter.setBrush(QColor(40, 40, 40, 200))
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.drawRoundedRect(0, 0, 300, 400, 20, 20)
            
            painter.setPen(QColor(255, 255, 255))
            font = QFont("Microsoft YaHei", 12)
            painter.setFont(font)
            painter.drawText(img.rect(), QtCore.Qt.AlignmentFlag.AlignCenter, "Focus Card")
            
            painter.end()
            img.save(path)
            print(f"[TEST] PNG created at {path}")
        except Exception as e:
            print(f"[TEST] Error creating PNG: {e}")

def main():
    print("[TEST] ====== 启动 UI 测试 ======", flush=True)
    
    app = QtWidgets.QApplication(sys.argv)
    print("[TEST] QApplication 创建完成", flush=True)
    
    # 准备资源
    assets_dir = os.path.join(os.getcwd(), "assets")
    os.makedirs(assets_dir, exist_ok=True)
    card_path = os.path.join(assets_dir, "focus_card.png")
    ensure_card_png(card_path)
    
    # 创建悬浮球
    print("[TEST] 创建 SuspensionBall...", flush=True)
    ball = SuspensionBall()
    print(f"[TEST] SuspensionBall 大小: {ball.size()}, 位置: {ball.pos()}", flush=True)
    ball.show()
    print("[TEST] SuspensionBall 已显示", flush=True)
    
    # 创建弹窗
    print("[TEST] 创建 CardPopup...", flush=True)
    popup = CardPopup(card_path, ball_size=ball.height())
    popup.setMinimumSize(280, 200)
    print(f"[TEST] CardPopup 大小: {popup.size()}", flush=True)
    
    # 连接信号
    def on_ball_hover():
        print("[TEST] Ball hovered, showing popup", flush=True)
        if not popup.isVisible():
            try:
                popup.showFromBall(ball)
                print("[TEST] Popup shown successfully", flush=True)
            except Exception as e:
                print(f"[TEST] Error showing popup: {e}")
                import traceback
                traceback.print_exc()
    
    def on_ball_clicked():
        print("[TEST] Ball clicked", flush=True)
        if popup.isVisible():
            try:
                popup.hideToBall(ball)
            except Exception as e:
                print(f"[TEST] Error hiding popup: {e}")
        else:
            try:
                popup.showFromBall(ball)
            except Exception as e:
                print(f"[TEST] Error showing popup: {e}")
    
    ball.entered.connect(on_ball_hover)
    ball.clicked.connect(on_ball_clicked)
    
    if popup:
        ball.positionChanged.connect(lambda pos: popup.followBall(ball))
    
    # 运行
    app.setQuitOnLastWindowClosed(False)
    print("[TEST] 进入事件循环...", flush=True)
    exit_code = app.exec()
    
    print("[TEST] 退出", flush=True)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
