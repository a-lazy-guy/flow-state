import sqlite3
import json
from datetime import datetime, timedelta

def backfill_summaries(target_date):
    """
    回填指定日期的 Window Sessions 摘要
    逻辑：从 activity_logs 中查找对应时间段的 AI 摘要，更新到 window_sessions
    """
    db_path = 'focus_app.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print(f"开始回填 {target_date} 的摘要...")
    
    # 1. 获取当天的所有 Sessions
    start_of_day = f"{target_date} 00:00:00"
    end_of_day = f"{target_date} 23:59:59"
    
    cursor.execute('''
        SELECT id, start_time, end_time, window_title, summary 
        FROM window_sessions 
        WHERE start_time BETWEEN ? AND ?
    ''', (start_of_day, end_of_day))
    
    sessions = cursor.fetchall()
    print(f"找到 {len(sessions)} 条 Session 记录。")
    
    updated_count = 0
    
    for sess in sessions:
        sess_id = sess['id']
        start_time = sess['start_time']
        end_time = sess['end_time']
        original_summary = sess['summary']
        window_title = sess['window_title']
        
        # 2. 在 Logs 中查找对应时间段的记录
        # 稍微放宽一点时间范围，因为 Log 可能比 Session 晚几秒写入
        # 但主要还是找这个 Session 范围内的
        
        cursor.execute('''
            SELECT summary, raw_data 
            FROM activity_logs 
            WHERE timestamp BETWEEN ? AND ?
            AND summary IS NOT NULL 
            AND summary != ''
            ORDER BY timestamp ASC
        ''', (start_time, end_time))
        
        logs = cursor.fetchall()
        
        best_summary = None
        
        for log in logs:
            log_summary = log['summary']
            
            # 过滤掉无效摘要
            if not log_summary:
                continue
            if log_summary == window_title:
                continue
            if log_summary == "No Title":
                continue
                
            # 找到了一个看起来不错的摘要
            best_summary = log_summary
            # 只要找到一个，就认为是最好的（通常第一条 AI 分析就是最准的）
            break
            
        if best_summary and best_summary != original_summary:
            print(f"[更新 ID {sess_id}]")
            print(f"  原: {original_summary[:30]}...")
            print(f"  新: {best_summary[:30]}...")
            
            cursor.execute('''
                UPDATE window_sessions 
                SET summary = ? 
                WHERE id = ?
            ''', (best_summary, sess_id))
            updated_count += 1
            
    conn.commit()
    conn.close()
    print(f"完成！共更新了 {updated_count} 条记录。")

if __name__ == "__main__":
    # 设置为昨天
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    # 或者指定日期
    # yesterday = "2026-01-20" 
    backfill_summaries(yesterday)
