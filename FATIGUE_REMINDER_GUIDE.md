# 疲惫提醒系统使用指南

## 概述

疲惫提醒系统是一个智能化的工作时间监控系统，当用户连续工作超过5小时后，会显示一个友好的提醒弹窗，建议用户进行休息。

## 功能特性

### 1. 连续工作时间追踪
- 自动追踪用户的工作活动
- 支持暂停/恢复计时
- 检测用户闲置状态（5分钟无活动自动暂停计时）

### 2. 渐进式提醒
- **5小时**：首次提醒
- **6小时**：二次提醒
- **7小时**：持续提醒
- 每个提醒间隔至少1小时，防止频繁弹窗

### 3. 智能休息建议
系统提供6种休息建议：
- 🚶 **散步** (10-15分钟)：户外活动，呼吸新鲜空气
- 😴 **小睡** (15-20分钟)：让大脑充分恢复
- 🧘 **伸展运动** (5-10分钟)：缓解肌肉疲劳
- 👀 **眼部放松** (3-5分钟)：眼睛保健操
- 🥤 **营养补充** (5分钟)：补充体力和水分
- 🧖 **冥想静坐** (5-10分钟)：平复心绪

### 4. 灵活的提醒控制
- 继续工作：关闭提醒，继续工作
- 30分钟后提醒：给自己30分钟的缓冲时间
- 1小时后提醒：延长休息时间

### 5. 用户交互
- 点击休息建议卡片可以了解更多信息
- 美观的梯度背景和响应式设计
- 始终置顶显示，不会被其他窗口遮挡

## 系统架构

### 核心模块

#### 1. FatigueReminder (fatigue_reminder.py)
**职责**：工作时间追踪和提醒逻辑控制

```python
# 创建实例
reminder = FatigueReminder()

# 标记工作活动
reminder.mark_activity()

# 获取工作时长
duration = reminder.get_work_duration()  # 返回秒数
formatted = reminder.get_work_duration_formatted()  # 返回格式化字符串

# 检查是否需要提醒
reminder_data = reminder.check_fatigue_reminder()

# 延后提醒
reminder.snooze_reminder(minutes=30)

# 结束工作会话
reminder.end_work_session()
```

**关键属性**：
- `FATIGUE_THRESHOLD`: 5小时（18000秒）
- `REMINDER_INTERVAL`: 提醒间隔1小时（3600秒）
- `IDLE_THRESHOLD`: 闲置阈值5分钟（300秒）

#### 2. FatigueReminderDialog (fatigue_reminder_dialog.py)
**职责**：显示友好的提醒UI界面

```python
# 创建对话框
dialog = FatigueReminderDialog(reminder_data)

# 连接信号
dialog.continue_working.connect(callback)
dialog.snooze_clicked.connect(lambda minutes: callback(minutes))
dialog.rest_selected.connect(lambda title: callback(title))

# 显示
dialog.show()
```

#### 3. EntertainmentReminder (reminder_logic.py)
**职责**：集成疲惫提醒系统与现有提醒逻辑

- 在 `__init__` 中创建 `FatigueReminder` 实例
- 在 `on_status_update()` 中调用 `mark_activity()` 和 `check_fatigue_reminder()`
- 处理用户交互回调

## 集成说明

### 在主程序中使用

疲惫提醒系统已自动集成到 `EntertainmentReminder` 中，无需额外配置：

```python
# main.py
from ui.interaction_logic.reminder_logic import EntertainmentReminder

reminder_logic = EntertainmentReminder(threshold_duration=0.5)
monitor_thread.status_updated.connect(reminder_logic.on_status_update)
```

### 工作流程

1. **活动检测**：当用户进行工作/专注活动时
2. **时间追踪**：系统自动记录工作时长
3. **状态检查**：定期检查是否达到5小时阈值
4. **触发提醒**：达到阈值时显示 `FatigueReminderDialog`
5. **用户交互**：用户可以选择继续工作或延后提醒
6. **后续追踪**：继续监控工作时间，6小时和7小时时再次提醒

## 数据流

```
InputMonitor (监控键盘/鼠标)
       ↓
MonitorThread (分析数据)
       ↓
on_status_update() (处理状态更新)
       ↓
FatigueReminder.mark_activity() (记录活动)
       ↓
FatigueReminder.check_fatigue_reminder() (检查是否需要提醒)
       ↓
FatigueReminderDialog (显示提醒)
       ↓
用户交互 (继续/延后/选择建议)
```

## 自定义配置

### 修改提醒阈值

编辑 `fatigue_reminder.py`：

```python
class FatigueReminder(QtCore.QObject):
    # 修改这些常量
    FATIGUE_THRESHOLD = 5 * 3600      # 改成其他小时数
    REMINDER_INTERVAL = 3600           # 改成其他间隔
    IDLE_THRESHOLD = 300               # 改成其他闲置时间
```

### 添加自定义休息建议

编辑 `fatigue_reminder.py` 中的 `_get_rest_suggestions()` 方法：

```python
def _get_rest_suggestions(self) -> list:
    return [
        {
            'title': '自定义建议',
            'description': '具体描述',
            'duration': '持续时间',
            'icon': '😊'
        },
        # ... 其他建议
    ]
```

### 修改UI样式

编辑 `fatigue_reminder_dialog.py` 中的样式表：

```python
# 修改颜色、字体、边框等
container.setStyleSheet("""
    QWidget {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #your_color_1, stop:1 #your_color_2);
    }
""")
```

## 测试

### 运行测试

```bash
# 测试UI界面
python test_fatigue_reminder.py ui

# 测试逻辑
python test_fatigue_reminder.py logic

# 测试集成
python test_fatigue_reminder.py integration
```

### 加速测试

如果想快速测试5小时提醒，可以修改 `FatigueReminder` 的常量：

```python
FATIGUE_THRESHOLD = 60  # 改成1分钟进行测试
```

## 常见问题

### Q: 提醒没有显示？
A: 请检查以下几点：
1. 确保 `FatigueReminder` 的 `is_working` 状态为 `True`
2. 确保 `on_status_update()` 被正确调用
3. 检查工作时长是否确实达到5小时以上

### Q: 如何禁用疲惫提醒？
A: 在 `EntertainmentReminder.__init__()` 中注释掉相关代码，或在 `FatigueReminder` 中添加禁用标志。

### Q: 可以自定义提醒消息吗？
A: 可以，在 `fatigue_reminder_dialog.py` 中修改标题和提示文本。

### Q: 如何记录用户的休息选择？
A: 在 `_on_rest_suggestion_selected()` 方法中添加数据库或日志代码。

## 技术细节

### 时间计算

- 工作时长 = 累计时间 + 当前会话时间
- 当前会话时间 = 当前时间 - 会话开始时间
- 闲置检测 = 当前时间 - 最后活动时间

### 信号和槽

```
FatigueReminder.fatigue_reminder_triggered
    → EntertainmentReminder._on_fatigue_reminder_triggered()
    → FatigueReminderDialog.show()

FatigueReminderDialog.continue_working
    → EntertainmentReminder._on_fatigue_continue_working()

FatigueReminderDialog.snooze_clicked
    → EntertainmentReminder._on_fatigue_snooze()

FatigueReminderDialog.rest_selected
    → EntertainmentReminder._on_rest_suggestion_selected()
```

### 线程安全

- `FatigueReminder` 是 `QtCore.QObject`，使用信号通知主线程
- 所有UI操作在主线程中进行
- 时间计算使用 `time.time()` 确保一致性

## 扩展建议

1. **数据持久化**：保存用户的工作时长和休息选择
2. **统计分析**：显示每周/每月的工作时长统计
3. **个性化设置**：让用户自定义提醒时间和建议
4. **语音提醒**：在显示对话框的同时播放提醒语音
5. **渐进式增强**：根据用户反馈调整提醒频率

## 许可证和作者

这是 Flow-State 项目的一部分。

---

**最后更新**：2024年12月
**版本**：1.0
