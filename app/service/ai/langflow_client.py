import os
import requests
import json

class LangflowClient:
    def __init__(self, timeout: int = 180):
        # 按照用户要求，改为直接调用 Ollama 端口
        # 默认 Ollama 地址: http://localhost:11434
        self.ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        # 用户指定的模型: gpt-oss:20b-cloud (修正了拼写错误)
        self.model = os.getenv('OLLAMA_MODEL', 'gpt-oss:20b-cloud')
        self.timeout = timeout

    def call_flow(self, flow: str, text: str):
        """
        替代原本的 Langflow 调用，直接调用 Ollama。
        参数 flow 在此处仅作记录，不再影响路由，统一使用指定模型处理。
        """
        # 优先尝试 /api/chat 接口
        url = f"{self.ollama_base_url}/api/chat"
        
        # 构造 Ollama 请求
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": text}
            ],
            "stream": False
        }

        try:
            resp = requests.post(
                url,
                json=payload,
                timeout=self.timeout
            )
            
            # 特殊处理 404 错误，尝试回退或提供更明确的报错
            if resp.status_code == 404:
                error_text = resp.text.lower()
                # 如果是模型未找到，通常包含 "model" 和 "not found"
                if "model" in error_text and "not found" in error_text:
                    print(f"[OllamaClient] Model '{self.model}' not found. Please check 'ollama list'.")
                    return None
                
                # 如果不是模型错误，可能是端点不支持，尝试 /api/generate
                print(f"[OllamaClient] /api/chat not found (404), falling back to /api/generate...")
                return self._call_generate_fallback(text)

            resp.raise_for_status()
            data = resp.json()
            return self._extract_text(data)
        except Exception as e:
            # 打印错误日志以便调试
            print(f"[OllamaClient] Error calling Ollama ({url}): {e}")
            return None

    def _call_generate_fallback(self, text: str):
        """
        回退方法：使用 /api/generate 接口
        """
        url = f"{self.ollama_base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": text,
            "stream": False
        }
        try:
            resp = requests.post(url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            return self._extract_text(data)
        except Exception as e:
            print(f"[OllamaClient] Fallback to /api/generate failed: {e}")
            return None

    def _extract_text(self, data):
        # 适配 Ollama 的响应格式
        try:
            # /api/chat 的响应格式: data["message"]["content"]
            if "message" in data and "content" in data["message"]:
                return data["message"]["content"]
        except Exception:
            pass
        
        try:
            # /api/generate 的响应格式 (作为备用兼容): data["response"]
            if "response" in data:
                return data["response"]
        except Exception:
            pass
            
        # 如果格式都不匹配，尝试返回整个数据字符串（用于调试）或 None
        return None
