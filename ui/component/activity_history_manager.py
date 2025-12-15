# -*- coding: utf-8 -*-
"""活动历史管理器"""

import time

class ActivityHistoryManager:
    """活动历史管理器"""
    
    def __init__(self):
        self.history = []
        self.current_status = None
        self.status_start_time = None
    
    def update(self, status: str):
        """更新当前状态"""
        current_time = time.time()
        
        # 如果状态改变，保存前一个状态的历史
        if status != self.current_status:
            if self.current_status is not None:
                duration = int((current_time - self.status_start_time) / 60)
                self.history.append({
                    'status': self.current_status,
                    'duration': duration,
                    'timestamp': self.status_start_time
                })
                # 保持最近10条记录
                if len(self.history) > 10:
                    self.history = self.history[-10:]
            
            self.current_status = status
            self.status_start_time = current_time
    
    def get_current_duration(self) -> int:
        """获取当前状态持续时间（分钟）"""
        if self.status_start_time is None:
            return 0
        return int((time.time() - self.status_start_time) / 60)
    
    def get_history(self) -> list:
        """获取历史记录"""
        return self.history
    
    def get_formatted_history(self, limit: int = 5) -> list:
        """获取格式化的历史记录"""
        formatted = []
        for record in self.history[-limit:]:
            status = record['status']
            duration = record['duration']
            desc = f"{status} - {duration}分钟"
            formatted.append((status, duration, desc))
        return formatted
    
    def get_reminder_interval(self, duration: int, threshold: int = 30) -> int:
        """获取提醒间隔（秒）"""
        if duration < threshold:
            return 999999  # 不提醒
        
        excess = duration - threshold
        
        if excess < 5:
            return 300  # 5分钟
        elif excess < 15:
            return 180  # 3分钟
        else:
            return 120  # 2分钟
    
    def should_remind(self, threshold: int = 30) -> bool:
        """判断是否应该提醒"""
        if self.current_status != 'entertainment':
            return False
        
        duration = self.get_current_duration()
        return duration >= threshold
