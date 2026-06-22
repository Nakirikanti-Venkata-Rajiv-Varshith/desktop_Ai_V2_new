import requests
import json
from config.settings import OLLAMA_URL, OLLAMA_MODEL
from tools.logger import agent_logger

class OllamaClient:
    """Handles communications with local Ollama daemon infrastructure."""
    
    def __init__(self):
        self.url = OLLAMA_URL
        self.model = OLLAMA_MODEL

    def generate(self, user_prompt: str) -> str:
        # Determine if we are hitting the chat or generate endpoint dynamically
        is_chat_endpoint = "/api/chat" in self.url

        if is_chat_endpoint:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                "stream": False,
                "options": {"temperature": 0}
            }
        else:
            # Traditional fallback structure
            payload = {
                "model": self.model,
                "prompt": f"{SYSTEM_PROMPT}\n\nUser: {user_prompt}\nOutput:",
                "stream": False,
                "options": {"temperature": 0}
            }

        try:
            agent_logger.info(f"Dispatching query to Ollama ({self.model})...")
            response = requests.post(self.url, json=payload, timeout=60)
            response.raise_for_status()
            response_json = response.json()

            if is_chat_endpoint:
                raw_response = response_json.get("message", {}).get("content", "").strip()
            else:
                raw_response = response_json.get("response", "").strip()

            # --- CRITICAL SAFETY FALLBACK ---
            # If the model returned absolutely nothing, intercept it before it hits the parser!
            if not raw_response:
                agent_logger.warning("Empty response received from LLM. Injecting automated system fallback.")
                if "time" in user_prompt.lower() or "clock" in user_prompt.lower():
                    raw_response = '{"tool": "system", "function": "current_time", "arguments": {}}'
                elif "date" in user_prompt.lower() or "today" in user_prompt.lower():
                    raw_response = '{"tool": "system", "function": "current_date", "arguments": {}}'
                else:
                    raw_response = '{"tool": "system", "function": "os_info", "arguments": {}}'

            print("\n" + "="*60)
            print("USER PROMPT:")
            print(user_prompt)
            print("="*60)
            print("RAW LLM RESPONSE:")
            print(raw_response)
            print("="*60 + "\n")

            return raw_response

        except Exception as e:
            agent_logger.error(f"Ollama connection dropped/failed: {str(e)}")
            raise ConnectionError(f"Could not interact with local LLM context: {str(e)}")