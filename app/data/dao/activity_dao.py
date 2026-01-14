from app.data import get_db_connection

class ActivityDAO:
    """»î¶¯ÈÕÖ¾Êı¾İ·ÃÎÊ¶ÔÏó"""
    
    @staticmethod
    def insert_log(status: str, duration: int):
        with get_db_connection() as conn:
            conn.execute(
                'INSERT INTO activity_logs (status, duration) VALUES (?, ?)',
                (status, duration)
            )
            conn.commit()

    @staticmethod
    def get_logs_by_date(date_obj):
        """è·å–æŸæ—¥çš„æ‰€æœ‰æ´»åŠ¨æ—¥å¿—"""
        start_time = f"{date_obj} 00:00:00"
        end_time = f"{date_obj} 23:59:59"
        with get_db_connection() as conn:
            rows = conn.execute(
                'SELECT * FROM activity_logs WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp ASC',
                (start_time, end_time)
            ).fetchall()
            return [dict(row) for row in rows]


class StatsDAO:
    """Í³¼ÆÊı¾İ·ÃÎÊ¶ÔÏó"""
    
    @staticmethod
    def update_daily_stats(date_obj, status: str, duration: int):
        """ÔöÁ¿¸üĞÂÃ¿ÈÕÍ³¼Æ"""
        col_name = f"total_{status}_time"
        # ½ö´¦ÀíÓĞĞ§×´Ì¬×Ö¶Î
        if status not in ['focus', 'work', 'entertainment']:
            return

        with get_db_connection() as conn:
            # Upsert (Insert or Update)
            conn.execute(f'''
                INSERT INTO daily_stats (date, {col_name}) 
                VALUES (?, ?)
                ON CONFLICT(date) DO UPDATE SET 
                {col_name} = {col_name} + ?
            ''', (date_obj, duration, duration))
            conn.commit()

    @staticmethod
    def get_daily_summary(date_obj):
        """»ñÈ¡Ä³ÈÕµÄÍ³¼ÆÊı¾İ"""
        with get_db_connection() as conn:
            row = conn.execute(
                'SELECT * FROM daily_stats WHERE date = ?', (date_obj,)
            ).fetchone()
            if row:
                return dict(row)
        return None

class OcrDAO:
    """OCR ¼ÇÂ¼Êı¾İ·ÃÎÊ¶ÔÏó"""
    
    @staticmethod
    def insert_record(content: str, app_name: str, screenshot_path: str = None):
        with get_db_connection() as conn:
            conn.execute(
                'INSERT INTO ocr_records (content, app_name, screenshot_path) VALUES (?, ?, ?)',
                (content, app_name, screenshot_path)
            )
            conn.commit()

    @staticmethod
    def get_recent_records(limit=50):
        """»ñÈ¡×î½üµÄ OCR/ä¯ÀÀ¼ÇÂ¼"""
        with get_db_connection() as conn:
            rows = conn.execute(
                'SELECT id, timestamp, app_name, window_title, content FROM ocr_records ORDER BY timestamp DESC LIMIT ?',
                (limit,)
            ).fetchall()
            return [dict(row) for row in rows]
