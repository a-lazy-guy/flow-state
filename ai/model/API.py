"""
专注力提升APP - 主程序
完整的API服务器，无依赖问题
"""

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from functools import wraps
import jwt
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import os
import re
import time
import platform
import subprocess
from dataclasses import dataclass, asdict

app = Flask(__name__)
CORS(app)

# ==================== 配置 ====================

class Config:
    """API配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
    DATABASE_PATH = 'focus_app.db'
    TOKEN_EXPIRATION_HOURS = 24
    API_VERSION = 'v1'
    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = True
    
app.config.from_object(Config)


# ==================== 数据模型 ====================

@dataclass
class MouseData:
    move_count: int = 0
    click_count: int = 0
    scroll_count: int = 0
    idle_time: float = 0
    move_distance: float = 0
    average_speed: float = 0
    click_interval: float = 0
    focused_area: str = ""


@dataclass
class KeyboardData:
    key_press_count: int = 0
    words_per_minute: float = 0
    typing_interval: float = 0
    backspace_rate: float = 0
    shortcut_usage: int = 0
    typing_rhythm: float = 0


@dataclass
class PageData:
    url: str = ""
    title:  str = ""
    content: str = ""
    app_name: str = ""
    domain: str = ""


@dataclass
class TimeData:
    session_duration: float = 0
    active_time: float = 0
    idle_time: float = 0
    time_of_day: int = 0
    day_of_week: int = 0
    consecutive_sessions: int = 0


@dataclass
class VideoLearningSignals:
    """视频学习信号"""
    is_video_playing: bool = False
    video_duration:  float = 0
    current_time: float = 0
    is_fullscreen: bool = False
    playback_speed: float = 1.0
    has_subtitles: bool = False
    has_paused: bool = False
    pause_frequency:  int = 0
    rewind_count: int = 0
    note_taking_detected: bool = False


@dataclass
class PageContentDetail:
    """页面内容详细信息"""
    window_title: str = ""
    app_name: str = ""
    url: str = ""
    domain: str = ""
    content_type: str = ""
    metadata: Dict = None
    video_signals: Optional[VideoLearningSignals] = None


# ==================== 数据库管理 ====================

class DatabaseManager:
    """数据库管理器"""
    
    @staticmethod
    def get_db():
        """获取数据库连接"""
        if 'db' not in g: 
            g.db = sqlite3.connect(
                Config.DATABASE_PATH,
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.db.row_factory = sqlite3.Row
        return g.db
    
    @staticmethod
    def close_db(e=None):
        """关闭数据库连接"""
        db = g.pop('db', None)
        if db is not None:
            db.close()
    
    @staticmethod
    def init_db():
        """初始化数据库"""
        db = sqlite3.connect(Config.DATABASE_PATH)
        cursor = db.cursor()
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                settings TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        db.commit()
        db.close()

# 初始化数据库
if not os.path.exists(Config.DATABASE_PATH):
    DatabaseManager.init_db()

@app.teardown_appcontext
def teardown_db(exception):
    DatabaseManager.close_db(exception)


# ==================== 运行时状态 ====================

_runtime_state = {
    'current_status': None,
    'status_started_at': None,
    'durations': {}
}


# ==================== 分析逻辑 ====================

def _classify_status(monitor_data: Dict) -> str:
    """
    根据画面变化率判断状态
    
    阈值说明 (基于 ScreenAnalyzer/CameraAnalyzer 的输出 0.0-1.0):
    - 高动态 (> 5%): 判定为 'entertainment' (视频、游戏、大幅动作)
    - 中动态 (> 2%): 判定为 'work' (滚动页面、正常操作)
    - 低动态/静止: 判定为 'focus' (极少动作，专注状态)
    """
    change = float(monitor_data.get('screen_change_rate', 0.0) or 0.0)
    
    if change > 0.05:
        status = 'entertainment'  # 高动态，视为非专注/娱乐/休息
    elif change > 0.02:
        status = 'work'           # 中动态，视为正常工作
    else:
        status = 'focus'          # 低动态，视为深度专注
    
    print(f"[API] 画面变化率: {change:.4f} -> 判定状态: {status}")
    return status

def _status_message(status: str) -> str:
    return {
        'entertainment': '检测到大幅动作或高动态画面，可能在休息或娱乐。',
        'work': '检测到正常活动，正在工作中。',
        'focus': '画面基本静止，深度专注中。',
    }.get(status, '状态未知。')

def get_analysis(monitor_data: Dict) -> Dict:
    """供项目调用的轻量分析函数。
    输入: monitor_data = {key_presses, mouse_clicks, screen_change_rate, is_complex_scene}
    输出: {status, duration, message}
    """
    now = time.time()
    status = _classify_status(monitor_data)

    # 切换状态时重置起点
    if _runtime_state['current_status'] != status:
        _runtime_state['current_status'] = status
        _runtime_state['status_started_at'] = now

    # 更新持续时长
    started = _runtime_state['status_started_at'] or now
    duration = now - started
    _runtime_state['durations'][status] = duration

    return {
        'status': status,
        'duration': int(duration),
        'message': _status_message(status)
    }


# ==================== 认证中间件 ====================

def token_required(f):
    """Token验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({
                    'success': False,
                    'error': 'Token格式错误'
                }), 401
        
        if not token: 
            return jsonify({
                'success': False,
                'error': '缺少认证Token'
            }), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
            
            db = DatabaseManager.get_db()
            cursor = db.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ? ', (current_user_id,))
            user = cursor.fetchone()
            
            if not user:
                return jsonify({
                    'success': False,
                    'error': '用户不存在'
                }), 401
            
            g.current_user_id = current_user_id
            
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'error': 'Token已过期'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'error':  '无效的Token'
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated


# ==================== API路由 ====================

@app.route(f'/api/{Config.API_VERSION}/auth/register', methods=['POST'])
def register():
    """用户注册"""
    try: 
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email', '')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'error': '用户名和密码不能为空'
            }), 400
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        default_settings = {
            'doNotDisturb': False,
            'enableAllReminders': True,
            'workGoal': 8,
            'learningGoal': 2,
            'breakInterval': 25,
            'notificationSound': True
        }
        
        db = DatabaseManager.get_db()
        cursor = db.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO users (username, password_hash, email, settings) VALUES (?, ?, ?, ?)',
                (username, password_hash, email, json.dumps(default_settings))
            )
            db.commit()
            user_id = cursor.lastrowid
            
            return jsonify({
                'success':  True,
                'message': '注册成功',
                'user_id': user_id
            }), 201
            
        except sqlite3.IntegrityError:
            return jsonify({
                'success':  False,
                'error': '用户名已存在'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success':  False,
            'error': str(e)
        }), 500


@app.route(f'/api/{Config.API_VERSION}/auth/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'error': '用户名和密码不能为空'
            }), 400
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        db = DatabaseManager.get_db()
        cursor = db.cursor()
        cursor.execute(
            'SELECT id, username FROM users WHERE username = ? AND password_hash = ?',
            (username, password_hash)
        )
        user = cursor.fetchone()
        
        if not user:
            return jsonify({
                'success': False,
                'error': '用户名或密码错误'
            }), 401
        
        token = jwt.encode({
            'user_id': user['id'],
            'username': user['username'],
            'exp': datetime.utcnow() + timedelta(hours=Config.TOKEN_EXPIRATION_HOURS)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'success': True,
            'token': token,
            'user':  {
                'id': user['id'],
                'username': user['username']
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success':  False,
            'error': str(e)
        }), 500

# 占位符：页面识别和视频质量分析
# 如果需要完整功能，需要恢复 PageRecognizer 类和相关逻辑
# 这里提供最小实现以防报错

@app.route(f'/api/{Config.API_VERSION}/page/recognize', methods=['POST'])
@token_required
def recognize_current_page():
    return jsonify({'success': True, 'message': 'Not implemented yet'}), 200

@app.route(f'/api/{Config.API_VERSION}/video/learning-quality', methods=['POST'])
@token_required
def analyze_video_learning_quality():
    return jsonify({'success': True, 'message': 'Not implemented yet'}), 200

if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
