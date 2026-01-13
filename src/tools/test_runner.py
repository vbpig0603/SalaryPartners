import subprocess
import sys
import os
from pathlib import Path

class TestRunner:
    """負責執行 playground 中的測試程式"""
    
    def __init__(self, playground_dir: str = "playground"):
        self.playground_path = Path(playground_dir).resolve()

    def run(self, test_filename: str) -> tuple[bool, str]:
        target_file = self.playground_path / test_filename
        
        if not target_file.exists():
            return False, f"❌ 找不到測試檔案: {target_file}"

        print(f"    ...執行 Pytest: {test_filename}")

        # 設定 PYTHONPATH
        env = os.environ.copy()
        current_path = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = str(self.playground_path) + os.pathsep + current_path

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(target_file)],
                capture_output=True,
                text=True,
                timeout=30,
                env=env
            )
            
            # ✅ 新增：把 Pytest 的輸出印出來給人類看
            print("-" * 20 + " Pytest Logs " + "-" * 20)
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr) # 通常是嚴重的系統錯誤
            print("-" * 53)
            
            if result.returncode == 0:
                return True, "PASS"
            else:
                return False, f"FAILED:\n{result.stdout}\n{result.stderr}"
                
        except subprocess.TimeoutExpired:
            print("❌ Timeout!")
            return False, "❌ 測試執行逾時 (Timeout)"
        except Exception as e:
            print(f"❌ Error: {e}")
            return False, f"❌ 執行發生例外錯誤: {str(e)}"