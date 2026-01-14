import dspy
from src.utils.schema import FileSchema

class ScaffolderSignature(dspy.Signature):
    """
    [Role: Scaffolder]
    將 Technical Spec 轉換為結構化的程式碼骨架 (JSON)。
    
    任務：
    1. 分析 Spec，找出需要的 Import、Class、Method。
    2. 輸出符合結構的 JSON 資料。
    3. 不涉及任何實作邏輯，只定義介面。
    """
    requirement = dspy.InputField()
    technical_spec = dspy.InputField()
    # ip_code = dspy.InputField(desc="現有的產品代碼 (若有)", default="")
    # it_code = dspy.InputField(desc="現有的測試代碼 (若有)", default="")
    # last_op_code = dspy.InputField(desc="上次生成的產品骨架代碼 (若有)", default="")
    # last_ot_code = dspy.InputField(desc="上次生成的測試骨架代碼 (若有)", default="")
    
    product_structure: FileSchema = dspy.OutputField(desc="產品程式碼的結構定義")
    test_structure: FileSchema = dspy.OutputField(desc="測試程式碼的結構定義")

class ScaffolderAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        # DSPy 支援 Typed output
        self.prog = dspy.ChainOfThought(ScaffolderSignature)
    
    def forward(self, requirement, technical_spec):
        return self.prog(
            requirement=requirement,
            technical_spec=technical_spec
        )