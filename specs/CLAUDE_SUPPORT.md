# Claude API 支持说明

## 配置方式

在 `config.yaml` 中设置：

```yaml
llm:
  provider: anthropic
  api_key: "sk-ant-..."  # Anthropic API Key
  model_name: claude-3-5-sonnet-20241022
```

## 支持的模型

- `claude-3-5-sonnet-20241022` (推荐)
- `claude-3-opus-20240229`
- `claude-3-haiku-20240307`

## Rate Limit 处理

`core/llm_base.py` 已实现自动重试机制：

| 参数 | 值 | 说明 |
|------|-----|------|
| MAX_RETRIES | 3 | 最大重试次数 |
| BASE_RETRY_DELAY | 1.0s | 基础延迟时间 |
| MAX_RETRY_DELAY | 60.0s | 最大延迟时间 |

重试策略：指数退避 + 抖动
- 第 1 次重试：~1-1.1s
- 第 2 次重试：~2-2.2s
- 第 3 次重试：~4-4.4s

如果 API 返回 `retry-after` header，会优先使用该值。

## 依赖安装

```bash
pip install anthropic==0.18.0
```

## 测试

```python
from core.llm_base import LLMBase

llm = LLMBase()
response = llm.generate_response(
    system_prompt="你是一个助手",
    user_prompt="你好，请介绍一下自己"
)
print(response)
```
