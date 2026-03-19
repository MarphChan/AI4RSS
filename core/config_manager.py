import copy
import yaml
import os
from typing import Dict, Any

DEFAULT_AI_NEWS_IMAGE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "static", "images", "ai_news.svg")
)

class ConfigManager:
    DEFAULT_CONFIG = {
        "system": {
            "fetch_time": "08:00",
            "push_time": "09:30",
            "timezone": "Asia/Shanghai",
            "time_period": 24,
            "max_items": 20,
            "max_workers": 5,
            "fetch_article_images": False
        },
        "llm": {
            "provider": "dashscope",
            "api_key": "",
            "model_name": "qwen-max"
        },
        "image": {
            "enable_generation": True,
            "provider": "wanx",
            "default_images": [DEFAULT_AI_NEWS_IMAGE]
        },
        "notification": {
            "webhook_url": ""
        },
        "feishu": {
            "receiver_enabled": False,
            "receiver_host": "127.0.0.1",
            "receiver_port": 8765,
            "receiver_token": ""
        }
    }

    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file. Create with defaults if not exists."""
        if not os.path.exists(self.config_path):
            self._save_config(self.DEFAULT_CONFIG)
            return copy.deepcopy(self.DEFAULT_CONFIG)

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return self._merge_defaults(config, self.DEFAULT_CONFIG)
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")
            return copy.deepcopy(self.DEFAULT_CONFIG)

    def _merge_defaults(self, config: Dict, default: Dict) -> Dict:
        """Deep merge config with defaults to ensure all keys exist.
        User-supplied empty lists are treated as valid values and honoured."""
        if not isinstance(config, dict):
            return default

        result = default.copy()
        for key, value in config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_defaults(value, result[key])
            else:
                result[key] = value
        return result

    def save(self, new_config: Dict[str, Any]):
        """Save configuration to YAML file."""
        self._config = new_config
        self._save_config(new_config)

    def _save_config(self, config: Dict[str, Any]):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)

    @property
    def config(self) -> Dict[str, Any]:
        return self._config

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from config using dot notation (e.g. 'system.fetch_time')"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

# Global instance
config_manager = ConfigManager()
