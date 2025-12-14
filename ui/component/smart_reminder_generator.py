# -*- coding: utf-8 -*-
"""智能提醒消息生成器"""

class SmartReminderGenerator:
    """智能提醒消息生成器"""
    
    def __init__(self):
        self.messages = {
            'low': [
                "你已经看了一会儿视频啦～",
                "是不是感觉有点累了？",
                "不如休息一下眼睛？"
            ],
            'medium': [
                "稍微缓一缓～你已经看了这么久了",
                "不如休息一下，喝杯水吧 ☕",
                "站起来活动活动肩膀～"
            ],
            'high': [
                "你已经看太久了！该休息了！",
                "现在就站起来活动一下吧！",
                "保护好眼睛，该休息了！"
            ]
        }
    
    def calculate_severity(self, status: str, duration: int, threshold: int = 30) -> str:
        """计算提醒严重级别
        
        Args:
            status: 当前状态
            duration: 持续时间(分钟)
            threshold: 阈值(分钟)
        
        Returns:
            'low', 'medium', 或 'high'
        """
        if status != 'entertainment':
            return 'low'
        
        ratio = duration / threshold
        
        if ratio < 1.0:
            return 'low'
        elif ratio < 1.5:
            return 'medium'
        else:
            return 'high'
    
    def generate_message(self, status: str, duration: int, threshold: int = 30) -> str:
        """生成提醒消息"""
        severity = self.calculate_severity(status, duration, threshold)
        messages = self.messages.get(severity, self.messages['low'])
        return messages[0] if messages else "该休息了～"
    
    def generate_reminder(self, severity: str) -> dict:
        """生成完整的提醒对象
        
        Args:
            severity: 严重级别 ('low', 'medium', 'high')
        
        Returns:
            包含message, icon, encouragement的字典
        """
        messages = self.messages.get(severity, self.messages['low'])
        message = messages[0] if messages else "该休息了～"
        
        icons = {
            'low': '🎬',
            'medium': '⏱️',
            'high': '⚠️'
        }
        
        encouragements = {
            'low': '站起来活动活动吧～',
            'medium': '做个简单的拉伸运动～',
            'high': '立刻停下来休息！'
        }
        
        return {
            'message': message,
            'icon': icons.get(severity, '🎬'),
            'encouragement': encouragements.get(severity, '去休息一下～')
        }
