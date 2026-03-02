import requests
from core.config_manager import config_manager
import logging
from typing import Union, Dict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Pusher:
    def __init__(self):
        pass

    def push(self, content: Union[str, Dict], webhook_url: str = None) -> bool:
        """
        Push content to Enterprise WeChat Webhook.
        If content is a string, it sends as markdown.
        If content is a dict, it sends as raw JSON payload.
        If webhook_url is not provided, uses global default from config.
        """
        if not webhook_url:
            webhook_url = config_manager.config["notification"].get("webhook_url", "")
        
        if not webhook_url:
            logger.warning("Webhook URL not configured.")
            return False

        # Construct payload
        if isinstance(content, dict):
            payload = content
        else:
            # Default to markdown
            payload = {
                "msgtype": "markdown",
                "markdown": {
                    "content": content
                }
            }

        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            if response.status_code == 200:
                # WeCom API returns 200 even for some errors, check errcode
                res_json = response.json()
                if res_json.get("errcode") == 0:
                    logger.info("Pushed successfully.")
                    return True
                else:
                    logger.error(f"Push failed with API error: {res_json}")
                    return False
            else:
                logger.error(f"Push failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Push error: {e}")
            return False

# Global instance
pusher = Pusher()
