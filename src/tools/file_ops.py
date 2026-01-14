from pathlib import Path
import shutil
from src.utils.parsers import clean_code_block

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
        # ✅ 自動清洗 Markdown 標記
        clean_content = clean_code_block(content)
        
        # 簡單防呆
        if not filename:
            print("⚠️ [FileOps] 警告：檔名為空，跳過存檔")
            return ""

        file_path = self.base_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(clean_content) # 寫入清洗後的內容
            
        print(f"💾 [System] 檔案已儲存: {file_path}")
        return str(file_path)

    def read(self, filename: str) -> str:
        """讀取檔案內容"""
        file_path = self.base_dir / filename
        
        if not file_path.exists():
            return ""
            
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
        
    def rename(self, src: str, dst: str) -> None:
        """重新命名檔案"""
        src_path = self.base_dir / src
        dst_path = self.base_dir / dst
        
        if not src_path.exists():
            return
        
        src_path.rename(dst_path)
        print(f"RENAMED {src_path} -> {dst_path}")

    def backup(self, filename: str) -> None:
        """備份檔案 (副檔名改為 .bak)"""
        file_path = self.base_dir / filename
        if not file_path.exists():
            return
        
        file_path.replace(file_path.with_suffix(".bak"))
    
    def restore(self, filename: str) -> None:
        """恢復檔案 (副檔名改回原來的)"""
        file_path = self.base_dir / filename
        if not file_path.exists():
            return
        
        file_path.replace(file_path.with_suffix(""))

    def exists(self, filename: str) -> bool:
        """檢查檔案是否存在"""
        file_path = self.base_dir / filename
        return file_path.exists()
    
    def copy(self, src: str, dst: str) -> None:
        """複製檔案"""
        src_path = self.base_dir / src
        dst_path = self.base_dir / dst
        
        if not src_path.exists():
            return
        
        shutil.copy(src_path, dst_path)
        print(f"Copied {src_path} -> {dst_path}")

    def unlink(self, filename: str) -> None:
        """刪除檔案"""
        file_path = self.base_dir / filename
        if not file_path.exists():
            return
        
        file_path.unlink(missing_ok=True)
        print(f"Deleted {file_path}")