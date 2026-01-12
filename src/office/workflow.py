from langgraph.graph import StateGraph, END
from src.agents.code_agent import CoderAgent
from src.agents.qa_agent import QAAgent
from src.office.state import OfficeState

# --- 1. 實例化 DSPy 員工 (他們現在坐在位子上了) ---
coder = CoderAgent()
qa = QAAgent()

# --- 2. 定義節點 (Nodes - 實際發生的工作) ---

def coder_node(state: OfficeState):
    print(f"\n👨‍💻 Coder 正在工作... (第 {state['revision_count'] + 1} 次嘗試)")
    
    # 呼叫 DSPy 員工
    result = coder(
        requirement=state['requirement'],
        prev_code=state['source_code'],
        feedback=state['test_result']
    )
    
    # 更新卷宗
    return {
        "source_code": result.output_code,
        "revision_count": state['revision_count'] + 1
    }

def qa_node(state: OfficeState):
    print("\n🕵️‍♀️ QA 正在撰寫測試...")
    
    # 呼叫 DSPy 員工
    result = qa(
        requirement=state['requirement'],
        source_code=state['source_code']
    )
    
    return {"test_code": result.test_code}

def test_runner_node(state: OfficeState):
    print("\n🏃 正在執行測試 (模擬)...")
    # 這裡未來會接真正的 subprocess 執行 pytest
    # 現在我們先模擬：如果 code 裡有 "def" 就當作過，否則失敗
    if "def" in state['source_code']:
        print("✅ 測試通過！")
        return {"test_result": "PASS"}
    else:
        print("❌ 測試失敗！")
        return {"test_result": "Syntax Error: Missing def"}

# --- 3. 定義邏輯 (Edges - 決定文件怎麼送) ---

def should_continue(state: OfficeState):
    if state['test_result'] == "PASS":
        return "end" # 驗收通過
    elif state['revision_count'] > 3:
        print("⚠️ 達到最大重試次數，人工介入。")
        return "end" # 避免無限迴圈
    else:
        return "retry" # 退回給 Coder 重修

# --- 4. 組裝辦公室 (Graph) ---

def build_office():
    workflow = StateGraph(OfficeState)
    
    # 增加座位 (Nodes)
    workflow.add_node("coder", coder_node)
    workflow.add_node("qa", qa_node)
    workflow.add_node("runner", test_runner_node)
    
    # 設定流程 (Flow)
    workflow.set_entry_point("coder") # 需求一進來先給 Coder
    
    workflow.add_edge("coder", "qa")  # Code 寫完給 QA
    workflow.add_edge("qa", "runner") # Test 寫完跑測試
    
    # 條件判斷
    workflow.add_conditional_edges(
        "runner",
        should_continue,
        {
            "end": END,
            "retry": "coder" # 失敗了，文件退回給 Coder
        }
    )
    
    return workflow.compile()