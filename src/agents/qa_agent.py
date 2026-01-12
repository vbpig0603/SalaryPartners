import dspy

class WriteTestSignature(dspy.Signature):
    """根據功能需求與實作碼，撰寫 Pytest 測試案例。"""
    requirement = dspy.InputField()
    source_code = dspy.InputField()
    test_file_name = dspy.OutputField(desc="建議的測試檔案名稱 (例如: 'test_fibonacci.py')")
    test_code = dspy.OutputField(desc="Pytest 測試程式碼")

class QAAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.prog = dspy.ChainOfThought(WriteTestSignature)

    def forward(self, requirement, source_code):
        return self.prog(requirement=requirement, source_code=source_code)