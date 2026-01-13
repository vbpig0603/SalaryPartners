from langgraph.graph import StateGraph, END
from src.agents.code_agent import CoderAgent
from src.agents.qa_agent import QAAgent
from src.office.state import OfficeState
from src.tools.file_ops import FileOps
from src.tools.test_runner import TestRunner

class OfficeManager:
    def __init__(self):
        """
        辦公室初始化：在這裡聘用員工 (Agents) 與採購工具 (Tools)
        """
        print("🏢 SalaryPartners 辦公室正在開張...")
        
        # 聘用員工 (DSPy Modules)
        self.coder = CoderAgent()
        self.qa = QAAgent()
        
        # 實例化工具
        self.file_ops = FileOps(base_dir="playground")
        self.runner = TestRunner(playground_dir="playground")

    # --- 節點方法 (Node Methods) ---
    
    def qa_work(self, state: OfficeState):
        """[Step 1] QA 先寫測試 (TDD Red Phase)"""
        print("\n🕵️‍♀️ QA 正在撰寫測試 (TDD Red Phase)...")
        
        # 第一次還沒有 source_code，傳空字串，QA 必須憑空設計介面
        result = self.qa(
            requirement=state['requirement'],
            source_code=state.get('source_code', ""),
            src_filename=state.get('file_name', "") 
        )
        
        # 存檔
        self.file_ops.save(result.test_file_name, result.test_code)
        
        return {
            "test_file_name": result.test_file_name,
            "test_code": result.test_code,
            "file_name": result.src_filename, # QA 決定的實作檔名
            "last_worker": "qa" # ✅ 標記：這棒是 QA 跑的
        }

    def coder_work(self, state: OfficeState):
        """[Step 3] Coder 根據失敗結果寫程式 (Green Phase)"""
        current_round = state.get('revision_count', 0) + 1
        print(f"\n👨‍💻 Coder 正在實作... (第 {current_round} 次嘗試)")
        
        # Coder 必須使用 QA 指定的檔名 (從 state 取得)
        target_filename = state.get('file_name')
        
        # 呼叫 Coder，給予錯誤訊息回饋
        result = self.coder(
            requirement=state['requirement'],
            prev_code=state.get('source_code'),
            feedback=state.get('test_result')
        )
        
        # 如果 Coder 自己決定了新檔名，我們還是優先尊重 state 裡的 (保持一致性)，除非 state 裡沒有
        final_filename = target_filename or result.file_name
        
        # 存檔
        self.file_ops.save(final_filename, result.output_code)
        
        return {
            "file_name": final_filename,
            "source_code": result.output_code,
            "revision_count": current_round,
            "last_worker": "coder" # ✅ 標記：這棒是 Coder 跑的
        }

    def run_tests(self, state: OfficeState):
        """執行測試 (真實 Pytest)"""
        print("\n🏃 正在執行測試...")
        
        test_file = state.get('test_file_name')
        
        if not test_file:
            print("⚠️ 找不到測試檔名，跳過測試")
            return {"test_result": "No Test File"}

        # 呼叫 TestRunner 工具
        # is_passed (bool): 是否通過
        # message (str): PASS 或 錯誤訊息(stdout/stderr)
        is_passed, message = self.runner.run(test_file)
        
        if is_passed:
            print("✅ 測試通過！")
            return {"test_result": "PASS"}
        else:
            print("❌ 測試失敗！")
            return {"test_result": message}

    # --- 流程邏輯 (Router) ---

    def check_results(self, state: OfficeState):
        """
        TDD 核心路由邏輯：
        1. 通過 -> 結束
        2. 失敗且上一棒是 QA -> 這是 Red Phase (好事) -> 給 Coder
        3. 失敗且上一棒是 Coder -> 這是 Bug (壞事) -> 給 Coder 重修
        """
        result = state.get('test_result')
        last_worker = state.get('last_worker')
        
        # 情況 A: 測試通過 -> 大家都開心 -> 結案
        if result == "PASS":
            return "end"
        
        # 情況 B: 測試失敗，且上一棒是 QA -> 這是「預期中的失敗 (Red Phase)」 -> 叫 Coder 寫 code
        if result != "PASS" and last_worker == "qa":
            print("🔴 TDD Red Phase: 測試如預期失敗 (或還沒實作)，交給 Coder 實作。")
            return "to_coder"
            
        # 情況 C: 測試失敗，且上一棒是 Coder -> 這是「真的寫爛了」 -> 叫 Coder 重寫 (Retry)
        if result != "PASS" and last_worker == "coder":
            if state.get('revision_count', 0) > 3:
                print("⚠️ 達到最大重試次數，停止工作。")
                return "end"
            print("🟠 測試失敗，退回給 Coder 修正。")
            return "to_coder"
            
        # 預設結束 (避免死路)
        return "end"

    # --- 建構圖表 (Graph Builder) ---

    def compile_graph(self):
        workflow = StateGraph(OfficeState)
        
        # 註冊節點
        workflow.add_node("qa", self.qa_work)
        workflow.add_node("runner", self.run_tests)
        workflow.add_node("coder", self.coder_work)
        
        # 1. 設定流程起點：QA 先寫測試
        workflow.set_entry_point("qa")
        
        # 2. QA 寫完 -> 跑測試 (驗證紅燈)
        workflow.add_edge("qa", "runner")
        
        # 3. 跑完測試 -> 判斷去哪
        workflow.add_conditional_edges(
            "runner",
            self.check_results,
            {
                "end": END,         # 測試通過或放棄 -> 結束
                "to_coder": "coder" # 需要實作或修復 -> Coder
            }
        )
        
        # 4. Coder 寫完 -> 再跑測試 (驗證綠燈)
        workflow.add_edge("coder", "runner")
        
        return workflow.compile()