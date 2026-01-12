from config import init_dspy
from office.workflow import build_office

# 1. 初始化 DSPy 設定
init_dspy()

# 2. 建立辦公室
salary_partners_office = build_office()

# 3. 接第一個案子 (Initial State)
initial_state = {
    "requirement": "寫一個 Python 函數計算費波那契數列的第 n 項",
    "source_code": None,
    "test_code": None,
    "test_result": None,
    "revision_count": 0,
    "next_step": None
}

print("🚀 SalaryPartners 辦公室啟動中...")
# 4. 開始運作 (Run the Graph)
final_state = salary_partners_office.invoke(initial_state)

print("\n" + "="*30)
print("🎉 最終交付成果：")
print("程式碼：")
print(final_state["source_code"])
print("\n測試碼：")
print(final_state["test_code"])