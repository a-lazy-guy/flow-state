import requests
import uuid
import json
from datetime import date, timedelta
from app.data.web_report.report_generator import ReportGenerator

# --- 配置区 ---
# API 1: 核心事件总结 (Event Summarizer)
API_KEY_1 = 'sk-Gwhx0iMED0qlkQS6Oxsuxo5DW192U-w28AM1JDEJsDk'
URL_1 = "http://localhost:7860/api/v1/run/09733a7e-ecf8-4771-b3fd-d4a367d67f57"

# API 2: 致奋斗者 (Encouragement)
API_KEY_2 = 'sk-kidtu9j5hqYnpV5rGD81xvNPjQsq5QUmI53HY6JHp0M'
URL_2 = "http://localhost:7860/api/v1/run/7886edbe-e56a-46b5-ae24-9103becf35f1"

def call_langflow_api(url, api_key, input_text):
    """通用的 LangFlow API 调用函数"""
    payload = {
        "output_type": "chat",
        "input_type": "chat",
        "input_value": input_text,
        "session_id": str(uuid.uuid4())
    }
    headers = {"x-api-key": api_key}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        # 尝试提取核心文本
        try:
            return data["outputs"][0]["outputs"][0]["results"]["message"]["text"]
        except (KeyError, IndexError):
            return data # 提取失败返回原始数据
    except Exception as e:
        print(f"API Call Failed: {e}")
        return None

def test_report_generation():
    print("🚀 开始测试报告生成流程...")
    
    # 1. 准备数据 (使用 ReportGenerator 的逻辑)
    # 我们只用它的数据获取部分，不直接生成报告
    generator = ReportGenerator()
    days = 3
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)
    
    print(f"📅 获取数据范围: {start_date} 至 {end_date}")
    data_context = generator._fetch_data(start_date, end_date)
    formatted = generator._process_data(data_context, days)
    
    # 2. 准备 "核心事件" 的 Prompts 并批量调用
    # 遍历每一天的日志
    core_items_result = {}
    print("\n🔍 开始生成每日核心事项...")
    
    for log in formatted["daily_logs_for_ai"]:
        # log 结构: {'date': '1月26日', 'top_app': 'Trae.exe', 'title': 'database.py', 'hours': 3.1}
        date_str = log['date']
        
        # 构造 Prompt
        prompt_event = f"""
Role: 你是一个极其敏锐的数据分析师。
Task: 请阅读以下用户在 {date_str} 的应用使用记录，总结出当天唯一的一个核心事项。
Data Context:
- Top App: {log['top_app']}
- Window Title: {log['title']}
- Duration: {log['hours']} 小时
Constraints:
- 输出必须少于 15 个字。
- 格式：[动词] [核心名词]
- 例如："重构后端代码"。
- 不要包含任何解释性文字，只输出结果。
"""
        print(f"  -> 正在处理 {date_str} ({log['title']})...")
        summary = call_langflow_api(URL_1, API_KEY_1, prompt_event)
        if summary:
            print(f"     ✅ AI总结: {summary}")
            core_items_result[date_str] = summary
        else:
            print("     ❌ 调用失败")

    # 3. 准备 "致奋斗者" 的 Prompt 并调用
    print("\n💌 开始生成致奋斗者寄语...")
    
    peak_info = formatted["peak_day_info"]
    peak_str = f"{peak_info.get('date_str', '无')} ({peak_info.get('hours', 0)}h)"
    
    prompt_encouragement = f"""
Role: 你是一个充满激情与同理心的高效能教练。
Task: 根据用户的专注数据，写一段“致奋斗者”的寄语。
Data Context:
- 专注总时长: {formatted['total_focus_hours']} 小时
- 意志力胜利: {formatted['willpower_wins']} 次 (意味着他战胜了诱惑)
- 巅峰时刻: {peak_str}
Style:
- 激昂、真诚、数据驱动。
- 必须引用上面的具体数字。
- 结尾要给人以力量。
- 字数控制在 100 字左右。
"""
    encouragement = call_langflow_api(URL_2, API_KEY_2, prompt_encouragement)
    print(f"📝 AI寄语:\n{encouragement}")

    # 4. 模拟最终报告组装
    print("\n📊 最终报告预览 (部分):")
    print("-" * 30)
    for row in formatted["daily_rows_data"]:
        d = row['fmt_date']
        item = core_items_result.get(d, row['raw_core_item'])
        print(f"| {d} | {item} | {row['hours']}h |")
    print("-" * 30)
    print(f"致追梦者: {encouragement}")

if __name__ == "__main__":
    test_report_generation()