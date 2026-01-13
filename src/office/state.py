from typing import TypedDict, Optional, List

# 這就是我們在辦公室裡傳遞的「公文夾」
class OfficeState(TypedDict):
    # 原始需求
    requirement: str
    
    # 目前產出的程式碼
    file_name: Optional[str]
    source_code: Optional[str]
    test_file_name: Optional[str]
    
    # 目前產出的測試程式碼
    test_code: Optional[str]
    
    # 測試執行結果 (例如: "Passed" 或 錯誤訊息)
    test_result: Optional[str]
    
    # 迴圈次數 (避免 Agent 修不好陷入無窮迴圈)
    revision_count: int
    
    # 下一步該誰做 (用來決定路由)
    next_step: str

    last_worker: str