from typing import List, Optional
from pydantic import BaseModel, Field

class FunctionSchema(BaseModel):
    name: str
    args: List[str] = Field(description="參數列表，例如 ['self', 'price: float']")
    return_type: str = Field(description="回傳型別，例如 'float'", default="None")
    docstring: str = Field(description="函式說明", default="")
    is_async: bool = False

class ClassSchema(BaseModel):
    name: str
    parent_class: Optional[str] = Field(default=None)
    methods: List[FunctionSchema] = []
    docstring: str = ""

class FileSchema(BaseModel):
    filename: str
    imports: List[str] = Field(description="需要的 import 語句列表", default=[])
    classes: List[ClassSchema] = []
    functions: List[FunctionSchema] = [] # 支援全域函式