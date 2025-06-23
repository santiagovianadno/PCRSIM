#!/usr/bin/env python3
"""Minimize project: remove comments, docstrings, emojis and verbose prints.
- Makes .bak backup of each .py file.
- Removes all comments (# ...).
- Strips all docstrings (triple quoted strings at top of modules, classes or functions).
- Removes emojis from remaining strings.
- Replaces verbose stage-change prints with concise labels: "Etapa 1" .. "Etapa 4".
"""

import ast
import re
from pathlib import Path
import tokenize

EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002500-\U00002BEF\U0001F900-\U0001F9FF\u2600-\u26FF\u2700-\u27BF]",
    re.UNICODE,
)

STAGE_MAP = {
    "BASTERIA": "Etapa 0",
    "ADN": "Etapa 1",
    "ENZYME": "Etapa 2",
    "PCR": "Etapa 3",
}

UNWANTED_WORDS = {
    "Hola",
    "Inicializando",
    "Inicialización",
    "Gesto Detectado",
    "Hasta luego",
    "Zoom",
    "Separacion",
    "ATTACH",
}


def strip_emojis(text: str) -> str:
    return EMOJI_RE.sub("", text)


def simplify_print(node: ast.Call):
    # Replace verbose messages
    if not node.args:
        return node
    if isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
        msg = node.args[0].value
        for key, label in STAGE_MAP.items():
            if key in msg:
                node.args[0].value = label
                return node
        # remove unwanted prints entirely
        if any(word in msg for word in UNWANTED_WORDS):
            return None
        # strip emojis
        node.args[0].value = strip_emojis(msg)
    return node


def process_file(path: Path):
    backup = path.with_suffix(path.suffix + ".bak")
    backup.write_bytes(path.read_bytes())

    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    # Parse AST
    tree = ast.parse(source)

    class Transformer(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            node.body = self._strip_docstring(node.body)
            self.generic_visit(node)
            return node

        def visit_ClassDef(self, node):
            node.body = self._strip_docstring(node.body)
            self.generic_visit(node)
            return node

        def visit_Module(self, node):
            node.body = self._strip_docstring(node.body)
            self.generic_visit(node)
            return node

        def visit_Expr(self, node):
            # Remove standalone strings (module/class/function docstrings already handled)
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                return None
            return self.generic_visit(node)

        def visit_Call(self, node):
            if isinstance(node.func, ast.Name) and node.func.id == "print":
                new_node = simplify_print(node)
                if new_node is None:
                    return None
                return self.generic_visit(new_node)
            return self.generic_visit(node)

        @staticmethod
        def _strip_docstring(body_list):
            if body_list and isinstance(body_list[0], ast.Expr) and isinstance(body_list[0].value, ast.Constant) and isinstance(body_list[0].value.value, str):
                return body_list[1:]
            return body_list

    new_tree = Transformer().visit(tree)
    ast.fix_missing_locations(new_tree)
    new_code = ast.unparse(new_tree)

    # Remove comments using tokenize
    tokens = tokenize.generate_tokens(iter(new_code.splitlines(keepends=True)).__next__)
    cleaned = []
    for tok_type, tok_string, *_ in tokens:
        if tok_type == tokenize.COMMENT:
            continue
        if tok_type == tokenize.STRING:
            tok_string = strip_emojis(tok_string)
        cleaned.append((tok_type, tok_string))
    new_code = tokenize.untokenize(cleaned)

    path.write_text(new_code, encoding="utf-8")


def main():
    root = Path(__file__).resolve().parent
    for py_file in root.rglob("*.py"):
        if py_file.name in {Path(__file__).name, "clean_project.py"}:
            continue
        process_file(py_file)
    print("Minimización completa. Copias .bak creadas.")

if __name__ == "__main__":
    main() 