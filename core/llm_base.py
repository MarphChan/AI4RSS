import logging
from typing import Optional
from openai import OpenAI
from core.config_manager import config_manager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LLMBase:
    def __init__(self):
        self.config = config_manager.config["llm"]
        self.provider = self.config.get("provider", "dashscope")
        self.api_key = self.config.get("api_key", "")
        self.model_name = self.config.get("model_name", "qwen-max")
        
        self.client = self._init_client()

    def _init_client(self) -> Optional[OpenAI]:
        """Initialize OpenAI compatible client."""
        if not self.api_key:
            return None
        
        base_url = "https://api.openai.com/v1"
        if self.provider == "dashscope":
            base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        elif self.provider == "volcengine":
            base_url = "https://ark.cn-beijing.volces.com/api/v3" 
        elif self.provider == "deepseek":
            base_url = "https://api.deepseek.com"
        elif self.provider == "moonshot":
            base_url = "https://api.moonshot.cn/v1"
        elif self.provider == "yi":
            base_url = "https://api.lingyiwanwu.com/v1"
        elif self.provider == "custom":
             # Try to get custom base url from config
             base_url = self.config.get("base_url", "https://api.openai.com/v1")

        return OpenAI(
            api_key=self.api_key,
            base_url=base_url
        )

    def generate_response(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        """Generic method to call LLM."""
        if not self.client:
            return ""
            
        try:
            kwargs = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            }
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
                
            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM Generation Error: {e}")
            return ""
