import dspy

class WriteTestSignature(dspy.Signature):
    """
    [TDD Red Phase]
    根據需求，先定義測試案例。
    如果還沒有 Source Code，請根據需求與檔名自行推斷 Import 寫法。
    """
    requirement = dspy.InputField(desc="功能需求")
    technical_spec = dspy.InputField(desc="架構師制定的技術規格 (包含 Class/Method 定義)")
    error_feedback = dspy.InputField(desc="上次執行測試發生的錯誤訊息 (若無則為空)", default="")
    
    ip_code = dspy.InputField(desc="目前產品程式碼", default="")
    it_code = dspy.InputField(desc="目前測試程式碼", default="")
    last_ot_code = dspy.InputField(desc="上次生成的測試骨架代碼 (若有)", default="")

    # Outputs
    ot_code = dspy.OutputField(desc="輸出的測試程式碼")

class QAAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.prog = dspy.ChainOfThought(WriteTestSignature)
    
    def forward(self, requirement, technical_spec, error_feedback, ip_code,
                it_code, last_ot_code):
        
        safe_spec = technical_spec if technical_spec else "無規格書，請自行發揮"
        ip_code = ip_code if ip_code else "尚無實作"
        it_code = it_code if it_code else "尚無實作"
        last_ot_code = last_ot_code if last_ot_code else "無上次測試代碼"

        result = self.prog(
            requirement=requirement,
            technical_spec=safe_spec,
            error_feedback=error_feedback,
            ip_code=ip_code,
            it_code=it_code,
            last_ot_code=last_ot_code,
        )
        
        return result