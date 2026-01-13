from config import config
from office.office_manager import OfficeManager
import warnings

# 過濾掉 Pydantic 的序列化警告 (眼不見為淨)
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

config.initialize_dspy()

def main():
    manager = OfficeManager()
    salary_partners = manager.compile_graph()

    initial_state = {
        "requirement": "寫一個 Python 函數計算費波那契數列的第 n 項",
        "revision_count": 0
    }

    print("🚀 SalaryPartners 辦公室啟動中...")
    final_state = salary_partners.invoke(initial_state)

    print("\n" + "="*30)
    print("🎉 最終交付成果：")
    print(f"檔案：{final_state.get('file_name')}")
    print("程式碼已寫入 playground/")

if __name__ == "__main__":
    main()