from config import init_dspy
from office.office_manager import OfficeManager

# 1. 初始化 DSPy 設定
init_dspy(provider="gemini") 

def main():
    # 2. 聘請一位辦公室經理 (實例化 Class)
    manager = OfficeManager()
    
    # 3. 請經理把辦公室流程架設好 (Compile Graph)
    salary_partners = manager.compile_graph()

    # 4. 指派任務
    initial_state = {
        "requirement": "寫一個 Python 函數計算費波那契數列的第 n 項",
        "revision_count": 0
    }

    print("🚀 SalaryPartners 辦公室啟動中...")
    
    # 5. 開始運作
    final_state = salary_partners.invoke(initial_state)

    print("\n" + "="*30)
    print("🎉 最終交付成果：")
    print(f"檔案：{final_state.get('file_name')}")
    print("程式碼已寫入 playground/")

if __name__ == "__main__":
    main()