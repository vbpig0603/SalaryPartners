from typing import TypedDict, Optional

class OfficeState(TypedDict):
    requirement: str

    augment_context: Optional[str]
    technical_spec: Optional[str]
    
    # "init" -> "scaffold" -> "qa_assertion" -> "coding"
    phase: str

    p_filepath: Optional[str]
    t_filepath: Optional[str]

    p_filepath_scaffolder: Optional[str]
    t_filepath_scaffolder: Optional[str]
    t_filepath_qa: Optional[str]
    p_filepath_coder: Optional[str]

    scaffolder_revision_count: int
    qa_revision_count: int
    coder_revision_count: int

    test_result_status: Optional[str] # "PASS" | "FAIL" | "ERROR"
    test_message: Optional[str]

    next_step: str
    last_worker: str