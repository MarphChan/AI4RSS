from openai import OpenAI
from core.config_manager import config_manager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImageGenerator:
    def __init__(self):
        self.config = config_manager.config["image"]
        self.llm_config = config_manager.config["llm"]
        self.enabled = self.config.get("enable_generation", True)
        self.provider = self.config.get("provider", "wanx")
        
        # Re-use LLM key if possible, or assume same provider for MVP
        self.api_key = self.llm_config.get("api_key", "")
        self.client = self._init_client()

    def _init_client(self):
        if not self.api_key or not self.enabled:
            return None
        
        # For DALL-E 3 (via OpenAI)
        if self.provider == "dall-e-3" or "openai" in self.llm_config.get("provider", ""):
             return OpenAI(api_key=self.api_key)
        
        # For Wanx (DashScope), we also use OpenAI compatible client or DashScope SDK
        # For MVP, let's assume OpenAI compatible image generation or just return placeholder
        # if using DashScope/Wanx via OpenAI SDK (which is not standard).
        # Actually DashScope has its own SDK. 
        # To keep dependencies simple (only openai), we might struggle with Wanx unless we use `dashscope` lib.
        # But `requirements.txt` only has `openai`.
        # Let's support DALL-E 3 first. If DashScope, we might need to skip or mock for now.
        
        return OpenAI(
            api_key=self.api_key,
            base_url="https://api.openai.com/v1" # Standard OpenAI for DALL-E
        )

    def generate_image(self, prompt: str) -> str:
        """
        Generate image from prompt. Returns URL.
        """
        if not self.enabled or not self.client:
            return ""

        # Refine prompt
        full_prompt = f"{prompt}, high resolution, 4k, minimalist style, vector art, soft lighting, tech blue and orange theme, no text, clean background."

        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=full_prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            return response.data[0].url
        except Exception as e:
            logger.error(f"Image Generation Error: {e}")
            return ""

# Global instance
image_generator = ImageGenerator()
