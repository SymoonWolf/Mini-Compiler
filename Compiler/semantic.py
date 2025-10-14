# semantic.py
# ------------------------------------------
# Builds symbol table and checks basic types
# ------------------------------------------

from parser import *
from collections import defaultdict

class SymbolTable:
    def __init__(self): self.scopes=[{}]
    def enter(self): self.scopes.append({})
    def leave(self): self.scopes.pop()
    def declare(self,name,typ): self.scopes[-1][name]=typ
    def lookup(self,name):
        for s in reversed(self.scopes):
            if name in s: return s[name]
        return None
    def dump(self):
        merged={}
        for s in self.scopes: merged.update(s)
        return merged

def infer(expr,tab):
    if isinstance(expr,Number): return "float" if isinstance(expr.val,float) else "int"
    if isinstance(expr,String): return "string"
    if isinstance(expr,Char): return "char"
    if isinstance(expr,VarRef): return tab.lookup(expr.name) or "int"
    if isinstance(expr,BinOp):
        lt=infer(expr.left,tab); rt=infer(expr.right,tab)
        if "float" in (lt,rt): return "float"
        if "string" in (lt,rt): return "string"
        return "int"
    return "int"

def analyze(tree):
    tab=SymbolTable()
    for f in tree.funcs:
        tab.declare(f.name,"func")
        tab.enter()
        for p in f.params: tab.declare(p,"int")
        analyze_block(f.body,tab)
        tab.leave()
    # print symbol table
    print("===== SYMBOL TABLE =====")
    for n,t in tab.dump().items():
        print(f"{n} : {t}")
    print("========================\n")
    return tab

def analyze_block(block,tab):
    for s in block.stmts:
        if isinstance(s,VarAssign):
            t=infer(s.expr,tab)
            if not tab.lookup(s.name): tab.declare(s.name,t)
        elif isinstance(s,IfStmt):
            analyze_block(s.thenb,tab)
            if s.elseb: analyze_block(s.elseb,tab)
        elif isinstance(s,WhileStmt):
            analyze_block(s.body,tab)
        elif isinstance(s,Block):
            tab.enter(); analyze_block(s,tab); tab.leave()
