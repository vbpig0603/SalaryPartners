import subprocess
import sys
import os
from pathlib import Path

class TestRunner:
    """負責執行 playground 中的測試程式"""

    def __init__(self, playground_dir: str = "playground", source_dirs: list[str] = None):
        self.playground_path = Path(playground_dir).resolve()
        # 如果沒傳，預設 source code 也在 playground (為了相容舊邏輯)
        self.source_paths = [Path(p).resolve() for p in (source_dirs or [playground_dir])]

    def run(self, test_filename: str) -> tuple[str, str]:
        """
        Returns:
            status: "PASS" | "FAIL" (AssertionError) | "ERROR" (Syntax/System Error)
            message: 詳細訊息
        """
        target_file = self.playground_path / test_filename
        
        if not target_file.exists():
            return "ERROR", f"❌ 找不到測試檔案: {target_file}"

        print(f"    ...執行 Pytest: {test_filename}")

        # ✅ 關鍵修改：設定 PYTHONPATH
        env = os.environ.copy()
        current_pythonpath = env.get("PYTHONPATH", "")
        
        # 把所有的 source_dirs 都加入 PYTHONPATH
        # 這樣 Python 就會去這些資料夾找 import
        additional_paths = [str(p) for p in self.source_paths]
        # 也把 playground 本身加進去 (因為測試檔在這裡)
        additional_paths.append(str(self.playground_path))
        
        # 組合路徑 (Windows 用 ; 分隔)
        env["PYTHONPATH"] = os.pathsep.join(additional_paths) + os.pathsep + current_pythonpath

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(target_file)],
                capture_output=True,
                text=True,
                timeout=30,
                env=env
            )
            
            # 除錯用輸出
            # print(result.stdout) 
            # print(result.stderr)

            if result.returncode == 0:
                return "PASS", "✅ 測試通過"
            
            elif result.returncode == 1:
                # Exit Code 1 代表測試有跑完，但 Assertion Failed
                # 這在 TDD 階段是正確的「紅燈」
                return "FAIL", f"🔴 測試邏輯失敗 (Assertion Error):\n{result.stdout}"
            
            else:
                # 其他 Exit Code (2, 3, 4, 5) 代表語法錯誤、Import 錯誤等
                return "ERROR", f"💥 測試碼本身有錯 (Syntax/Import Error):\n{result.stderr}\n{result.stdout}"

        except subprocess.TimeoutExpired:
            return "ERROR", "❌ 測試執行逾時 (Timeout)"
        except Exception as e:
            return "ERROR", f"❌ 執行發生例外錯誤: {str(e)}"