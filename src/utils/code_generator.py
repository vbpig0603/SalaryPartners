import ast
import black
from typing import List, Optional
from src.utils.schema import FileSchema, ClassSchema, FunctionSchema

class CodeGenerator:
    """
    使用 Python AST (抽象語法樹) 來生成程式碼。
    保證產出的程式碼 100% 符合 Python 語法結構。
    """

    @staticmethod
    def _parse_annotation(type_str: str) -> Optional[ast.AST]:
        """
        將型別字串 (e.g., "List[str]", "float") 轉換為 AST 節點
        """
        if not type_str or type_str == "None":
            return None
        try:
            # mode='eval' 可以把一個表達式字串轉成 AST
            return ast.parse(type_str, mode='eval').body
        except SyntaxError:
            # 如果 AI 給了奇怪的型別字串 (e.g. "float?"), 忽略它避免炸裂
            return None

    @staticmethod
    def _create_function_node(func_schema: FunctionSchema, is_method: bool = False) -> ast.FunctionDef:
        """建立一個函式節點 (永遠只包含 pass)"""
        
        # 1. 處理參數與 Type Hint
        args_list = []
        for arg_str in func_schema.args:
            # 分割 "name: type"
            parts = arg_str.split(":")
            arg_name = parts[0].strip()
            
            annotation = None
            if len(parts) > 1:
                # 嘗試解析型別
                annotation = CodeGenerator._parse_annotation(parts[1].strip())
            
            # 若無明確型別，預設不加 (None)
            args_list.append(ast.arg(arg=arg_name, annotation=annotation))

        # 2. 處理 Return Type Hint
        return_annotation = None
        if func_schema.return_type:
            return_annotation = CodeGenerator._parse_annotation(func_schema.return_type)

        # 3. 建立 Docstring (如果有)
        body_nodes = []
        if func_schema.docstring:
            docstring_node = ast.Expr(value=ast.Constant(value=func_schema.docstring))
            body_nodes.append(docstring_node)
        
        # 4. 填入 pass (TDD Blue Phase 核心)
        body_nodes.append(ast.Pass())

        # 5. 回傳 FunctionDef 節點
        return ast.FunctionDef(
            name=func_schema.name,
            args=ast.arguments(
                posonlyargs=[],
                args=args_list,
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[]
            ),
            body=body_nodes,
            decorator_list=[],
            returns=return_annotation, # ✅ 加回 Return Type Hint
            type_comment=None
        )

    @staticmethod
    def _create_class_node(class_schema: ClassSchema) -> ast.ClassDef:
        """建立類別節點"""
        body_nodes = []
        
        if class_schema.docstring:
            body_nodes.append(ast.Expr(value=ast.Constant(value=class_schema.docstring)))

        if not class_schema.methods:
            body_nodes.append(ast.Pass())
        else:
            for method in class_schema.methods:
                body_nodes.append(CodeGenerator._create_function_node(method, is_method=True))

        bases = []
        if class_schema.parent_class:
            bases.append(ast.Name(id=class_schema.parent_class, ctx=ast.Load()))

        return ast.ClassDef(
            name=class_schema.name,
            bases=bases,
            keywords=[],
            body=body_nodes,
            decorator_list=[]
        )

    @staticmethod
    def generate_product_code(schema: FileSchema) -> str:
        """生成產品程式碼"""
        module_body = []

        # 1. Imports
        for imp in schema.imports:
            try:
                import_node = ast.parse(imp).body[0]
                module_body.append(import_node)
            except SyntaxError:
                pass 

        # 2. Classes
        for cls in schema.classes:
            module_body.append(CodeGenerator._create_class_node(cls))

        # 3. Global Functions
        for func in schema.functions:
            module_body.append(CodeGenerator._create_function_node(func))

        module = ast.Module(body=module_body, type_ignores=[])
        
        # 4. Unparse & Format
        try:
            code_str = ast.unparse(module)
        except Exception as e:
            return f"# Error generating code: {e}"

        if black:
            try:
                code_str = black.format_str(code_str, mode=black.Mode())
            except Exception as e:
                print(f"⚠️ Formatting failed: {e}")

        return code_str

    @staticmethod
    def generate_test_code(schema: FileSchema) -> str:
        """生成測試程式碼"""
        module_body = []

        # 1. Imports
        for imp in schema.imports:
            try:
                module_body.append(ast.parse(imp).body[0])
            except: pass

        # 2. Test Functions
        for func in schema.functions:
            body_nodes = []
            if func.docstring:
                body_nodes.append(ast.Expr(value=ast.Constant(value=func.docstring)))
            
            # ✅ assert True
            assert_node = ast.Assert(
                test=ast.Constant(value=True),
                msg=None
            )
            body_nodes.append(assert_node)

            func_node = ast.FunctionDef(
                name=func.name,
                args=ast.arguments(posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]),
                body=body_nodes,
                decorator_list=[]
            )
            module_body.append(func_node)

        module = ast.Module(body=module_body, type_ignores=[])
        
        try:
            code_str = ast.unparse(module)
        except Exception as e:
            return f"# Error generating code: {e}"

        if black:
            try:
                code_str = black.format_str(code_str, mode=black.Mode())
            except Exception as e:
                print(f"⚠️ Formatting failed: {e}")

        return code_str