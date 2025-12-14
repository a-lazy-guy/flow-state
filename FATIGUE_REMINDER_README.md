# 疲惫提醒系统 - 完整说明

你好！我已经为你设计并实现了一个完整的**疲惫提醒系统**。下面是详细说明：

## 📋 系统概览

```
连续工作时间追踪
       ↓
达到5小时后
       ↓
显示友好的提醒弹窗
       ↓
用户选择 (继续/延后/选择建议)
       ↓
根据选择进行相应操作
       ↓
继续追踪，6小时和7小时时再提醒
```

## 🎯 核心功能

### 1. 自动工作时间追踪 ⏱️
- ✅ 自动检测用户的工作活动
- ✅ 支持暂停和恢复
- ✅ 5分钟无活动自动暂停计时
- ✅ 格式化输出（如 "5小时30分钟"）

### 2. 智能提醒系统 🔔
- **5小时**：首次提醒 - "你已经连续工作很久了"
- **6小时**：二次提醒 - 再次强调休息的重要性
- **7小时**：持续提醒 - 再次提醒用户休息

每次提醒间隔至少1小时，防止频繁弹窗。

### 3. 美观的提醒UI 🎨
弹窗包含：
- ⏰ 工作时长显示
- 💡 休息建议卡片（6种）
- 🎯 操作按钮（继续/延后）
- 🎪 梯度背景和平滑动画

### 4. 智能休息建议 💪
系统提供6种科学的休息方式：

```
🚶 散步(10-15分钟)
   └─ 户外活动，呼吸新鲜空气，放松身心

😴 小睡(15-20分钟)
   └─ 让大脑得到充分恢复，非常有效

🧘 伸展运动(5-10分钟)
   └─ 缓解颈部、肩部、腰部肌肉疲劳

👀 眼部放松(3-5分钟)
   └─ 做眼睛保健操，保护视力

🥤 营养补充(5分钟)
   └─ 喝杯水或吃点水果，补充体力

🧖 冥想静坐(5-10分钟)
   └─ 深呼吸冥想，平复心绪
```

### 5. 灵活的提醒控制 ⏯️
用户可以：
- ✅ 点击"继续工作"忽略提醒
- ✅ 点击"30分钟后提醒"延后
- ✅ 点击"1小时后提醒"延长缓冲
- ✅ 点击建议卡片选择休息方式

## 📦 新增文件

### 1. `ui/component/fatigue_reminder.py` (274行)
**职责**：工作时间追踪和提醒逻辑

```python
class FatigueReminder(QtCore.QObject):
    # 关键方法：
    def mark_activity()          # 标记工作活动
    def get_work_duration()      # 获取工作时长（秒）
    def check_fatigue_reminder() # 检查是否需要提醒
    def snooze_reminder()        # 延后提醒
    def end_work_session()       # 结束工作会话
    
    # 常量：
    FATIGUE_THRESHOLD = 5 * 3600   # 5小时
    REMINDER_INTERVAL = 3600        # 1小时间隔
    IDLE_THRESHOLD = 300            # 5分钟无活动
```

**关键特性**：
- 📊 追踪累计工作时间和当前会话时间
- 🔍 检测空闲状态（5分钟无键盘/鼠标活动）
- ⏰ 发出 `fatigue_reminder_triggered` 信号
- 🎯 支持多个时间点提醒（5h、6h、7h）

### 2. `ui/component/fatigue_reminder_dialog.py` (351行)
**职责**：显示友好的提醒UI

```python
class FatigueReminderDialog(QtWidgets.QDialog):
    # 信号：
    continue_working = QtCore.Signal()
    snooze_clicked = QtCore.Signal(int)
    rest_selected = QtCore.Signal(str)
    
    # 包含的组件：
    - 工作时长显示
    - 警告提示文本
    - 6个休息建议卡片
    - 3个操作按钮

class RestSuggestionCard(QtWidgets.QWidget):
    # 单个建议卡片
    - 图标、标题、时长
    - 描述文本
    - Hover效果
```

**UI特性**：
- 🎨 梯度背景（蓝色系）
- ✨ 平滑的hover过渡效果
- 📱 可滚动的建议列表
- 🎯 清晰的操作按钮
- 🔝 始终置顶（不被其他窗口遮挡）

### 3. `ui/interaction_logic/reminder_logic.py` (修改)
**修改内容**：

```python
class EntertainmentReminder(QtCore.QObject):
    def __init__(self):
        # ... 原有代码 ...
        
        # 新增：疲惫提醒系统
        self.fatigue_reminder = FatigueReminder(parent)
        self.fatigue_reminder.fatigue_reminder_triggered.connect(
            self._on_fatigue_reminder_triggered
        )
    
    def on_status_update(self, result: dict):
        # ... 原有代码 ...
        
        # 新增：追踪工作活动
        if status in ['focus', 'work']:
            self.fatigue_reminder.mark_activity()
        
        # 新增：检查是否需要提醒
        self.fatigue_reminder.check_idle_and_update()
        fatigue_reminder_data = self.fatigue_reminder.check_fatigue_reminder()
        
    def _on_fatigue_reminder_triggered(self, reminder_data: dict):
        """处理疲惫提醒，显示对话框"""
        dialog = FatigueReminderDialog(reminder_data)
        dialog.show()
```

## 🔄 完整的数据流

```
┌─────────────────────────────────────────────────┐
│ main.py - 主程序                                 │
│ InputMonitor: 监控键盘/鼠标活动                  │
│ ScreenAnalyzer: 分析屏幕内容                     │
└─────────────┬───────────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────────────┐
│ MonitorThread                                   │
│ 每2秒收集一次数据                              │
│ 调用 API 分析用户状态                          │
└─────────────┬───────────────────────────────────┘
              │ status_updated 信号
              ↓
┌─────────────────────────────────────────────────┐
│ EntertainmentReminder.on_status_update()        │
│ ├─ 追踪娱乐时间（现有功能）                     │
│ └─ 追踪工作时间（新增功能）                     │
│    ├─ fatigue_reminder.mark_activity()         │
│    ├─ fatigue_reminder.check_idle_and_update() │
│    └─ fatigue_reminder.check_fatigue_reminder()│
└─────────────┬───────────────────────────────────┘
              │ fatigue_reminder_triggered 信号
              ↓
┌─────────────────────────────────────────────────┐
│ _on_fatigue_reminder_triggered()                │
│ 创建 FatigueReminderDialog 对话框              │
│ 连接用户交互信号                               │
│ 显示对话框                                     │
└─────────────┬───────────────────────────────────┘
              │
              ├─ continue_working → 继续工作
              ├─ snooze_clicked → 延后提醒
              └─ rest_selected → 记录选择
              │
              ↓
              继续工作时间追踪...
```

## 💻 代码集成示例

系统已自动集成到现有代码中，你无需修改 `main.py` 或其他文件。

但如果想深入理解，可以看这部分：

```python
# main.py 中：
from ui.interaction_logic.reminder_logic import EntertainmentReminder

reminder_logic = EntertainmentReminder(threshold_duration=0.5)
monitor_thread.status_updated.connect(reminder_logic.on_status_update)

# 疲惫提醒系统自动在 EntertainmentReminder.__init__ 中初始化
# 并在 on_status_update 中自动触发
```

## 🧪 快速测试

### 方式1：查看UI效果

```bash
python test_fatigue_reminder.py ui
```

这会显示一个完整的提醒弹窗。

### 方式2：测试逻辑

```bash
python test_fatigue_reminder.py logic
```

输出：
```
==================================================
疲惫提醒系统 - 逻辑测试
==================================================

1. 模拟开始工作...
   工作状态: True
   工作时长: 0小时0分钟

2. 模拟经过5小时...
   工作时长: 5小时0分钟

3. 检查是否触发提醒...
   ✓ 触发了提醒
   工作时长: 5小时0分钟
   里程碑: 5小时
   建议数: 6

...
```

### 方式3：快速测试（改配置）

编辑 `ui/component/fatigue_reminder.py` 第22行：

```python
# 改这行：
FATIGUE_THRESHOLD = 60  # 改成60秒，便于快速测试
```

然后运行主程序，工作1分钟后就会看到提醒！

## ⚙️ 常见自定义

### 1. 改变提醒时间（从5小时改成3小时）

编辑 `ui/component/fatigue_reminder.py`：

```python
class FatigueReminder(QtCore.QObject):
    FATIGUE_THRESHOLD = 3 * 3600  # 改成3小时
```

### 2. 改变提醒间隔（减少弹窗频率）

```python
REMINDER_INTERVAL = 7200  # 改成2小时间隔
```

### 3. 添加自定义休息建议

编辑 `ui/component/fatigue_reminder.py` 的 `_get_rest_suggestions()` 方法：

```python
def _get_rest_suggestions(self) -> list:
    return [
        {
            'title': '你的建议',
            'description': '描述信息',
            'duration': '5分钟',
            'icon': '🎯'
        },
        # ... 其他建议
    ]
```

### 4. 改变UI颜色

编辑 `ui/component/fatigue_reminder_dialog.py`，查找 `setStyleSheet()` 方法。

## 📚 文档结构

```
Flow-State 项目
├── README.md (项目简介)
├── FATIGUE_REMINDER_QUICKSTART.md (这个文件 - 快速开始)
├── FATIGUE_REMINDER_GUIDE.md (完整文档 - 详细说明)
├── main.py (主程序 - 集成了疲惫提醒)
└── ui/
    ├── component/
    │   ├── fatigue_reminder.py (疲惫提醒逻辑 - 新文件)
    │   ├── fatigue_reminder_dialog.py (疲惫提醒UI - 新文件)
    │   └── ...
    └── interaction_logic/
        └── reminder_logic.py (已集成疲惫提醒系统)
```

## 🎯 使用流程

### 基本流程

1. ▶️ 启动应用
   ```bash
   python main.py
   ```

2. 💼 开始工作
   - 系统自动开始计时

3. ⏰ 5小时后
   - 弹窗提醒
   - 显示工作时长和建议

4. 👆 用户选择
   - 继续工作
   - 或延后提醒
   - 或选择休息方式

### 示例场景

```
09:00 - 用户开始工作，系统开始计时
09:30 - 连续工作30分钟，系统继续计时
14:00 - 连续工作5小时
         ▼
    📱 [弹窗] 你已经连续工作很久了！
    📋 建议：散步、小睡、伸展运动...
    ✅ [继续工作] [30分钟后] [1小时后]
    
用户选择 "散步"
         ↓
    系统关闭弹窗，继续计时
    
14:15 - 散步完成，用户回来继续工作
         （累计工作时长：5小时15分钟）
         
18:00 - 连续工作9小时
         (累计: 9小时，但中间有休息)
         
19:00 - 继续工作10小时
         ▼
    📱 再次显示提醒（6小时或7小时的提醒）
```

## 🔐 安全性和稳定性

### ✅ 确保的特性

- 🔒 线程安全：使用 Qt 信号进行线程间通信
- ⚡ 高效：仅在必要时检查（每状态更新时）
- 🛡️ 错误处理：所有方法都有异常处理
- 📊 资源管理：时间戳作为计时，而非占用大量内存

### 🧪 已测试的场景

- ✅ 工作开始/暂停/恢复
- ✅ 空闲检测
- ✅ 多次提醒
- ✅ 延后提醒
- ✅ 会话结束

## 📖 下一步学习

1. **快速上手**：运行 `python test_fatigue_reminder.py ui` 看效果
2. **理解原理**：阅读 `FATIGUE_REMINDER_GUIDE.md`
3. **自定义配置**：修改常数和建议
4. **扩展功能**：添加数据持久化、统计分析等

## 🎉 总结

你现在拥有了一个完整的、生产级别的疲惫提醒系统，具有：

✨ 自动工作时间追踪
✨ 智能5小时提醒
✨ 美观友好的UI
✨ 6种科学的休息建议
✨ 灵活的用户交互
✨ 完整的中文文档
✨ 可测试的代码

**享受更健康、更高效的工作！** 💪

---

如有任何问题，请查看完整文档：[FATIGUE_REMINDER_GUIDE.md](FATIGUE_REMINDER_GUIDE.md)
