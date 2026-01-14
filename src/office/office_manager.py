from datetime import datetime
from pathlib import Path
from langgraph.graph import StateGraph, END
import dspy
from src.agents.scaffolder_agent import ScaffolderAgent
from src.agents.qa_agent import QAAgent
from src.agents.code_agent import CoderAgent
from src.agents.architect_agent import ArchitectAgent
from src.office.state import OfficeState
from src.tools.file_ops import FileOps
from src.tools.test_runner import TestRunner
from src.utils.code_generator import CodeGenerator

class OfficeManager:
    def __init__(self, lm: dspy.LM):
        """
        辦公室初始化：在這裡聘用員工 (Agents) 與採購工具 (Tools)
        """
        self.lm = lm
        self.input_pricing_per_m_token = 0.5
        self.output_pricing_per_m_token = 3
        print("🏢 SalaryPartners 辦公室正在開張...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 聘用員工 (DSPy Modules)
        self.scaffolder = ScaffolderAgent()
        self.qa = QAAgent()
        self.coder = CoderAgent()
        self.architect = ArchitectAgent()
        
        # 實例化工具
        playground_dir = f"playground/{timestamp}"
        Path(playground_dir).mkdir(parents=True, exist_ok=True)
        self.file_ops = FileOps(base_dir=playground_dir)
        self.runner = TestRunner(playground_dir=playground_dir)

    def print_last_asking(self):
        last_call = self.lm.history[-1]
        print(last_call.keys())
        cost_from_server = last_call['cost']
        input_token = last_call['usage']['prompt_tokens']
        input_cost = input_token * self.input_pricing_per_m_token / 1000000
        output_token = last_call['usage']['completion_tokens']
        output_cost = output_token * self.output_pricing_per_m_token / 1000000
        total_token = last_call['usage']['total_tokens']
        total_cost = input_cost + output_cost
        print(f"    Cost from server: {cost_from_server}")
        print(f"    Input Tokens: {input_token}(NT$ {input_cost:.4f})")
        print(f"    Output Tokens: {output_token}(NT$ {output_cost:.4f})")
        print(f"    Total Tokens: {total_token}(NT$ {total_cost:.4f})")


    # --- 節點方法 (Node Methods) ---
    def architect_work(self, state: OfficeState):
        """[Step 0] 架構師分析需求與外部 Context"""
        print("\n🏗️ Architect 正在分析架構 (Analyzing Context)...")
        
        result = self.architect(
            requirement=state['requirement'],
            augment_context=state.get('augment_context')
        )
        
        p_filepath = Path(result.p_filepath)
        spec_filepath = p_filepath.name + ".spec"
        print(f"    -> 規格書存放在: {spec_filepath}")
        self.file_ops.save(spec_filepath, result.technical_spec)

        print(f"    -> 決定產品檔案名稱: {p_filepath.name}")
        t_filepath = "test_" + p_filepath.name
        print(f"    -> 決定測試檔案名稱: {t_filepath}")
        p_filepath_scaffolder = p_filepath.stem + ".scaffolder" + p_filepath.suffix
        t_filepath_scaffolder = "test_" + p_filepath.stem + ".scaffolder" + p_filepath.suffix
        t_filepath_qa = "test_" + p_filepath.stem + ".qa" + p_filepath.suffix
        p_filepath_coder = p_filepath.stem + ".coder" + p_filepath.suffix
        print("    -> 規格書已生成。")
        self.print_last_asking()
        
        return {
            "technical_spec": result.technical_spec,
            "p_filepath": p_filepath.name,
            "t_filepath": t_filepath,
            "p_filepath_scaffolder": p_filepath_scaffolder,
            "t_filepath_scaffolder": t_filepath_scaffolder,
            "t_filepath_qa": t_filepath_qa,
            "p_filepath_coder": p_filepath_coder,
            "last_worker": "architect",
            "phase": "init"
        }

    # --- Node 2: 鷹架工 (Scaffolder) ---
    def scaffolder_work(self, state: OfficeState):
        current_round = state.get('scaffolder_revision_count', 0) + 1
        print(f"\n🏗️ Scaffolder 正在規劃結構 (JSON Mode) (第 {current_round} 次嘗試)...")
        
        # 1. AI 思考結構 (取得 Pydantic 物件)
        result = self.scaffolder(
            requirement=state['requirement'],
            technical_spec=state['technical_spec']
        )
        prod_schema = result.product_structure
        test_schema = result.test_structure
        
        p_filepath_scaffolder = state.get('p_filepath_scaffolder')
        t_filepath_scaffolder = state.get('t_filepath_scaffolder')
        
        p_json_path = f"{p_filepath_scaffolder}.json.{current_round}"
        t_json_path = f"{t_filepath_scaffolder}.json.{current_round}"
        
        self.file_ops.save(p_json_path, prod_schema.model_dump_json(indent=2))
        self.file_ops.save(t_json_path, test_schema.model_dump_json(indent=2))
        print(f"    Schema JSON 已備份")

        # ---------------------------------------------------------
        # 🔗 Dependency Glue: 強制修復 Test Import
        # ---------------------------------------------------------
        
        # 取得 Product 的 module name (去掉 .py)
        prod_module_name = Path(prod_schema.filename).stem
        
        # 收集 Product 中所有需要被測試的對象 (Classes + Functions)
        export_targets = [c.name for c in prod_schema.classes] + \
                         [f.name for f in prod_schema.functions]
        
        if export_targets:
            # 建立正確的 import 語句
            # e.g., "from discount_system import ShoppingCart, DiscountStrategy"
            expected_import = f"from {prod_module_name} import {', '.join(export_targets)}"
            
            # 檢查是否已經存在 (簡單字串檢查，避免重複)
            # 這裡比較寬鬆，只要 test_schema 的 imports 裡沒有這個字串就加進去
            # 為了保險，我們直接加進去，重複的 import Python 不會報錯，black 會幫忙整理
            is_imported = any(prod_module_name in imp for imp in test_schema.imports)
            
            if not is_imported:
                print(f"    (Auto-Fix) 發現測試檔缺少 Import，自動補上: {expected_import}")
                test_schema.imports.append(expected_import)

        print("    -> 結構生成完畢，正在轉譯為 Python Code...")

        # 2. Rule-based 生成程式碼 (AST)
        product_code = CodeGenerator.generate_product_code(prod_schema)
        test_code = CodeGenerator.generate_test_code(test_schema)

        # 3. 存檔
        self.file_ops.save(p_filepath_scaffolder, product_code)
        self.file_ops.save(t_filepath_scaffolder, test_code)

        # 4. 備份 (for debug)
        self.file_ops.save(p_filepath_scaffolder + f".{current_round}", product_code)
        self.file_ops.save(t_filepath_scaffolder + f".{current_round}", test_code)
        
        print("    -> 鷹架已生成。")
        self.print_last_asking()

        state["scaffolder_revision_count"] = current_round
        state["last_worker"] = "scaffolder"
        state["phase"] = "scaffold"
        
        return state
    
    # --- Node 3: QA (填入真實斷言) ---
    def qa_work(self, state: OfficeState):
        """[Phase: Red] 把 assert True 改成真的測試"""
        current_round = state.get('qa_revision_count', 0) + 1
        print(f"\n🕵️‍♀️ QA 正在實作測試斷言 (第 {current_round} 次嘗試) (Red Phase)...")

        # 讀取現有檔案 (支援 Refactoring)
        p_filepath = state.get('p_filepath')
        ip_code = self.file_ops.read(p_filepath) if p_filepath else ""
        t_filepath = state.get('t_filepath')
        it_code = self.file_ops.read(t_filepath) if p_filepath else ""
        t_filepath_qa = state.get('t_filepath_qa')
        last_ot_code = self.file_ops.read(t_filepath_qa) if t_filepath_qa else ""

        error_feedback = state.get('test_message') \
            if state.get('test_result_status') == "ERROR" else ""
        
        # 傳入目前的骨架
        result = self.qa(
            requirement=state['requirement'],
            technical_spec=state['technical_spec'],
            error_feedback=error_feedback,
            ip_code=ip_code,
            it_code=it_code,
            last_ot_code=last_ot_code
        )

        # 存檔
        self.file_ops.save(t_filepath_qa, result.ot_code)
        # 備份 (for debug)
        self.file_ops.save(t_filepath_qa + f".{current_round}", result.ot_code)

        print("    -> 測試碼已生成。")
        self.print_last_asking()

        state["qa_revision_count"] = current_round
        state["last_worker"] = "qa"
        state["phase"] = "qa_assertion"
        
        return state

    def coder_work(self, state: OfficeState):
        """[Step 3] Coder 根據失敗結果寫程式 (Green Phase)"""
        current_round = state.get('coder_revision_count', 0) + 1
        print(f"\n👨‍💻 Coder 正在實作... (第 {current_round} 次嘗試)")

        p_filepath = state.get('p_filepath')
        ip_code = self.file_ops.read(p_filepath) if p_filepath else ""
        p_filepath_coder = state.get('p_filepath_coder')
        last_op_code = self.file_ops.read(p_filepath_coder) if p_filepath_coder else ""
        t_filepath = state.get('t_filepath')
        it_code = self.file_ops.read(t_filepath) if p_filepath else ""

        # 呼叫 Coder，給予錯誤訊息回饋
        result = self.coder(
            requirement=state['requirement'],
            technical_spec=state['technical_spec'],
            feedback=state.get('test_message'),
            ip_code=ip_code,
            last_op_code=last_op_code,
            it_code=it_code
        )
        
        # 存檔
        self.file_ops.save(p_filepath_coder, result.op_code)
        # 備份 (for debug)
        self.file_ops.save(p_filepath_coder + f".{current_round}", result.op_code)

        print("    -> 程式碼已生成。")
        self.print_last_asking()

        state["coder_revision_count"] = current_round
        state["last_worker"] = "coder"
        state["phase"] = "coding"
        
        return state

    def run_tests(self, state: OfficeState):
        print("\n🏃 正在執行測試...")
        phase = state.get('phase')
        p_filepath = state.get('p_filepath')
        t_filepath = state.get('t_filepath')
        is_p_filepath_bak = False
        is_t_filepath_bak = False
        if phase == "scaffold":
            if self.file_ops.exists(p_filepath):
                self.file_ops.backup(p_filepath)
                is_p_filepath_bak = True
            if self.file_ops.exists(t_filepath):
                self.file_ops.backup(t_filepath)
                is_t_filepath_bak = True

            p_filepath_new = state.get('p_filepath_scaffolder')
            t_filepath_new = state.get('t_filepath_scaffolder')
            self.file_ops.copy(p_filepath_new, p_filepath)
            self.file_ops.copy(t_filepath_new, t_filepath)
        elif phase == "qa_assertion":
            if self.file_ops.exists(t_filepath):
                self.file_ops.backup(t_filepath)
                is_t_filepath_bak = True

            t_filepath_new = state.get('t_filepath_qa')
            self.file_ops.copy(t_filepath_new, t_filepath)
        elif phase == "coding":
            if self.file_ops.exists(p_filepath):
                self.file_ops.backup(p_filepath)
                is_p_filepath_bak = True

            p_filepath_new = state.get('p_filepath_coder')
            self.file_ops.copy(p_filepath_new, p_filepath)

        if not t_filepath:
            return {"test_result_status": "ERROR", "test_result": "No Test File"}

        # ✅ 取得 status 和 message
        status, message = self.runner.run(t_filepath)
        
        if status == "PASS":
            print("✅ 測試通過 (Green)!")
        else:
            if is_p_filepath_bak:
                self.file_ops.restore(p_filepath + ".bak")
            else:
                self.file_ops.unlink(p_filepath)
            if is_t_filepath_bak:
                self.file_ops.restore(t_filepath + ".bak")
            else:
                self.file_ops.unlink(t_filepath)

            if status == "FAIL":
                print("🔴 測試斷言失敗")
                print(message)
            else:
                print("💥 測試執行錯誤 (Syntax/Import Error)")
                print(message)

        state["test_result_status"] = status
        state["test_result_message"] = message

        return state

    # --- 流程邏輯 (Router) ---
    def check_results(self, state: OfficeState):
        status = state.get('test_result_status')
        phase = state.get('phase')

        print(f"   [Router] Phase: {phase}, Status: {status}")
        # ------------------------------------------------
        # 🔵 Phase 1: Scaffold (骨架驗收)
        # 目標：必須 PASS。如果有任何 Error，代表骨架搭錯了 (Import Error)。
        # ------------------------------------------------
        if phase == "scaffold":
            scaffolder_revision = state.get('scaffolder_revision_count', 0)
            if status != "PASS":
                if scaffolder_revision >= 2:
                    print("⚠️ 達到最大重試次數，停止工作。")
                    return "end"
                print("💥 骨架驗證失敗 (Import/Syntax Error)！退回重搭。")
                return "to_scaffolder"
            print("🔵 骨架驗證通過！交給 QA 寫斷言。")
            return "to_qa"

        # ------------------------------------------------
        # 🔴 Phase 2: QA Assertion (測試驗收)
        # 目標：必須 FAIL (AssertionError)。如果是 PASS，代表測試沒寫好(太鬆)；如果是 ERROR，代表語法錯。
        # ------------------------------------------------
        if phase == "qa_assertion":
            if status == "PASS":
                # 這是很特殊的狀況：QA 寫完測試居然直接過了？
                # 1. 可能是邏輯太簡單 2. 可能是 QA 偷懶寫了 assert True
                # 在嚴格 TDD 中，這是不被允許的 (沒有 Red 就不該有 Green)
                # 但為了系統彈性，我們先假設這是「無需實作」或「已實作」
                print("🟡 [Warning] 測試在實作前就通過 (可能是既有功能或測試無效)，流程結束。")
                return "end"

            qa_revision = state.get('qa_revision_count', 0)
            if status == "ERROR":
                if qa_revision >= 5:
                    print("⚠️ 達到最大重試次數，停止工作。")
                    return "end"
                print("💥 測試碼語法錯誤！退回 QA。")
                return "to_qa"

            print("🔴 測試如預期失敗 (Red Light)！交給 Coder 實作。")
            return "to_coder"

        # ------------------------------------------------
        # 🟢 Phase 3: Coding (實作驗收)
        # 目標：必須 PASS。
        # ------------------------------------------------
        if phase == "coding" or state.get('last_worker') == "coder":
            code_revision = state.get('coder_revision_count', 0)
            if status != "PASS":
                if code_revision >= 5:
                    print("⚠️ 達到最大重試次數，停止工作。")
                    return "end"
                print("🟠 實作失敗，退回給 Coder 修正。")
                return "to_coder" # 繼續修
            return "end"

        raise NotImplementedError(f"Unknown phase: {phase}")

    # --- 建構圖表 (Graph Builder) ---
    def compile_graph(self):
        workflow = StateGraph(OfficeState)
        
        workflow.add_node("architect", self.architect_work)
        workflow.add_node("scaffolder", self.scaffolder_work)
        workflow.add_node("qa", self.qa_work)
        workflow.add_node("coder", self.coder_work)

        workflow.add_node("runner", self.run_tests)
        
        workflow.set_entry_point("architect")

        workflow.add_edge("architect", "scaffolder")
        workflow.add_edge("scaffolder", "runner")
        
        workflow.add_conditional_edges(
            "runner",
            self.check_results,
            {
                "to_scaffolder": "scaffolder", # 骨架壞掉
                "to_qa": "qa",                 # 骨架好了，去寫測試
                "to_coder": "coder",           # 測試紅燈，去寫Code
                "end": END
            }
        )

        workflow.add_edge("qa", "runner")
        workflow.add_edge("coder", "runner")
        
        return workflow.compile()