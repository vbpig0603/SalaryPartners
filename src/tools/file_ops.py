import os
from pathlib import Path

# 設定一個安全的沙盒目錄
PLAYGROUND_DIR = Path("playground")

def save_to_playground(filename: str, content: str) -> str:
    """
    將內容寫入 playground 資料夾中的指定檔案。
    如果資料夾不存在會自動建立。
    """
    # 確保 playground 資料夾存在
    PLAYGROUND_DIR.mkdir(parents=True, exist_ok=True)
    
    # 組合完整路徑
    file_path = PLAYGROUND_DIR / filename
    
    # 寫入檔案
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"💾 [System] 檔案已儲存: {file_path}")
    return str(file_path)

def read_from_playground(filename: str) -> str:
    """讀取 playground 中的檔案內容"""
    file_path = PLAYGROUND_DIR / filename
    
    if not file_path.exists():
        return ""
        
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()