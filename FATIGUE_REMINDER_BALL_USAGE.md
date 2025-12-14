# 疲惫提醒浮球模块使用指南

## 模块概述

`float_ball.py` 已被改造为 **疲惫提醒浮球模块** (`FatigueReminderBall`)，它是一个悬浮窗口组件，用于显示工作状态和疲惫提醒。

## 主要功能

### 1. **工作状态追踪**
- 自动追踪用户工作时间
- 支持工作会话的自动暂停和恢复
- 5分钟无活动自动判定为暂停状态

### 2. **状态指示**
通过颜色变化直观显示工作状态：
- 🔵 **蓝色** (IDLE): 闲置状态
- 🟢 **绿色** (WORKING): 工作中 (<5小时)
- 🟠 **橙色** (FATIGUED): 疲惫 (5-7小时)
- 🔴 **红色** (EXHAUSTED): 极度疲惫 (7小时+)

### 3. **疲惫提醒**
- 工作5小时后触发第一次提醒
- 之后每30分钟提醒一次
- 发送包含工作时长信息的信号

### 4. **交互功能**
- 拖动浮球重新定位
- 点击触发 `touched` 信号（可连接到提醒对话框）
- 鼠标悬停时显示/隐藏边框

### 5. **呼吸灯效果**
- 实时呼吸灯动画表示活跃状态
- 增强视觉反馈

## 使用示例

### 基本初始化

```python
from ui.component.float_ball import FatigueReminderBall

# 创建浮球实例
ball = FatigueReminderBall(size=64)
ball.show()

# 连接信号
ball.fatigue_reminder_triggered.connect(on_fatigue_reminder)
ball.touched.connect(on_ball_clicked)
```

### 处理用户活动

```python
def on_key_press():
    """当用户按键时调用"""
    ball.mark_activity(activity_type="keypress")

def on_mouse_click():
    """当用户点击鼠标时调用"""
    ball.mark_activity(activity_type="click")
```

### 处理疲惫提醒

```python
def on_fatigue_reminder(reminder_data):
    """处理疲惫提醒"""
    work_duration = reminder_data['work_duration_formatted']
    print(f"您已工作{work_duration}，请休息一下！")
    # 可以显示提醒对话框等操作
```

### 获取工作时长

```python
# 获取当前工作时长（秒）
duration_seconds = ball.get_work_duration()

# 获取格式化的工作时长
duration_str = ball.get_work_duration_formatted()
print(f"当前工作时长: {duration_str}")
```

### 重置工作会话

```python
# 重置所有工作时间统计
ball.reset_work_session()
```

## API 参考

### 构造函数
```python
FatigueReminderBall(size=64)
```
- `size` (int): 浮球直径，默认64像素

### 主要方法

| 方法 | 说明 |
|------|------|
| `mark_activity(activity_type="input")` | 标记用户活动，启动或恢复工作计时 |
| `get_work_duration()` | 返回当前工作时长（秒） |
| `get_work_duration_formatted()` | 返回格式化的工作时长（如 "5小时30分钟"） |
| `check_fatigue_reminder()` | 检查是否应该触发提醒，返回提醒数据或None |
| `reset_work_session()` | 重置工作会话 |
| `checkIdleAndUpdate()` | 检查闲置状态并更新（自动调用） |

### 信号

| 信号 | 参数 | 说明 |
|------|------|------|
| `touched` | 无 | 用户点击浮球时发出 |
| `entered` | 无 | 鼠标进入浮球时发出 |
| `left` | 无 | 鼠标离开浮球时发出 |
| `positionChanged` | `QtCore.QPoint` | 浮球位置改变时发出 |
| `fatigue_reminder_triggered` | `dict` | 疲惫提醒触发时发出 |

## 提醒触发时机

提醒会在以下工作时长时触发：
- **22分钟**: 第一次提醒
- **35分钟**: 第二次提醒  
- **50分钟**: 第三次提醒

可以通过修改 `reminder_times` 列表来自定义触发时间：

```python
# 自定义提醒时间
ball.reminder_times = [15*60, 30*60, 45*60]  # 15分钟、30分钟、45分钟
```

## 状态转换图

```
[IDLE] ←→ [WORKING] ←→ [FATIGUED] ←→ [EXHAUSTED]
  (<22分钟)  (22-35分钟)  (35-50分钟)  (50分钟+)
  ↑                                      ↓
  +──────────────────────────────────────+
        （重置或长时间无活动）
```

## 集成建议

1. **键盘监听**: 全局监听键盘事件，调用 `mark_activity()`
2. **鼠标监听**: 全局监听鼠标事件，调用 `mark_activity()`
3. **通知系统**: 连接 `fatigue_reminder_triggered` 信号到通知系统
4. **数据持久化**: 定期保存 `get_work_duration()` 的结果到数据库
5. **提醒对话框**: 连接 `touched` 信号到疲惫提醒对话框

## 向后兼容性

为了保持与现有代码的兼容性，保留了 `TaijiBall` 类名别名：

```python
from ui.component.float_ball import TaijiBall
# TaijiBall 现在指向 FatigueReminderBall
```

## 注意事项

- 浮球自动定位在屏幕右下角
- 呼吸灯动画每50ms更新一次
- 闲置检查每1秒进行一次
- 所有时间都使用 Unix 时间戳（秒）
