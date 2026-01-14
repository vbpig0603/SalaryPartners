import dspy

class WriteCodeSignature(dspy.Signature):
    """根據需求與測試結果，撰寫或修正 Python 程式碼。"""
    # Inputs
    requirement = dspy.InputField(desc="功能需求描述")
    technical_spec = dspy.InputField(desc="架構師制定的技術規格 (包含 Class/Method 定義)")
    feedback = dspy.InputField(desc="測試失敗的錯誤訊息 (如果是 None 代表是第一次寫)")
    ip_code = dspy.InputField(desc="目前的產品程式碼")
    last_op_code = dspy.InputField(desc="上次生成的產品骨架代碼 (若有)", default="")
    it_code = dspy.InputField(desc="目前的測試程式碼")

    # Outputs
    op_code = dspy.OutputField(desc="輸出的產品程式碼")

class CoderAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.prog = dspy.ChainOfThought(WriteCodeSignature)
    
    def forward(self, requirement, technical_spec, feedback, ip_code,
                last_op_code, it_code):
        return self.prog(
            requirement=requirement,
            technical_spec=technical_spec,
            feedback=feedback or "No feedback, this is the first draft.",
            ip_code=ip_code,
            last_op_code=last_op_code,
            it_code=it_code
        )