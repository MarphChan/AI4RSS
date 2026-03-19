# 开发规范（Principles）

从 lessons.md 中提炼的通用规则，适用于本项目所有模块。

---

## 1. Python 异常处理

### 1.1 禁止裸 `except:`
- 任何 except 子句必须指定捕获类型。
- 防御性兜底最宽泛写 `except Exception`，可预测错误写具体类型如 `except (ValueError, IndexError)`。
- 裸 `except:` 会拦截 `KeyboardInterrupt`、`SystemExit` 等，导致进程无法正常终止。

```python
# ❌ 错误
try:
    ...
except:
    pass

# ✅ 正确
try:
    ...
except Exception as e:
    logger.error(f"...: {e}")
```

### 1.2 try 块外预初始化变量
- 在 try 块内赋值的变量，若在 except / try 块之后仍被引用，必须在 try 块**外部**预先初始化为安全默认值（通常为 `None`）。
- 否则，一旦 except 分支执行，后续代码会触发 `NameError` 或使用上一轮迭代的脏值。

```python
# ❌ 错误
for future in as_completed(futures):
    try:
        article_meta = future.result()
    except Exception as e:
        logger.error(e)
    # article_meta 若异常则未定义
    progress_callback(article_meta['title'])

# ✅ 正确
for future in as_completed(futures):
    article_meta = None          # 预初始化
    try:
        article_meta = future.result()
    except Exception as e:
        logger.error(e)
    if article_meta:
        progress_callback(article_meta['title'])
```

---

## 2. 并发处理

### 2.1 用 `as_completed` 遍历 futures
- 对 futures 字典直接迭代（`for f in futures:`）只是按提交顺序阻塞等待，浪费并发优势。
- 必须使用 `concurrent.futures.as_completed(futures)` 以完成顺序处理。

```python
# ❌ 错误
for future in futures:
    result = future.result()

# ✅ 正确
from concurrent.futures import as_completed
for future in as_completed(futures):
    result = future.result()
```

### 2.2 并发数通过配置读取，不硬编码
- `ThreadPoolExecutor(max_workers=N)` 中的 N 不得硬编码，必须从配置读取。
- 配置路径：`system.max_workers`（默认 5）。

```python
# ❌ 错误
with ThreadPoolExecutor(max_workers=5) as executor:
    ...

# ✅ 正确
max_workers = config_manager.get("system.max_workers", 5)
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    ...
```

---

## 3. 数据安全

### 3.1 返回可变默认值时必须深拷贝
- 类变量（`DEFAULT_CONFIG` 等）是所有实例共享的可变对象，直接返回引用会导致调用方修改后污染类状态。
- 返回前用 `copy.deepcopy()`。

```python
# ❌ 错误
return self.DEFAULT_CONFIG

# ✅ 正确
import copy
return copy.deepcopy(self.DEFAULT_CONFIG)
```

### 3.2 时间 fallback 不得使用 `datetime.now()`
- 对于来源不明或缺失时间字段的数据（如 RSS 无日期条目），不能用 `datetime.now()` 作为 fallback。
- 应跳过该条目（`continue`）或赋值为 `None`，由下游过滤，避免"时间未知"的内容伪装成"最新内容"通过时间窗口过滤。

```python
# ❌ 错误
pub_date = entry.get('published') or datetime.now()

# ✅ 正确
if not entry.get('published_parsed'):
    continue  # 跳过无日期条目
```

---

## 4. 代码组织

### 4.1 import 语句必须在模块顶部
- 所有无条件 import 放在文件顶部，不得写在函数或方法体内。
- 函数内 import 仅允许用于明确的延迟加载场景（如可选依赖）。

```python
# ❌ 错误
def _calculate_delay(self):
    import random
    return random.random()

# ✅ 正确
import random  # 文件顶部

def _calculate_delay(self):
    return random.random()
```

---

## 5. Streamlit 专项

### 5.1 同名组件必须设置唯一 key
- Streamlit 每次交互重新运行整个脚本，所有 Tab 的内容都会被渲染。
- 同名 widget（如两个 `st.button("删除选中")`）必须指定不同的 `key` 参数，否则报 `DuplicateWidgetID`。

### 5.2 布尔列筛选使用 `.fillna(False).astype(bool)`
- `data_editor` 返回的布尔列可能包含 `NaN`，直接 `== True` 筛选不可靠。
- 标准写法：`df.loc[df["col"].fillna(False).astype(bool)]`

### 5.3 NumPy 类型在序列化前需转换
- `data_editor` 返回的 DataFrame 单个值可能是 `numpy.bool_` 等 NumPy 类型，`json.dump` 不支持。
- 保存前用 `.item()` 转为 Python 原生类型，或统一通过 `_sanitize_value` 辅助方法处理。

### 5.4 避免不必要的 `st.rerun()` 重建 widget state
- 使用稳定的 `data_editor` key，避免因 key 变化导致 widget state 重建后步骤状态回落。
- 触发 `st.rerun()` 前显式写回当前步骤到 `session_state`。

---

## 6. 调度与定时任务

### 6.1 仅在配置变化时刷新调度表
- `schedule.clear()` + 重新添加任务不应无条件执行（如每分钟触发一次）。
- 应比较新旧配置，仅在时间配置实际发生变化时才重新调度，否则可能在任务即将执行时将其清除，导致当天跳过。

---

## 7. 通用质量要求

- **静默失败要有反馈**：并发任务部分失败时，结果中应包含失败列表（如 `⚠️ Failed to Fetch` 章节），不能只显示成功部分。
- **配置热重载**：用户在 UI 更新配置后，需调用 `reload()` 使变更对运行中的服务立即生效，不能依赖应用重启。
- **NaN 不写入 JSON**：保存数据到 JSON 前，清洗所有 `NaN`/`None`，保证输出合法 JSON。
