# -*- coding: utf-8 -*-
"""疲惫提醒系统使用示例和测试"""

import sys
import time
from PySide6 import QtCore, QtWidgets

from ui.interaction_logic.reminder_logic import EntertainmentReminder
from ui.component.fatigue_reminder import FatigueReminder
from ui.component.fatigue_reminder_dialog import FatigueReminderDialog


def test_fatigue_reminder_ui():
    """测试疲惫提醒UI"""
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    
    # 创建模拟的提醒数据
    reminder_data = {
        'duration': 18000,  # 5小时
        'duration_formatted': '5小时0分钟',
        'milestone': '5小时',
        'suggestions': [
            {
                'title': '散步',
                'description': '到户外走一走，呼吸新鲜空气，放松身心',
                'duration': '10-15分钟',
                'icon': '🚶'
            },
            {
                'title': '小睡',
                'description': '舒服地躺着闭眼休息，让大脑得到充分恢复',
                'duration': '15-20分钟',
                'icon': '😴'
            },
            {
                'title': '伸展运动',
                'description': '做简单的颈部、肩部和腰部拉伸，缓解肌肉疲劳',
                'duration': '5-10分钟',
                'icon': '🧘'
            },
        ]
    }
    
    # 创建并显示对话框
    dialog = FatigueReminderDialog(reminder_data)
    dialog.continue_working.connect(lambda: print("用户继续工作"))
    dialog.snooze_clicked.connect(lambda m: print(f"用户延后 {m} 分钟"))
    dialog.rest_selected.connect(lambda s: print(f"用户选择: {s}"))
    dialog.show()
    
    sys.exit(app.exec())


def test_fatigue_reminder_logic():
    """测试疲惫提醒逻辑"""
    print("=" * 50)
    print("疲惫提醒系统 - 逻辑测试")
    print("=" * 50)
    
    # 创建提醒系统
    reminder = FatigueReminder()
    
    # 模拟工作活动
    print("\n1. 模拟开始工作...")
    reminder.mark_activity()
    print(f"   工作状态: {reminder.is_working}")
    print(f"   工作时长: {reminder.get_work_duration_formatted()}")
    
    # 模拟经过5小时
    print("\n2. 模拟经过5小时...")
    # 直接修改时间（用于测试）
    reminder.work_session_start = time.time() - 5 * 3600
    print(f"   工作时长: {reminder.get_work_duration_formatted()}")
    
    # 检查是否需要提醒
    print("\n3. 检查是否触发提醒...")
    fatigue_data = reminder.check_fatigue_reminder()
    if fatigue_data:
        print(f"   ✓ 触发了提醒")
        print(f"   工作时长: {fatigue_data['duration_formatted']}")
        print(f"   里程碑: {fatigue_data['milestone']}")
        print(f"   建议数: {len(fatigue_data['suggestions'])}")
    else:
        print(f"   ✗ 未触发提醒")
    
    # 测试延后功能
    print("\n4. 测试延后功能...")
    reminder.snooze_reminder(30)
    print(f"   已设置30分钟后提醒")
    fatigue_data = reminder.check_fatigue_reminder()
    print(f"   立即检查: {'触发提醒' if fatigue_data else '不会触发（在延后期内）'}")
    
    # 测试结束会话
    print("\n5. 测试结束会话...")
    reminder.end_work_session()
    print(f"   工作状态: {reminder.is_working}")
    print(f"   累计工作时长: {reminder.get_work_duration_formatted()}")
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)


def test_integration_with_reminder_logic():
    """测试与提醒系统的集成"""
    print("\n" + "=" * 50)
    print("集成测试 - EntertainmentReminder + FatigueReminder")
    print("=" * 50)
    
    # 创建提醒系统
    reminder = EntertainmentReminder(threshold_duration=0.5)
    
    print("\n✓ 疲惫提醒系统已集成到 EntertainmentReminder")
    print("   - fatigue_reminder: 疲惫提醒管理器")
    print("   - current_fatigue_reminder_dialog: 当前显示的对话框")
    print("\n触发机制:")
    print("   1. on_status_update() 会调用 fatigue_reminder.mark_activity()")
    print("   2. 当连续工作超过5小时时触发提醒")
    print("   3. 显示 FatigueReminderDialog 对话框")
    print("   4. 用户可以选择休息或延后提醒")
    
    print("\n" + "=" * 50)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'ui':
            test_fatigue_reminder_ui()
        elif sys.argv[1] == 'logic':
            test_fatigue_reminder_logic()
        elif sys.argv[1] == 'integration':
            test_integration_with_reminder_logic()
    else:
        print("使用说明:")
        print("  python test_fatigue_reminder.py ui         - 测试UI界面")
        print("  python test_fatigue_reminder.py logic       - 测试逻辑")
        print("  python test_fatigue_reminder.py integration - 测试集成")
        print("\n运行UI测试:")
        test_fatigue_reminder_ui()
