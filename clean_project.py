#!/usr/bin/env python3
"""Clean project: remove comments and emoji characters from all .py files.
Creates a .bak backup of every processed file.
Usage: python clean_project.py
"""
import tokenize
import os
import sys
import re
from pathlib import Path

# Regex to match most common emoji codepoints (faces, symbols, etc.)
EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002500-\U00002BEF\U0001F900-\U0001F9FF\u2600-\u26FF\u2700-\u27BF]",
    flags=re.UNICODE,
)

def strip_emojis(text: str) -> str:
    """Return text without emoji characters."""
    return EMOJI_RE.sub("", text)


def process_file(path: Path):
    backup = path.with_suffix(path.suffix + ".bak")
    backup.write_bytes(path.read_bytes())

    out_tokens = []
    with tokenize.open(path) as fh:
        tokens = list(tokenize.generate_tokens(fh.readline))

    for tok_type, tok_string, start, end, line in tokens:
        if tok_type == tokenize.COMMENT:
            continue  # skip comments entirely
        if tok_type == tokenize.STRING:
            tok_string = strip_emojis(tok_string)
        out_tokens.append((tok_type, tok_string))

    new_code = tokenize.untokenize(out_tokens)
    # Remove trailing whitespace on each line
    new_code = "\n".join(line.rstrip() for line in new_code.splitlines()) + "\n"

    path.write_text(new_code, encoding="utf-8")


def main():
    root = Path(__file__).resolve().parent
    count = 0
    for py_file in root.rglob("*.py"):
        if py_file.name == Path(__file__).name:
            continue  # skip self
        try:
            process_file(py_file)
            count += 1
        except Exception as e:
            print(f"[WARN] Could not process {py_file}: {e}")
    print(f"✔ Limpieza completada en {count} archivos .py")

if __name__ == "__main__":
    main() 