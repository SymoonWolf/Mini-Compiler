# codegen.py
# ------------------------------------------
# Generates 3-address code from AST
# ------------------------------------------

from parser import *
from itertools import count

class TACGen:
    def __init__(self):
        self.code=[]
        self.temp=count(1)
        self.label=count(1)

    def newt(self): return f"T{next(self.temp)}"
    def newl(self): return f"L{next(self.label)}"
    def emit(self,line): self.code.append(line)

    def gen(self,tree):
        for f in tree.funcs:
            self.emit(f"label {f.name}")
            for s in f.body.stmts: self.stmt(s)
        return self.code

    def stmt(self,s):
        if isinstance(s,VarAssign):
            t=self.expr(s.expr)
            self.emit(f"{s.name} = {t}")
        elif isinstance(s,PrintStmt):
            t=self.expr(s.expr)
            self.emit(f"PRINT {t}")
        elif isinstance(s,IfStmt):
            cond=self.expr(s.cond)
            L1=self.newl(); L2=self.newl()
            self.emit(f"IF {cond} GOTO {L1}")
            for st in s.thenb.stmts: self.stmt(st)
            self.emit(f"GOTO {L2}")
            self.emit(f"{L1}:")
            if s.elseb:
                for st in s.elseb.stmts: self.stmt(st)
            self.emit(f"{L2}:")
        elif isinstance(s,WhileStmt):
            L1=self.newl(); L2=self.newl()
            self.emit(f"{L1}:")
            cond=self.expr(s.cond)
            self.emit(f"IFZ {cond} GOTO {L2}")
            for st in s.body.stmts: self.stmt(st)
            self.emit(f"GOTO {L1}")
            self.emit(f"{L2}:")
        elif isinstance(s,ReturnStmt):
            t=self.expr(s.expr)
            self.emit(f"RETURN {t}")

    def expr(self,e):
        if isinstance(e,Number): t=self.newt(); self.emit(f"{t} = {e.val}"); return t
        if isinstance(e,String): t=self.newt(); self.emit(f'{t} = "{e.val}"'); return t
        if isinstance(e,Char): t=self.newt(); self.emit(f"{t} = '{e.val}'"); return t
        if isinstance(e,VarRef): return e.name
        if isinstance(e,BinOp):
            a=self.expr(e.left); b=self.expr(e.right)
            t=self.newt()
            opmap={"PLUS":"+","MINUS":"-","TIMES":"*","DIVIDE":"/","EQEQ":"==","NE":"!=",
                   "LT":"<","GT":">","LE":"<=","GE":">="}
            op=opmap.get(e.op,"?")
            self.emit(f"{t} = {a} {op} {b}")
            return t
        return "0"

if __name__ == "__main__":
    import sys
    from lexical import tokenize
    from parser import Parser, print_ast
    if len(sys.argv)<2:
        print("Usage: python codegen.py sample.src"); sys.exit()
    src=open(sys.argv[1]).read()
    toks=list(tokenize(src)); tree=Parser(toks).parse()
    g=TACGen(); tac=g.gen(tree)
    print("===== THREE ADDRESS CODE =====")
    for i,line in enumerate(tac,1): print(f"({i}) {line}")
    print("==============================\n")
