import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
import tree_sitter_typescript as tstypescript
from tree_sitter import Language, Parser

class ASTParser:
    def __init__(self):
        self.parsers = {}
        
        # Carrega Gramática Python
        self.parsers["python"] = Parser(Language(tspython.language()))
        
        # Carrega Gramática JavaScript
        self.parsers["javascript"] = Parser(Language(tsjavascript.language()))
        
        # Carrega Gramáticas TypeScript / TSX
        self.parsers["typescript"] = Parser(Language(tstypescript.language_typescript()))
        self.parsers["tsx"] = Parser(Language(tstypescript.language_tsx()))

    def _safe_decode(self, source: bytes, start: int, end: int) -> str:
        try:
            return source[start:end].decode("utf-8", errors="ignore")
        except Exception:
            return ""

    def extract_structure(self, source_code: bytes, lang: str) -> dict:
        parser = self.parsers.get(lang)
        if not parser:
            return {"classes": [], "functions": [], "tests": [], "imports": []}

        tree = parser.parse(source_code)
        root = tree.root_node

        structure = {"classes": [], "functions": [], "tests": [], "imports": []}
        visited = set()

        def traverse(node, current_class=None, current_function=None):
            node_id = (node.start_byte, node.end_byte)
            if node_id in visited: return
            visited.add(node_id)

            node_type = node.type

            # 1. IMPORTS (Poliglota: Python, JS, TS)
            if node_type in ["import_statement", "import_from_statement"]:
                module_name = ""
                symbols = []
                # Tenta capturar o módulo no estilo JS/TS (node do tipo string)
                for child in node.children:
                    if child.type == "string":
                        module_name = self._safe_decode(source_code, child.start_byte, child.end_byte).strip("'\"")
                
                # Fallback para estilo Python se module_name estiver vazio
                if not module_name:
                    module_node = node.child_by_field_name("module_name")
                    if module_node:
                        module_name = self._safe_decode(source_code, module_node.start_byte, module_node.end_byte)

                if module_name:
                    structure["imports"].append({"module": module_name, "symbols": symbols})

            # 2. CLASSES (Poliglota)
            elif node_type in ["class_definition", "class_declaration"]:
                name_node = node.child_by_field_name("name")
                if name_node:
                    class_name = self._safe_decode(source_code, name_node.start_byte, name_node.end_byte)
                    structure["classes"].append({
                        "name": class_name,
                        "code": self._safe_decode(source_code, node.start_byte, node.end_byte),
                        "start_line": node.start_point[0] + 1,
                        "end_line": node.end_point[0] + 1
                    })
                    for child in node.children:
                        traverse(child, current_class=class_name)
                    return

            # 3. FUNÇÕES E MÉTODOS (Poliglota)
            elif node_type in ["function_definition", "function_declaration", "method_definition"]:
                name_node = node.child_by_field_name("name")
                if name_node:
                    raw_name = self._safe_decode(source_code, name_node.start_byte, name_node.end_byte)
                    qualified = f"{current_class}.{raw_name}" if current_class else raw_name
                    
                    func_data = {
                        "name": qualified,
                        "raw_name": raw_name,
                        "calls": [],
                        "code": self._safe_decode(source_code, node.start_byte, node.end_byte),
                        "start_line": node.start_point[0] + 1,
                        "end_line": node.end_point[0] + 1 
                    }

                    for child in node.children:
                        traverse(child, current_class, func_data)

                    if raw_name.startswith("test_") or "test" in raw_name.lower():
                        structure["tests"].append(func_data)
                    else:
                        structure["functions"].append(func_data)
                    return

            # 4. CHAMADAS (Poliglota: call ou call_expression no JS/TS)
            elif node_type in ["call", "call_expression"]:
                func_node = node.child_by_field_name("function")
                if func_node and current_function:
                    call_text = self._safe_decode(source_code, func_node.start_byte, func_node.end_byte)
                    call_name = call_text.split(".")[-1]
                    if not call_name.startswith("__"):
                        current_function["calls"].append(call_name)

            for child in node.children:
                traverse(child, current_class, current_function)

        traverse(root)
        return structure