# -*- coding: utf-8 -*-
"""
[正在使用]
活动历史管理器 (业务逻辑层)
负责管理活动状态的流转和记录。
通过 DAO 层与数据库交互。
"""

import time
import sys
import os

# 添加项目根目录到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from datetime import date, datetime
from app.data.dao.activity_dao import ActivityDAO, StatsDAO, WindowSessionDAO
import json

class ActivityHistoryManager:
    """活动历史管理器"""
    
    # 全局当前模式变量
    _current_mode = "focus"  # 默认专注模式
    
    @classmethod
    def set_current_mode(cls, mode):
        """设置当前模式"""
        cls._current_mode = mode
    
    @classmethod
    def get_current_mode(cls):
        """获取当前模式"""
        return cls._current_mode
    
    def __init__(self):
        self.current_status = None
        self.status_start_time = None
        self._last_summary = None
        self._last_raw_data = None
        
        # 记录当前连续专注时长 (秒)
        self._current_focus_streak_seconds = 0
        
        # 意志力胜利检测状态: 记录进入当前状态前，是否处于 Focus 状态
        self._last_status_was_focus = False
        
        # 新增：记录上一个窗口会话的信息，用于合并
        self._last_window_session = {
            'id': None,
            'title': None,
            'process': None
        }
        
        # 内存缓存，用于快速 UI 展示
        self._history_cache = [] 
    
    def update(self, status: str, summary: str = None, raw_data: str = None):
        """更新当前状态"""
        current_time = time.time()
        
        # 首次运行
        if self.current_status is None:
            self.current_status = status
            self.status_start_time = current_time
            return

        # 状态改变，保存历史
        if status != self.current_status:
            duration_seconds = int(current_time - self.status_start_time)
            # 过滤短时抖动
            if duration_seconds > 2:
                # 检测意志力胜利 (从 Entertainment 切回 Focus)
                willpower_win_increment = 0
                if self.current_status == 'entertainment' and status in ['focus', 'work']:
                    if self._last_status_was_focus and 5 < duration_seconds < 300:
                        willpower_win_increment = 1
                
                self._save_record(self.current_status, duration_seconds, self._last_summary, self._last_raw_data, willpower_wins_increment=willpower_win_increment)
                self._update_cache(self.current_status, int(duration_seconds / 60), self.status_start_time)
            
            # 更新状态追踪 (为下一段做准备)
            if self.current_status in ['focus', 'work']:
                self._last_status_was_focus = True
            else:
                self._last_status_was_focus = False
                
            self.current_status = status
            self.status_start_time = current_time
            # 重置缓存的摘要
            self._last_summary = summary 
            self._last_raw_data = raw_data
            
            # 如果新状态直接带有详细信息（AI分析结果），立即保存一条快照，避免数据积压在内存
            if raw_data:
                 # 这里时长设为 0 或者当前已持续时间，视需求而定。
                 # 为了简单，我们让它作为一条"即时记录"被看到，但要注意不要和上面的 _save_record 重复统计时长
                 # 策略：更新 status_start_time，相当于开启了一段新记录
                 pass

        else:
            # 状态没变
            # 关键修改：如果收到了 raw_data (说明是 AI 分析结果)，强制保存当前这一段，并开启新的一段
            # 这样可以确保 AI 分析结果立即写入数据库，而不是等状态改变
            if raw_data:
                duration_seconds = int(current_time - self.status_start_time)
                # 即使时间很短，只要有 AI 分析结果，也值得保存
                if duration_seconds > 0:
                     self._save_record(self.current_status, duration_seconds, summary, raw_data)
                     self._update_cache(self.current_status, int(duration_seconds / 60), self.status_start_time)
                
                # 重置开始时间，相当于无缝开启下一段同状态的记录
                self.status_start_time = current_time
                self._last_summary = summary
                self._last_raw_data = raw_data
            
            else:
                # 只是普通的心跳更新，更新缓存即可
                if summary:
                    self._last_summary = summary
                if raw_data:
                    self._last_raw_data = raw_data
    
    def _save_record(self, status: str, duration: int, summary: str = None, raw_data: str = None, willpower_wins_increment: int = 0):
        """调用 DAO 保存数据 (自动处理跨日分割)"""
        current_ts = time.time()
        start_ts = current_ts - duration
        
        start_dt = datetime.fromtimestamp(start_ts)
        end_dt = datetime.fromtimestamp(current_ts)
        
        # 检查是否跨越午夜
        if start_dt.date() != end_dt.date():
            # 跨日：分割为两段
            print(f"[HistoryManager] Midnight crossing detected: {start_dt} -> {end_dt}")
            
            # 1. 计算第一段（昨天）的时长
            # 午夜时间戳
            midnight = datetime.combine(end_dt.date(), datetime.min.time())
            midnight_ts = midnight.timestamp()
            
            dur_prev = int(midnight_ts - start_ts)
            if dur_prev > 0:
                # 保存第一段
                self._do_save(status, dur_prev, summary, raw_data, 0, 
                              record_date=start_dt.date(), 
                              session_end_ts=midnight_ts)
                
            # 2. 强制切断会话上下文，确保下一段创建新会话
            self._last_window_session = {
                'id': None,
                'title': None,
                'process': None
            }
            
            # 3. 计算第二段（今天）的时长
            dur_curr = duration - dur_prev
            if dur_curr > 0:
                # 保存第二段，并将意志力胜利归属到这一段（结束时刻）
                self._do_save(status, dur_curr, summary, raw_data, willpower_wins_increment, 
                              record_date=end_dt.date(), 
                              session_end_ts=current_ts)
        else:
            # 未跨日：直接保存
            self._do_save(status, duration, summary, raw_data, willpower_wins_increment,
                          record_date=end_dt.date(),
                          session_end_ts=current_ts)

    def _do_save(self, status: str, duration: int, summary: str = None, raw_data: str = None, 
                 willpower_wins_increment: int = 0, record_date=None, session_end_ts=None):
        """实际执行 DAO 保存逻辑"""
        try:
            if record_date is None:
                record_date = date.today()
            if session_end_ts is None:
                session_end_ts = time.time()

            # 1. 写入流水日志
            # 使用 session_end_ts 作为记录时间点
            timestamp_str = datetime.fromtimestamp(session_end_ts).strftime("%Y-%m-%d %H:%M:%S")
            ActivityDAO.insert_log(status, duration, timestamp=timestamp_str, summary=summary, raw_data=raw_data)
            
            # 2. 计算连续专注时长
            if status in ['focus', 'work']:
                self._current_focus_streak_seconds += duration
            else:
                self._current_focus_streak_seconds = 0
            
            # 3. 更新每日统计 (传入当前连续时长)
            # 使用传入的 record_date 确保统计到正确的日期
            stats_status = status
            if self.get_current_mode() == "recharge":
                stats_status = "entertainment"

            StatsDAO.update_daily_stats(record_date, stats_status, duration, self._current_focus_streak_seconds, willpower_wins_increment)
            
            # 4. 更新或创建窗口会话聚合记录 (Window Sessions)
            if raw_data:
                try:
                    rd = json.loads(raw_data)
                    window_title = rd.get('window', '')
                    process_name = rd.get('process', '')
                    
                    if self._last_window_session['id'] is None:
                        last_sess = WindowSessionDAO.get_last_session()
                        if last_sess:
                            self._last_window_session = {
                                'id': last_sess['id'],
                                'title': last_sess['window_title'],
                                'process': last_sess['process_name']
                            }
                    
                    is_same_session = (
                        self._last_window_session['id'] is not None and
                        window_title == self._last_window_session['title']
                    )
                    
                    session_status = status
                    if self.get_current_mode() == "recharge":
                        session_status = "entertainment"
                    
                    if is_same_session:
                        # 是同一个会话，更新时长
                        # 传入 explicit end_timestamp
                        WindowSessionDAO.update_session_duration(self._last_window_session['id'], duration, end_timestamp=session_end_ts)
                        
                        if summary and summary != window_title:
                            WindowSessionDAO.update_session_summary(self._last_window_session['id'], summary)
                    else:
                        # 是新会话，创建新记录
                        # start_time = end_ts - duration
                        start_ts = session_end_ts - duration
                        
                        WindowSessionDAO.create_session(
                            window_title, process_name, start_ts, duration, session_status, summary
                        )
                        
                        new_sess = WindowSessionDAO.get_last_session()
                        if new_sess:
                            self._last_window_session = {
                                'id': new_sess['id'],
                                'title': new_sess['window_title'],
                                'process': new_sess['process_name']
                            }
                            
                except Exception as e:
                    print(f"[HistoryManager] Session Merge Error: {e}")
                    
        except Exception as e:
            print(f"[HistoryManager] DB Error: {e}")

    def _update_cache(self, status, duration_mins, timestamp):
        self._history_cache.append({
            'status': status,
            'duration': duration_mins,
            'timestamp': timestamp
        })
        if len(self._history_cache) > 10:
            self._history_cache = self._history_cache[-10:]

    def add_ocr_record(self, content: str, app_name: str, screenshot_path: str = None):
        """添加 OCR 记录"""
        pass
        # try:
        #     OcrDAO.insert_record(content, app_name, screenshot_path)
        # except Exception as e:
        #     print(f"[HistoryManager] OCR DB Error: {e}")

    def get_current_duration(self) -> int:
        if self.status_start_time is None:
            return 0
        return int((time.time() - self.status_start_time) / 60)
    
    def get_history(self) -> list:
        return self._history_cache
    
    def get_formatted_history(self, limit: int = 5) -> list:
        formatted = []
        for record in self._history_cache[-limit:]:
            status = record['status']
            duration = record['duration']
            desc = f"{status} - {duration}分钟"
            formatted.append((status, duration, desc))
        return formatted
    
    def get_daily_logs(self, day: date = None):
        """获取某日的详细活动日志"""
        if day is None:
            day = date.today()
        try:
            return ActivityDAO.get_logs_by_date(day)
        except Exception as e:
            print(f"[HistoryManager] Logs Error: {e}")
            return []

    def get_daily_summary(self, day: date = None):
        """获取统计摘要"""
        if day is None:
            day = date.today()
        
        try:
            data = StatsDAO.get_daily_summary(day)
            if data:
                return data
        except Exception as e:
            print(f"[HistoryManager] Summary Error: {e}")
        
        return {
            'total_focus_time': 0,
            'total_work_time': 0,
            'total_entertainment_time': 0,
            'pull_back_count': 0
        }

    # 兼容旧逻辑
    def get_reminder_interval(self, duration: int, threshold: int = 30) -> int:
        if duration < threshold: return 999999
        excess = duration - threshold
        if excess < 5: return 300
        elif excess < 15: return 180
        else: return 120
    
    def should_remind(self, threshold: int = 30) -> bool:
        if self.current_status != 'entertainment': return False
        return self.get_current_duration() >= threshold
