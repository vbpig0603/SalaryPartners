from config import config
from office.office_manager import OfficeManager
import warnings

# 過濾掉 Pydantic 的序列化警告 (眼不見為淨)
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

lm = config.initialize_dspy()

def main():
    manager = OfficeManager(lm)
    salary_partners = manager.compile_graph()
    
    user_req = "實作一個購物車折扣計算器，支援滿千送百和 VIP 9折"
    augment_context = """
    [Augment Suggestion]
    建議使用 Strategy Pattern 實作折扣策略。
    
    Class Diagram:
    - Interface: DiscountStrategy (method: apply_discount(original_price: float) -> float)
    - Concrete: ThresholdDiscount (滿額折抵)
    - Concrete: VipDiscount (VIP 折扣)
    - Context: ShoppingCart (method: calculate_total())
    
    Filename: discount_system.py
    """

    initial_state = {
        "requirement": user_req,
        "augment_context": augment_context, # ✅ 注入外部智慧
        "qa_revision_count": 0,
        "coder_revision_count": 0
    }

    print("🚀 SalaryPartners 辦公室啟動中...")
    final_state = salary_partners.invoke(initial_state)

    print("\n" + "="*30)
    print("🎉 最終交付成果：")
    print(f"檔案：{final_state.get('file_name')}")
    print("程式碼已寫入 playground/")

if __name__ == "__main__":
    main()