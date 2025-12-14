# 疲惫提醒系统 - 快速启动指南

## ⚡ 快速开始

疲惫提醒系统已经完全集成到你的 Flow-State 应用中。无需任何额外配置，系统会自动工作！

## 🎯 如何使用

### 基本流程

1. **启动应用**
   ```bash
   python main.py
   ```

2. **开始工作**
   - 开始进行工作/专注活动
   - 系统自动开始计时

3. **连续工作5小时后**
   - 📱 会显示一个友好的提醒弹窗
   - 展示当前工作时长和休息建议

4. **做出选择**
   - 🚶 选择一个休息建议
   - 或者"30分钟后提醒"
   - 或者"1小时后提醒"
   - 或者"继续工作"

## 📁 新增文件说明

### 核心文件

| 文件 | 描述 |
|------|------|
| `ui/component/fatigue_reminder.py` | 🔧 疲惫提醒逻辑引擎 |
| `ui/component/fatigue_reminder_dialog.py` | 🎨 疲惫提醒UI对话框 |
| `test_fatigue_reminder.py` | ✅ 测试和演示脚本 |
| `FATIGUE_REMINDER_GUIDE.md` | 📖 完整使用文档 |

### 修改文件

| 文件 | 修改内容 |
|------|---------|
| `ui/interaction_logic/reminder_logic.py` | 集成疲惫提醒系统 |

## 🧪 测试功能

### 快速测试UI界面

```bash
python test_fatigue_reminder.py ui
```

这将弹出一个包含所有休息建议的提醒窗口。

### 加速测试（5小时太长）

编辑 `ui/component/fatigue_reminder.py`，修改第22行：

```python
# 改这一行（从5小时改成1分钟用于测试）
FATIGUE_THRESHOLD = 60  # 1分钟，便于快速测试
```

然后运行应用，工作1分钟后就会看到提醒。

## 🎨 UI特性

### 美观的设计
- ⏰ 大字体警告图标
- 🎨 柔和的梯度背景
- 📱 响应式卡片设计
- ✨ 平滑的过渡和动画

### 交互特性
- 🖱️ 点击任何卡片查看详情
- ⏱️ 多个延后选项
- 🎯 清晰的操作按钮
- 📜 可滚动的建议列表

## 🔧 核心功能

### 自动工作时间追踪
```python
# 系统自动调用，无需手动操作
fatigue_reminder.mark_activity()
```

### 智能闲置检测
- 5分钟无活动 → 自动暂停计时
- 有新活动 → 自动恢复计时

### 灵活的提醒控制
- 5小时：首次提醒 ⏰
- 6小时：二次提醒 ⏰⏰
- 7小时：持续提醒 ⏰⏰⏰
- 延后功能：每次延后后重新计时

## 📊 提醒建议

系统会建议以下6种休息方式：

| 图标 | 建议 | 时长 | 描述 |
|------|------|------|------|
| 🚶 | 散步 | 10-15分钟 | 户外活动，呼吸新鲜空气 |
| 😴 | 小睡 | 15-20分钟 | 让大脑充分恢复 |
| 🧘 | 伸展运动 | 5-10分钟 | 缓解肌肉疲劳 |
| 👀 | 眼部放松 | 3-5分钟 | 眼睛保健操 |
| 🥤 | 营养补充 | 5分钟 | 补充体力和水分 |
| 🧖 | 冥想静坐 | 5-10分钟 | 平复心绪 |

## ⚙️ 自定义配置

### 修改提醒时间（从5小时改成其他）

编辑 `ui/component/fatigue_reminder.py`：

```python
class FatigueReminder(QtCore.QObject):
    FATIGUE_THRESHOLD = 3 * 3600  # 改成3小时
    REMINDER_INTERVAL = 1800      # 改成30分钟间隔
    IDLE_THRESHOLD = 600          # 改成10分钟闲置
```

### 修改UI颜色和字体

编辑 `ui/component/fatigue_reminder_dialog.py`，查找 `setStyleSheet()` 方法。

### 添加自定义建议

编辑 `ui/component/fatigue_reminder.py` 的 `_get_rest_suggestions()` 方法。

## 📚 深入了解

- 详细文档：[FATIGUE_REMINDER_GUIDE.md](FATIGUE_REMINDER_GUIDE.md)
- 源码注释：每个函数都有详细的中文文档字符串
- 测试脚本：`test_fatigue_reminder.py`

## 🐛 故障排查

### 提醒没有显示？

1. 确认工作状态
   ```python
   # 在主程序中添加调试
   print(f"工作状态: {reminder_logic.fatigue_reminder.is_working}")
   print(f"工作时长: {reminder_logic.fatigue_reminder.get_work_duration_formatted()}")
   ```

2. 检查事件流
   - `on_status_update()` 被调用了吗？
   - `mark_activity()` 被调用了吗？

3. 查看日志
   ```
   [FATIGUE_REMINDER] 显示疲惫提醒: 5小时0分钟
   ```

### 提醒频率太高？

修改 `REMINDER_INTERVAL`：
```python
REMINDER_INTERVAL = 7200  # 改成2小时
```

### 想完全禁用提醒？

注释掉 `reminder_logic.py` 中的这一行：
```python
# self.fatigue_reminder.fatigue_reminder_triggered.connect(self._on_fatigue_reminder_triggered)
```

## 📱 集成到你的工作流

系统已自动集成，会在以下场景触发：

✅ 用户进行工作/专注活动
✅ 键盘或鼠标有活动
✅ 连续工作超过5小时
✅ 5小时、6小时、7小时分别有提醒

## 💡 小技巧

1. **快速测试**：将 `FATIGUE_THRESHOLD` 改成60秒（1分钟）
2. **调整间隔**：修改 `REMINDER_INTERVAL` 控制提醒频率
3. **自定义建议**：添加你自己的休息方式建议
4. **记录数据**：在回调函数中添加数据库操作

## 🎓 下一步

- 阅读 [FATIGUE_REMINDER_GUIDE.md](FATIGUE_REMINDER_GUIDE.md) 了解更多细节
- 尝试 `python test_fatigue_reminder.py ui` 看UI演示
- 修改配置满足你的需求
- 添加数据持久化保存用户数据

---

**享受更健康的工作习惯！** 🎉

💪 记住：规律的休息是提高工作效率的关键！
