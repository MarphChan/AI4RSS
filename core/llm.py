from core.llm_base import LLMBase
from core.llm_content import ContentMixin
from core.llm_discovery import DiscoveryMixin
from core.llm_format import FormatMixin

class LLMEngine(LLMBase, ContentMixin, DiscoveryMixin, FormatMixin):
    pass

# Global instance
llm_engine = LLMEngine()
