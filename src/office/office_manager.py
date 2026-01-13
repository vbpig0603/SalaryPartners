from langgraph.graph import StateGraph, END
from src.agents.code_agent import CoderAgent
from src.agents.qa_agent import QAAgent
from src.office.state import OfficeState
from src.tools.file_ops import save_to_playground

class OfficeManager:
    def __init__(self):
        """
        辦公室初始化：在這裡聘用員工 (實例化 DSPy Agents)
        """
        print("🏢 SalaryPartners 辦公室正在開張...")
        self.coder = CoderAgent()
        self.qa = QAAgent()

    # --- 節點方法 (Node Methods) ---
    
    def coder_work(self, state: OfficeState):
        """Coder 員工的工作內容"""
        current_round = state.get('revision_count', 0) + 1
        print(f"\n👨‍💻 Coder 正在工作... (第 {current_round} 次嘗試)")
        
        # 呼叫 DSPy 員工 (self.coder)
        result = self.coder(
            requirement=state['requirement'],
            prev_code=state.get('source_code'),
            feedback=state.get('test_result')
        )
        
        # 使用工具存檔
        save_to_playground(result.file_name, result.output_code)
        
        return {
            "file_name": result.file_name,
            "source_code": result.output_code,
            "revision_count": current_round
        }

    def qa_work(self, state: OfficeState):
        """QA 員工的工作內容"""
        print("\n🕵️‍♀️ QA 正在撰寫測試...")
        
        # 呼叫 DSPy 員工 (self.qa)
        result = self.qa(
            requirement=state['requirement'],
            source_code=state['source_code']
        )
        
        # 使用工具存檔
        save_to_playground(result.test_file_name, result.test_code)
        
        return {
            "test_file_name": result.test_file_name,
            "test_code": result.test_code
        }

    def run_tests(self, state: OfficeState):
        """執行測試 (目前是模擬，下一步接真實 subprocess)"""
        print("\n🏃 正在執行測試 (模擬)...")
        
        # 模擬邏輯：只要有 def 就給過
        if "def" in state['source_code']:
            print("✅ 測試通過！")
            return {"test_result": "PASS"}
        else:
            print("❌ 測試失敗！")
            return {"test_result": "Syntax Error: Missing def"}

    # --- 流程邏輯 (Conditional Logic) ---

    def check_results(self, state: OfficeState):
        """決定下一步該怎麼走 (Router)"""
        if state.get('test_result') == "PASS":
            return "end"
        elif state.get('revision_count', 0) > 3:
            print("⚠️ 達到最大重試次數，停止工作。")
            return "end"
        else:
            return "retry"

    # --- 建構圖表 (Graph Builder) ---

    def compile_graph(self):
        """組裝辦公室流程圖"""
        workflow = StateGraph(OfficeState)
        
        # 註冊節點 (綁定到 self 的方法)
        workflow.add_node("coder", self.coder_work)
        workflow.add_node("qa", self.qa_work)
        workflow.add_node("runner", self.run_tests)
        
        # 設定流程
        workflow.set_entry_point("coder")
        
        workflow.add_edge("coder", "qa")
        workflow.add_edge("qa", "runner")
        
        # 設定條件路由
        workflow.add_conditional_edges(
            "runner",
            self.check_results,
            {
                "end": END,
                "retry": "coder"
            }
        )
        
        return workflow.compile()