#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""简化的提醒测试 - 直接测试新的科技风提醒界面"""

import sys
import time
from PySide6 import QtCore, QtGui, QtWidgets

# 导入新的提醒界面
from ui.component.reminder import ReminderOverlay

def main():
    app = QtWidgets.QApplication(sys.argv)
    
    print("[TEST] 启动简化提醒测试...")
    
    # 创建提醒窗口
    overlay = ReminderOverlay()
    
    # 模拟30秒娱乐数据
    test_data = {
        'message': '检测到您正在看视频',
        'icon': '◆',
        'history': [
            ('entertainment', 30, '看视频 30秒'),
            ('focus', 5, '之前工作 5分钟'),
        ],
        'duration': 30,
        'threshold': 30,
        'encouragement': '时间飞快～该休息一下了！',
        'severity': 'medium'
    }
    
    # 显示提醒
    print("[TEST] 显示提醒界面...")
    overlay.show_reminder(test_data)
    
    # 3秒后自动关闭
    QtCore.QTimer.singleShot(3000, lambda: print("[TEST] 应该看到提醒了！按Ctrl+C退出"))
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
