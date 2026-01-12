import dspy

class WriteCodeSignature(dspy.Signature):
    """根據需求與測試結果，撰寫或修正 Python 程式碼。"""
    requirement = dspy.InputField(desc="功能需求描述")
    prev_code = dspy.InputField(desc="目前的程式碼 (如果是修改階段)")
    feedback = dspy.InputField(desc="測試失敗的錯誤訊息 (如果是 None 代表是第一次寫)")
    output_code = dspy.OutputField(desc="完整的 Python 程式碼")

class CoderAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        # 使用 ChainOfThought 讓工程師思考架構
        self.prog = dspy.ChainOfThought(WriteCodeSignature)
    
    def forward(self, requirement, prev_code=None, feedback=None):
        return self.prog(
            requirement=requirement,
            prev_code=prev_code or "",
            feedback=feedback or "No feedback, this is the first draft."
        )