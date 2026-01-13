import os
from pathlib import Path

# 設定要忽略的目錄和檔案
IGNORE_DIRS = {'.git', '.venv', '__pycache__', 'playground', '.idea', '.vscode'}
IGNORE_FILES = {'uv.lock', '.env'}
# 設定只讀取哪些副檔名 (避免讀到圖檔或執行檔)
ALLOWED_EXTENSIONS = {'.py', '.toml', '.md', '.example'}

def generate_tree(start_path):
    """生成目錄樹狀圖與檔案內容"""
    start_path = Path(start_path)
    output = []
    
    output.append(f"# Project Snapshot: {start_path.name}")
    output.append("=" * 50 + "\n")

    for root, dirs, files in os.walk(start_path):
        # 過濾目錄 (修改 dirs 列表會影響 os.walk 的後續遍歷)
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        level = root.replace(str(start_path), '').count(os.sep)
        indent = ' ' * 4 * (level)
        output.append(f"{indent}📂 {os.path.basename(root)}/")
        
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if f in IGNORE_FILES:
                continue
            if not any(f.endswith(ext) for ext in ALLOWED_EXTENSIONS):
                continue

            file_path = Path(root) / f
            output.append(f"{subindent}📄 {f}")
            
            # 讀取檔案內容
            try:
                content = file_path.read_text(encoding='utf-8')
                output.append(f"\n{subindent}--- [START {f}] ---")
                output.append(content)
                output.append(f"{subindent}--- [END {f}] ---\n")
            except Exception as e:
                output.append(f"{subindent}[Error reading file: {e}]")

    return "\n".join(output)

if __name__ == "__main__":
    # 執行位置假設在專案根目錄
    project_root = "." 
    snapshot = generate_tree(project_root)
    
    # 輸出到檔案，方便複製
    with open("project_context.txt", "w", encoding="utf-8") as f:
        f.write(snapshot)
    
    print("✅ 專案快照已生成: project_context.txt")
    print("請將該檔案內容複製給 AI 進行 Sync。")