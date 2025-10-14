# lexical.py
# ------------------------------------------
# Lexical analyzer for MiniCompiler project
# Groups tokens into categories for CSE430
# ------------------------------------------

import re
from dataclasses import dataclass
from collections import defaultdict
import sys

@dataclass
class Token:
    type: str
    value: any
    line: int
    col: int

# token regex table
_spec = [
    ("COMMENT", r"//.*"),
    ("NEWLINE", r"\n"),
    ("SKIP",    r"[ \t\r]+"),
    ("FUNC",    r"\bfunc\b"),
    ("IF",      r"\bif\b"),
    ("ELSE",    r"\belse\b"),
    ("WHILE",   r"\bwhile\b"),
    ("RETURN",  r"\breturn\b"),
    ("PRINT",   r"\bprint\b"),
    ("TRUE",    r"\btrue\b"),
    ("FALSE",   r"\bfalse\b"),
    ("NUMBER",  r"-?\d+(\.\d+)?"),
    ("CHAR",    r"'([^'\\]|\\.)'"),
    ("STRING",  r'"([^"\\]|\\.)*"'),
    ("ID",      r"[A-Za-z_][A-Za-z0-9_]*"),
    ("EQEQ",    r"=="), ("NE", r"!="),
    ("LE",      r"<="), ("GE", r">="),
    ("LT", r"<"), ("GT", r">"),
    ("PLUS", r"\+"), ("MINUS", r"-"),
    ("TIMES", r"\*"), ("DIVIDE", r"/"),
    ("ASSIGN", r"="),
    ("LPAREN", r"\("), ("RPAREN", r"\)"),
    ("LBRACE", r"\{"), ("RBRACE", r"\}"),
    ("SEMI", r";"), ("COMMA", r",")
]
master = re.compile("|".join("(?P<%s>%s)" % x for x in _spec))

def tokenize(src: str):
    line, start = 1, 0
    for mo in master.finditer(src):
        kind = mo.lastgroup
        val = mo.group(kind)
        col = mo.start() - start + 1
        if kind == "NEWLINE":
            line += 1; start = mo.end(); continue
        if kind in ("SKIP", "COMMENT"): continue
        if kind == "NUMBER":
            if "." in val:
                yield Token("FLOAT", float(val), line, col)
            else:
                yield Token("INT", int(val), line, col)
        elif kind == "STRING":
            yield Token("STRING", val[1:-1], line, col)
        elif kind == "CHAR":
            yield Token("CHAR", val[1:-1], line, col)
        elif kind in ("TRUE", "FALSE"):
            yield Token("BOOL", True if kind == "TRUE" else False, line, col)
        else:
            yield Token(kind, val, line, col)

# pretty print grouped output
def print_token_summary(tokens):
    groups = defaultdict(list)
    for t in tokens:
        if t.type in ("FUNC","IF","ELSE","WHILE","RETURN","PRINT"):
            groups["Keywords"].append(t.value)
        elif t.type in ("ID",):
            groups["Identifiers"].append(t.value)
        elif t.type in ("PLUS","MINUS","TIMES","DIVIDE","ASSIGN"):
            groups["Arithmetic Operators"].append(t.value)
        elif t.type in ("EQEQ","NE","LT","GT","LE","GE"):
            groups["Relational Operators"].append(t.value)
        elif t.type in ("INT","FLOAT","CHAR","STRING","BOOL"):
            groups["Constants"].append(str(t.value))
        elif t.type in ("LPAREN","RPAREN"):
            groups["Parentheses"].append(t.value)
        elif t.type in ("LBRACE","RBRACE","SEMI","COMMA"):
            groups["Punctuations"].append(t.value)
        else:
            groups["Others"].append(t.value)

    print("===== LEXICAL ANALYSIS =====")
    for name, items in groups.items():
        print(f"{name} ({len(items)}): {', '.join(items)}")
    print("=============================\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python lexical.py sample.src")
        sys.exit()
    with open(sys.argv[1],'r',encoding='utf-8') as f:
        src=f.read()
    toks=list(tokenize(src))
    print_token_summary(toks)
