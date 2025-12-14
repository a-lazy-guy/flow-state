# 疲惫提醒系统 - 快速参考卡

## 🎯 核心概念

```
┌─ 自动工作时间追踪 ─┐
│  • 用户工作 → 系统自动计时
│  • 5分钟无活动 → 自动暂停
│  • 恢复活动 → 自动继续计时
└────────────────────┘
         ↓
┌─ 达到5小时阈值 ─┐
│  • 触发提醒信号
│  • 显示提醒对话框
│  • 展示休息建议
└────────────────────┘
         ↓
┌─ 用户交互 ─────┐
│  • 继续工作
│  • 延后30分钟
│  • 延后1小时
│  • 选择休息方式
└────────────────────┘
```

## 📝 代码速查表

### 查看工作时长
```python
from ui.component.fatigue_reminder import FatigueReminder

reminder = FatigueReminder()
# ... 用户工作中 ...

# 获取工作时长（秒）
duration_seconds = reminder.get_work_duration()

# 获取格式化时长
duration_str = reminder.get_work_duration_formatted()
print(duration_str)  # 输出: "5小时30分钟"
```

### 创建和显示提醒对话框
```python
from ui.component.fatigue_reminder_dialog import FatigueReminderDialog

reminder_data = {
    'duration': 18000,
    'duration_formatted': '5小时0分钟',
    'milestone': '5小时',
    'suggestions': [...]  # 6个建议
}

dialog = FatigueReminderDialog(reminder_data)
dialog.continue_working.connect(on_continue)
dialog.snooze_clicked.connect(on_snooze)
dialog.rest_selected.connect(on_rest)
dialog.show()
```

### 处理用户交互
```python
# 继续工作
dialog.continue_working.connect(lambda: print("用户继续工作"))

# 延后提醒
dialog.snooze_clicked.connect(
    lambda minutes: print(f"延后 {minutes} 分钟")
)

# 选择休息方式
dialog.rest_selected.connect(
    lambda title: print(f"用户选择: {title}")
)
```

## 🔧 常用配置

### 改变提醒阈值

**位置**：`ui/component/fatigue_reminder.py` 第22-24行

```python
# 当前配置（5小时）
FATIGUE_THRESHOLD = 5 * 3600      # 秒

# 改成3小时
FATIGUE_THRESHOLD = 3 * 3600

# 改成1小时（用于快速测试）
FATIGUE_THRESHOLD = 60
```

### 改变提醒间隔

**位置**：`ui/component/fatigue_reminder.py` 第25行

```python
# 当前配置（1小时）
REMINDER_INTERVAL = 3600          # 秒

# 改成30分钟（减少频率）
REMINDER_INTERVAL = 1800

# 改成15分钟（增加频率）
REMINDER_INTERVAL = 900
```

### 改变闲置检测时间

**位置**：`ui/component/fatigue_reminder.py` 第26行

```python
# 当前配置（5分钟）
IDLE_THRESHOLD = 300              # 秒

# 改成10分钟
IDLE_THRESHOLD = 600

# 改成3分钟
IDLE_THRESHOLD = 180
```

## 🎨 UI定制

### 改变背景颜色

**位置**：`ui/component/fatigue_reminder_dialog.py` 

查找这部分代码：
```python
container.setStyleSheet("""
    QWidget {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #e8f4f8, stop:1 #f0f7ff);  # ← 改这里
        border: 2px solid #3498db;             # ← 和这里
    }
""")
```

改成你喜欢的颜色：
```python
# 暖色调
stop:0 #fff5e6, stop:1 #ffe8cc

# 绿色调
stop:0 #e6f9f0, stop:1 #d4f1e6

# 紫色调
stop:0 #f0e6ff, stop:1 #e6d4ff
```

### 改变标题文本

**位置**：`ui/component/fatigue_reminder_dialog.py` 第186行

```python
main_title = QtWidgets.QLabel("你已经连续工作很久了")  # ← 改这里
```

## 📊 数据查询

### 获取当前工作状态
```python
reminder = EntertainmentReminder()
fatigue = reminder.fatigue_reminder

# 是否正在工作
is_working = fatigue.is_working  # True/False

# 工作时长（秒）
duration = fatigue.get_work_duration()

# 格式化显示
duration_str = fatigue.get_work_duration_formatted()

# 是否需要提醒
reminder_data = fatigue.check_fatigue_reminder()
if reminder_data:
    print(f"需要提醒，工作时长: {reminder_data['duration_formatted']}")
```

### 获取建议列表
```python
reminder = FatigueReminder()
suggestions = reminder._get_rest_suggestions()

for suggestion in suggestions:
    print(f"{suggestion['icon']} {suggestion['title']}")
    print(f"  {suggestion['description']}")
    print(f"  推荐时长: {suggestion['duration']}")
```

## 🧪 快速测试

### 测试1：查看UI
```bash
python test_fatigue_reminder.py ui
```
显示完整的提醒对话框

### 测试2：测试逻辑
```bash
python test_fatigue_reminder.py logic
```
输出逻辑验证结果

### 测试3：快速触发提醒（改配置）
```python
# fatigue_reminder.py 第22行改为：
FATIGUE_THRESHOLD = 60  # 1分钟

# 然后运行
python main.py
# 工作1分钟后就会看到提醒
```

## 📱 集成点

### 在你的主程序中使用

疲惫提醒系统已自动集成到 `EntertainmentReminder`，无需额外配置：

```python
# main.py
from ui.interaction_logic.reminder_logic import EntertainmentReminder

reminder_logic = EntertainmentReminder()
# 疲惫提醒系统自动初始化并工作！
```

### 监听提醒信号

```python
# 如果需要自定义处理
reminder_logic.fatigue_reminder.fatigue_reminder_triggered.connect(
    your_custom_handler
)

def your_custom_handler(reminder_data):
    duration = reminder_data['duration_formatted']
    print(f"用户已工作: {duration}")
```

## 🐛 常见问题速答

| 问题 | 答案 |
|------|------|
| 提醒没显示？ | 检查 `fatigue_reminder.is_working` 是否为 `True` |
| 想更早提醒？ | 改 `FATIGUE_THRESHOLD = 3 * 3600` (改成3小时) |
| 想延迟提醒？ | 改 `FATIGUE_THRESHOLD = 8 * 3600` (改成8小时) |
| 提醒太频繁？ | 改 `REMINDER_INTERVAL = 7200` (改成2小时) |
| 快速测试？ | 改 `FATIGUE_THRESHOLD = 60` (1分钟) |
| 改界面颜色？ | 编辑 `fatigue_reminder_dialog.py` 的 `setStyleSheet()` |
| 添加建议？ | 编辑 `_get_rest_suggestions()` 方法 |
| 禁用系统？ | 注释掉 `reminder_logic.py` 中的初始化代码 |

## 📂 文件导航

```
ui/component/
├── fatigue_reminder.py           ← 核心逻辑
├── fatigue_reminder_dialog.py    ← UI界面
└── ...

ui/interaction_logic/
├── reminder_logic.py             ← 集成点（已修改）
└── ...

根目录/
├── test_fatigue_reminder.py      ← 测试脚本
├── FATIGUE_REMINDER_README.md    ← 完整说明
├── FATIGUE_REMINDER_GUIDE.md     ← 详细文档
├── FATIGUE_REMINDER_QUICKSTART.md ← 快速开始
└── IMPLEMENTATION_SUMMARY.md      ← 实现总结
```

## 🔑 核心类和方法

### FatigueReminder

```python
# 创建实例
reminder = FatigueReminder()

# 关键方法
reminder.mark_activity()                    # 标记工作活动
reminder.get_work_duration()               # 获取工作时长(秒)
reminder.get_work_duration_formatted()     # 获取格式化时长
reminder.check_idle_and_update()           # 检查闲置状态
reminder.check_fatigue_reminder()          # 检查是否需要提醒
reminder.snooze_reminder(30)               # 延后30分钟提醒
reminder.end_work_session()                # 结束工作会话
reminder.reset_session()                   # 重置会话

# 属性
reminder.is_working                        # 是否正在工作
reminder.work_session_start                # 会话开始时间
reminder.cumulative_work_time              # 累计工作时间
```

### FatigueReminderDialog

```python
# 创建对话框
dialog = FatigueReminderDialog(reminder_data)

# 连接信号
dialog.continue_working.connect(callback)
dialog.snooze_clicked.connect(callback)
dialog.rest_selected.connect(callback)

# 显示
dialog.show()
```

## 💾 保存用户数据（扩展）

```python
# 在 reminder_logic.py 中添加

def _on_rest_suggestion_selected(self, suggestion_title: str):
    # 保存用户选择
    import json
    from datetime import datetime
    
    record = {
        'timestamp': datetime.now().isoformat(),
        'work_duration': self.fatigue_reminder.get_work_duration(),
        'rest_choice': suggestion_title
    }
    
    # 写入文件或数据库
    with open('fatigue_history.json', 'a') as f:
        f.write(json.dumps(record) + '\n')
```

## 📈 生成统计报告（扩展）

```python
# 分析工作数据
import json
from collections import Counter

# 读取历史
with open('fatigue_history.json', 'r') as f:
    records = [json.loads(line) for line in f]

# 统计
total_work = sum(r['work_duration'] for r in records) / 3600  # 小时
rest_choices = Counter(r['rest_choice'] for r in records)

print(f"总工作时长: {total_work:.1f} 小时")
print(f"最常选择的休息方式: {rest_choices.most_common(1)}")
```

---

**快速参考卡已准备好！** 🎯

需要更多帮助？查看 `FATIGUE_REMINDER_GUIDE.md`
