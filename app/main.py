import sys
import os
import time

try:
    from PySide6 import QtCore, QtGui, QtWidgets
except ImportError:
    from PyQt5 import QtCore, QtGui, QtWidgets

from app.ui.widgets.float_ball import SuspensionBall
from app.ui.views.popup_view import CardPopup
from app.ui.widgets.dialogs.fatigue import FatigueReminderDialog
from app.services.reminder.manager import EntertainmentReminder
from app.services.monitor_service import MonitorThread
from app.core.database import init_db

def ensure_card_png(path):
    if not os.path.exists(path):
        img = QtGui.QImage(300, 400, QtGui.QImage.Format_ARGB32)
        img.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(img)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        painter.setBrush(QtGui.QColor(40, 40, 40, 200))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(0, 0, 300, 400, 20, 20)
        
        painter.setPen(QtGui.QColor(255, 255, 255))
        font = QtGui.QFont("Microsoft YaHei", 12)
        painter.setFont(font)
        painter.drawText(img.rect(), QtCore.Qt.AlignCenter, "Focus Card")
        
        painter.end()
        img.save(path)

def main():
    try:
        if hasattr(QtCore.Qt, 'AA_ShareOpenGLContexts'):
            QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    except Exception:
        pass

    # 初始化数据库
    init_db()

    app = QtWidgets.QApplication(sys.argv)
    
    # 确保资源目录存在
    # Note: Assuming assets are at the root of the project
    assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
    os.makedirs(assets_dir, exist_ok=True)
    card_path = os.path.join(assets_dir, "focus_card.png")
    ensure_card_png(card_path)
    
    ball = SuspensionBall()
    ball.show()
    
    popup = CardPopup(card_path, ball_size=ball.height())
    popup.update_focus_status({"status": "working", "duration": 3600, "message": ""})

    entertainment_reminder = EntertainmentReminder()
    
    def on_ball_hover():
        if not popup.isVisible():
            popup.showFromBall(ball)
            
    ball.entered.connect(on_ball_hover)
    
    def on_ball_clicked():
        if popup.isVisible():
            popup.hideToBall(ball)
        else:
            popup.showFromBall(ball)
    ball.clicked.connect(on_ball_clicked)
    
    ball.positionChanged.connect(lambda pos: popup.followBall(ball))
    
    monitor_thread = MonitorThread()
    
    def on_status_update(result):
        # Using static data for demo as requested previously
        result = {"status": "working", "duration": 3600, "message": ""}
        status = result['status']
        duration = result['duration']
        popup.update_focus_status(result)
        
        # Fatigue reminder logic
        if not hasattr(on_status_update, 'app_start_time'):
            on_status_update.app_start_time = time.time()
        
        if not hasattr(on_status_update, 'fatigue_reminder_shown'):
            on_status_update.fatigue_reminder_shown = False
        
        if not on_status_update.fatigue_reminder_shown:
            elapsed_time = time.time() - on_status_update.app_start_time
            if elapsed_time >= 15:  
                on_status_update.fatigue_reminder_shown = True
                print("[MAIN] 程序运行 15 秒，弹出疲劳休息提醒")
                minutes = 60
                on_status_update.fatigue_dialog = FatigueReminderDialog(severity='medium', duration=minutes)
                on_status_update.fatigue_dialog.show()
        
        # Entertainment reminder logic
        if not hasattr(on_status_update, 'test_entertainment_shown'):
            on_status_update.test_entertainment_shown = False
            
        elapsed_time = time.time() - on_status_update.app_start_time

        if elapsed_time >= 60 and not on_status_update.test_entertainment_shown:
            on_status_update.test_entertainment_shown = True
            print("[MAIN] 程序运行已达60秒，触发一次预设娱乐提醒")
            entertainment_reminder._handle_entertainment_warning('entertainment', 60, 'medium')

        status_map = {
            'working': 'focus',
            'entertainment': 'distract_lite',
            'idle': 'rest'
        }
        
        ball_state = status_map.get(status, 'focus')
        if status == 'entertainment' and duration > 60:
            ball_state = 'distract_heavy'
            
        ball.update_state(ball_state)
        
        mins = int(duration / 60)
        if mins > 0:
            ball.update_data(text=f"{mins}m")
        else:
            ball.update_data(text="")
            
    monitor_thread.status_updated.connect(on_status_update)
    monitor_thread.start()
    
    report_path = os.path.join(assets_dir, "daily_summary_report.png")
    if not os.path.exists(report_path):
        try:
            from app.ui.widgets.report import daily as daily_sum
            pass 
        except Exception:
            pass

    app.setQuitOnLastWindowClosed(False)
    exit_code = app.exec()
    
    monitor_thread.stop()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
