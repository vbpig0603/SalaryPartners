import dspy

class WriteTestSignature(dspy.Signature):
    """
    [TDD Red Phase]
    根據需求，先定義測試案例。
    如果還沒有 Source Code，請根據需求與檔名自行推斷 Import 寫法。
    """
    requirement = dspy.InputField(desc="功能需求")
    
    # 這裡對應 OfficeManager 傳來的 source_code
    source_code = dspy.InputField(desc="目前的程式碼 (TDD 第一階段通常為空)", default="")
    
    # 這裡對應 OfficeManager 傳來的 src_filename
    src_filename = dspy.InputField(desc="預期的實作檔名 (例如 'fibonacci.py')，用來寫 import", default="")
    
    # Outputs
    test_file_name = dspy.OutputField(desc="建議的測試檔名 (例如 'test_fibonacci.py')")
    test_code = dspy.OutputField(desc="Pytest 測試程式碼")
    
    # 讓 QA 順便告訴我們它覺得實作檔該叫什麼名字 (如果 src_filename 是空的)
    suggested_src_filename = dspy.OutputField(desc="如果輸入的 src_filename 是空的，請建議一個實作檔名")

class QAAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.prog = dspy.ChainOfThought(WriteTestSignature)
    
    # ✅ 關鍵修正：forward 必須接收這三個參數，名稱要跟 OfficeManager 呼叫的一模一樣
    def forward(self, requirement, source_code, src_filename):
        
        # 簡單的邏輯處理：如果是 None 改成空字串
        safe_source_code = source_code if source_code else "尚無實作 (TDD Red Phase)"
        safe_src_filename = src_filename if src_filename else ""
        
        result = self.prog(
            requirement=requirement,
            source_code=safe_source_code,
            src_filename=safe_src_filename
        )
        
        # 這裡做一個小轉換：
        # 如果原本有傳檔名，就回傳原本的；如果沒有，就用 QA 建議的
        final_src_filename = src_filename if src_filename else result.suggested_src_filename
        
        # 為了配合 dspy 的回傳格式，我們手動塞一個屬性回去，或者直接依賴 result
        # 這裡我們利用 Python 動態特性，把 src_filename 掛在 result 上回傳給 Manager
        result.src_filename = final_src_filename
        
        return result