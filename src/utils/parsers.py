import re

def clean_code_block(raw_text: str) -> str:
    """
    從 LLM 的回覆中提取純程式碼。
    移除 ```python ... ``` 標記。
    """
    if not raw_text:
        return ""

    # 1. 嘗試抓取 ```python ... ``` 中間的內容
    pattern = r"```(?:\w+)?\n(.*?)```"
    match = re.search(pattern, raw_text, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    
    # 2. 如果沒有 markdown 標記，但有可能只有單純的 ``` 包裹
    if "```" in raw_text:
        return raw_text.replace("```", "").strip()
        
    # 3. 如果原本就是純文字，直接回傳
    return raw_text.strip()