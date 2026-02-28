import unittest
from unittest.mock import MagicMock, patch
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.llm import LLMEngine

class TestLLMProviders(unittest.TestCase):
    @patch('core.llm_base.config_manager')
    @patch('core.llm_base.OpenAI')
    def test_provider_base_urls(self, mock_openai, mock_config):
        # Helper to test a provider
        def check_provider(provider, expected_url, config_base_url=""):
            mock_config.config = {
                "llm": {
                    "provider": provider,
                    "api_key": "test_key",
                    "model_name": "test_model",
                    "base_url": config_base_url
                }
            }
            llm = LLMEngine()
            mock_openai.assert_called_with(api_key="test_key", base_url=expected_url)

        # Test DeepSeek
        check_provider("deepseek", "https://api.deepseek.com")
        
        # Test Moonshot
        check_provider("moonshot", "https://api.moonshot.cn/v1")
        
        # Test Custom
        check_provider("custom", "http://my-custom-url.com", "http://my-custom-url.com")
        
        # Test Default (Dashscope)
        check_provider("dashscope", "https://dashscope.aliyuncs.com/compatible-mode/v1")

if __name__ == '__main__':
    unittest.main()
