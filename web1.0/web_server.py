# -*- coding: utf-8 -*-
import os
import multiprocessing
from flask import Flask, render_template, jsonify, request, send_from_directory, make_response
from flask_cors import CORS
import time

def create_app():
    # Get absolute paths for templates and static
    # Assuming this file is in app/web/ or app/services/
    # If in app/web/, dirname is app/web, dirname again is app.
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(base_dir, 'web', 'templates')
    static_dir = os.path.join(base_dir, 'web', 'static')

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    CORS(app) 

    @app.route('/')
    def index():
        # Robust file reading: Try UTF-8 first, fallback to GBK/GB18030 for Windows compatibility
        path = os.path.join(template_dir, 'index.html')
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(path, 'r', encoding='gb18030') as f:
                    content = f.read()
            except Exception as e:
                return f"Error loading template (encoding failure): {str(e)}", 500
        except Exception as e:
            return f"Error loading template: {str(e)}", 500
            
        return content

    @app.route('/api/health')
    def health_check():
        return jsonify({'status': 'ok', 'message': 'Flow State Web Server is running'})
    
    # API: Get History
    @app.route('/api/history')
    def get_history():
        # TODO: Call app.data.dao to read SQLite
        return jsonify({"date": "2026-01-13", "focus_time": 120})

    @app.route('/api/history/recent')
    def get_recent_history():
        days = request.args.get('days', default=7, type=int)
        try:
            # Try to import DAO, handle if not available
            try:
                from app.data.dao.activity_dao import OcrDAO
                records = OcrDAO.get_recent_records(limit=50)
            except ImportError:
                print("DAO Import failed, using mock data")
                records = []
            except Exception as e:
                print(f"DAO Error: {e}")
                records = []
            
            # Mock data generation if DB is empty
            if not records:
                import datetime
                import random
                base_time = datetime.datetime.now()
                records = []
                apps = ['Chrome', 'VS Code', 'WeChat', 'Word', 'Edge']
                titles = ['Flow State Project - Design', 'app.py - flow-state', 'Team Chat', 'Requirements.docx', 'Stack Overflow - Python Flask']
                
                # Generate more data if requesting 30 days
                count = 50 if days > 7 else 15
                
                for i in range(count):
                    # Spread mock data over the requested period
                    delta_days = random.randint(0, days - 1)
                    delta_mins = random.randint(0, 1440)
                    timestamp = base_time - datetime.timedelta(days=delta_days, minutes=delta_mins)
                    
                    records.append({
                        'id': i,
                        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        'app_name': apps[i % len(apps)],
                        'window_title': titles[i % len(titles)],
                        'content': 'Simulated content for demo purposes...'
                    })
                
                # Sort by timestamp desc
                records.sort(key=lambda x: x['timestamp'], reverse=True)
                
            return jsonify(records)
        except Exception as e:
            print(f"Error fetching history: {e}")
            return jsonify([])

    # API: AI Generate Report
    @app.route('/api/generate_report', methods=['POST'])
    def generate_report():
        print("[Web] Calling AI model for report...")
        time.sleep(3) # Simulate AI thinking
        return jsonify({"report": "You focused for 2 hours today..."})

    @app.route('/api/stats/today')
    def get_today_stats():
        return jsonify({
            'total_productive_seconds': 3600,
            'total_entertainment': 1800
        })

    @app.route('/api/chat', methods=['POST'])
    def chat_api():
        try:
            print("[Web] Chat API called")
            data = request.json
            if not data:
                print("[Web] Chat API error: No JSON data")
                return jsonify({"error": "Invalid request, JSON required"}), 400
            
            user_message = data.get('message', '')
            print(f"[Web] User message: {user_message}")
            
            # Mock AI Response for now to fix the 404 error
            # In a real app, this would call app.service.detector.detector_logic.analyze or similar
            response_text = f"我收到了你的消息: '{user_message}'。\n\n(AI 服务目前为模拟状态，以防止网络错误。)"
            return jsonify({
                "response": response_text
            })
        except Exception as e:
            print(f"[Web] Chat API Exception: {e}")
            return jsonify({"error": str(e)}), 500

    return app

def run_server(port=8080):
    """
    Run Web Server
    """
    print(f"[Web Process] Started (PID: {multiprocessing.current_process().pid}) http://127.0.0.1:{port}")
    app = create_app()
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    run_server()