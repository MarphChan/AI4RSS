import logging
import time
from typing import Optional
from openai import OpenAI
from openai import RateLimitError as OpenAIRateLimitError
from core.config_manager import config_manager

try:
    from anthropic import Anthropic
    from anthropic import RateLimitError as AnthropicRateLimitError
except Exception:
    Anthropic = None

    class AnthropicRateLimitError(Exception):
        pass

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LLMBase:
    """LLM Base class with support for multiple providers and rate limit handling."""
    
    # Rate limit retry configuration
    MAX_RETRIES = 3
    BASE_RETRY_DELAY = 1.0  # seconds
    MAX_RETRY_DELAY = 60.0  # seconds
    
    def __init__(self):
        self.config = config_manager.config["llm"]
        self.provider = self.config.get("provider", "dashscope")
        self.api_key = self.config.get("api_key", "")
        self.model_name = self.config.get("model_name", "qwen-max")
        
        # Initialize clients
        self.openai_client = None
        self.anthropic_client = None
        self.client = None # For compatibility with mixins
        self._init_clients()

    def _init_clients(self):
        """Initialize OpenAI and Anthropic clients."""
        if not self.api_key:
            logger.warning("No API key configured")
            return

        if self.provider == "anthropic":
            if Anthropic is None:
                logger.error("Anthropic provider selected but SDK 'anthropic' is not installed")
                return
            self.anthropic_client = Anthropic(api_key=self.api_key)
            self.client = self.anthropic_client # Compatibility (partial)
            logger.info("Anthropic client initialized for Claude")
            return
        
        # Initialize OpenAI-compatible client
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
            base_url = self.config.get("base_url", "https://api.openai.com/v1")
        
        # Allow overriding base_url for openai provider if specified
        if self.provider == "openai":
            custom_url = self.config.get("base_url")
            if custom_url and custom_url.strip():
                base_url = custom_url
        
        self.openai_client = OpenAI(
            api_key=self.api_key,
            base_url=base_url
        )
        self.client = self.openai_client # Alias for compatibility with mixins

    def reload(self):
        """Reload configuration and re-initialize clients."""
        self.config = config_manager.config["llm"]
        self.provider = self.config.get("provider", "dashscope")
        self.api_key = self.config.get("api_key", "")
        self.model_name = self.config.get("model_name", "qwen-max")
        self._init_clients()

    def _calculate_retry_delay(self, attempt: int, retry_after: Optional[float] = None) -> float:
        """Calculate exponential backoff delay with jitter."""
        if retry_after is not None:
            return min(retry_after, self.MAX_RETRY_DELAY)
        
        # Exponential backoff: base_delay * 2^attempt
        delay = self.BASE_RETRY_DELAY * (2 ** attempt)
        # Add small jitter (±10%)
        import random
        jitter = delay * 0.1 * random.random()
        return min(delay + jitter, self.MAX_RETRY_DELAY)

    def _handle_rate_limit(self, attempt: int, error: Exception) -> bool:
        """Handle rate limit error with retry logic.
        
        Returns True if should retry, False if should give up.
        """
        if attempt >= self.MAX_RETRIES:
            logger.error(f"Rate limit exceeded after {self.MAX_RETRIES} retries")
            return False
        
        # Extract retry-after from error if available
        retry_after = None
        if hasattr(error, 'response') and error.response is not None:
            retry_after_header = error.response.headers.get('retry-after')
            if retry_after_header:
                try:
                    retry_after = float(retry_after_header)
                except ValueError:
                    pass
        
        delay = self._calculate_retry_delay(attempt, retry_after)
        logger.warning(f"Rate limit hit. Retrying in {delay:.1f}s (attempt {attempt + 1}/{self.MAX_RETRIES})")
        time.sleep(delay)
        return True

    def generate_response(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        """Generate response with rate limit handling and automatic retries."""
        attempt = 0
        
        while attempt <= self.MAX_RETRIES:
            try:
                if self.provider == "anthropic" and self.anthropic_client:
                    return self._generate_anthropic(system_prompt, user_prompt, json_mode)
                elif self.openai_client:
                    return self._generate_openai(system_prompt, user_prompt, json_mode)
                else:
                    logger.error("No LLM client available")
                    return ""
                    
            except (OpenAIRateLimitError, AnthropicRateLimitError) as e:
                logger.warning(f"Rate limit error: {e}")
                if not self._handle_rate_limit(attempt, e):
                    return ""
                attempt += 1
            except Exception as e:
                logger.error(f"LLM Generation Error: {e}")
                return ""
        
        return ""

    def _generate_openai(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        """Generate response using OpenAI-compatible API."""
        kwargs = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
            
        response = self.openai_client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

    def _generate_anthropic(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        """Generate response using Anthropic Claude API."""
        # Claude uses different message format
        messages = [{"role": "user", "content": user_prompt}]
        
        # Build system prompt
        system_content = system_prompt
        if json_mode:
            system_content += "\n\nPlease respond with valid JSON only."
        
        response = self.anthropic_client.messages.create(
            model=self.model_name,
            max_tokens=4096,
            system=system_content,
            messages=messages
        )
        
        return response.content[0].text
