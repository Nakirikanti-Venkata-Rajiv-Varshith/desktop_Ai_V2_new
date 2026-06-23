# llm/ollama_client.py
import requests
import json
from config.settings import OLLAMA_URL, OLLAMA_MODEL
from config.settings import OLLAMA_URL, OLLAMA_MODEL
from tools.logger import agent_logger
from llm.prompts.router_prompt import ROUTER_PROMPT

class OllamaClient:
    """Handles communications with local Ollama daemon infrastructure."""
    
    def __init__(self):
        self.url = OLLAMA_URL
        self.model = OLLAMA_MODEL

    def route(self, user_text: str) -> str:
        """Determines the appropriate tool category for the user text."""
        payload = {
            "model": self.model,
            "prompt": f"{ROUTER_PROMPT}\n\nUser: {user_text}\nOutput:",
            "stream": False,
            "options": {"temperature": 0}
        }
        try:
            agent_logger.info(f"Routing query to Ollama ({self.model})...")
            response = requests.post(self.url, json=payload, timeout=60)
            response.raise_for_status()
            
            tool_name = response.json().get("response", "").strip().lower()
            
            # Clean up potential extra wrapper punctuation or tokens
            for possible_tool in ["gmail", "youtube", "browser", "system", "file", "chat"]:
                if possible_tool in tool_name:
                    return possible_tool
            return "system"  # Safe default fallback
        except Exception as e:
            agent_logger.error(f"Ollama routing fallback triggered: {str(e)}")
            return "system"

    def generate(self, complete_prompt: str) -> str:
        """Generates structured tool execution instructions from the built prompt context."""
        payload = {
            "model": self.model,
            "prompt": complete_prompt,
            "stream": False,
            "options": {"temperature": 0}
        }

        try:
            agent_logger.info(f"Dispatching query to Ollama ({self.model})...")
            response = requests.post(self.url, json=payload, timeout=60)
            response.raise_for_status()
            
            raw_response = response.json().get("response", "").strip()
            print("\n" + "="*80)
            print("RAW OLLAMA RESPONSE")
            print("="*80)
            print(raw_response)
            print("="*80 + "\n")
            # --- CRITICAL SAFETY FALLBACK ---
            if not raw_response:
                agent_logger.warning("Empty response received from LLM. Injecting automated system fallback.")
                if "time" in complete_prompt.lower():
                    raw_response = '{"tool": "system", "function": "current_time", "arguments": {}}'
                elif "date" in complete_prompt.lower():
                    raw_response = '{"tool": "system", "function": "current_date", "arguments": {}}'
                else:
                    raw_response = '{"tool": "system", "function": "os_info", "arguments": {}}'

            return raw_response
        except Exception as e:
            agent_logger.error(f"Ollama connection failed: {str(e)}")
            return '{"tool": "system", "function": "os_info", "arguments": {}}'