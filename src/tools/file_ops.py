from pathlib import Path

class FileOps:
    """
    檔案操作工具
    負責處理專案中的檔案讀寫，預設操作範圍限制在 playground 目錄以策安全。
    """
    
    def __init__(self, base_dir: str = "playground"):
        self.base_dir = Path(base_dir)
        # 確保目錄存在
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, filename: str, content: str) -> str:
        """
        儲存檔案
        Returns: 儲存後的完整路徑字串
        """
        # 簡單的防呆：如果 Agent 給的路徑包含目錄 (e.g. "subdir/test.py")
        file_path = self.base_dir / filename
        
        # 確保該檔案的父目錄存在
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        print(f"💾 [System] 檔案已儲存: {file_path}")
        return str(file_path)

    def read(self, filename: str) -> str:
        """讀取檔案內容"""
        file_path = self.base_dir / filename
        
        if not file_path.exists():
            return ""
            
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()