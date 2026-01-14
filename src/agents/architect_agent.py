import dspy

class ArchitectSignature(dspy.Signature):
    """
    [Role: Software Architect]
    分析用戶需求與 Augment Code 提供的上下文(UML/Context)，
    制定詳細的實作規格書 (Technical Specification)。
    
    規格書必須包含：
    1. 建議的檔案名稱 (Filename)
    2. 類別與函式簽章 (Class/Function Signatures)
    3. 輸入與輸出型別 (Input/Output Types)
    4. 邏輯依賴關係
    """
    requirement = dspy.InputField(desc="用戶的功能需求")
    augment_context = dspy.InputField(desc="來自外部工具 (Augment/Copilot) 的架構建議或 UML")
    
    # Outputs
    technical_spec = dspy.OutputField(desc="給 QA 與 Coder 看的詳細開發規格書 (Markdown 格式)")
    p_filepath = dspy.OutputField(desc="實作檔案名稱 (例如: 'order_service.py')")

class ArchitectAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.prog = dspy.ChainOfThought(ArchitectSignature)
    
    def forward(self, requirement, augment_context):
        return self.prog(
            requirement=requirement,
            augment_context=augment_context or "無外部上下文，請根據需求自行設計架構。"
        )