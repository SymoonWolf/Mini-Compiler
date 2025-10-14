# parser.py
# ------------------------------------------
# Recursive-descent parser for MiniCompiler
# Produces indented syntax tree (P1 format)
# ------------------------------------------

from lexical import tokenize, Token
import sys

# AST node classes
class Node: pass
class Program(Node): 
    def __init__(self,funcs): self.funcs=funcs
class FuncDecl(Node):
    def __init__(self,name,params,body):
        self.name=name; self.params=params; self.body=body
class Block(Node):
    def __init__(self,stmts): self.stmts=stmts
class VarAssign(Node):
    def __init__(self,name,expr): self.name=name; self.expr=expr
class PrintStmt(Node):
    def __init__(self,expr): self.expr=expr
class IfStmt(Node):
    def __init__(self,cond,thenb,elseb):
        self.cond=cond; self.thenb=thenb; self.elseb=elseb
class WhileStmt(Node):
    def __init__(self,cond,body): self.cond=cond; self.body=body
class ReturnStmt(Node):
    def __init__(self,expr): self.expr=expr
class ExprStmt(Node):
    def __init__(self,expr): self.expr=expr
class BinOp(Node):
    def __init__(self,op,left,right):
        self.op=op; self.left=left; self.right=right
class Number(Node):  # also bool
    def __init__(self,val): self.val=val
class String(Node): 
    def __init__(self,val): self.val=val
class Char(Node): 
    def __init__(self,val): self.val=val
class VarRef(Node):
    def __init__(self,name): self.name=name
class FuncCall(Node):
    def __init__(self,name,args): self.name=name; self.args=args

class Parser:
    def __init__(self,tokens): self.toks=tokens; self.i=0
    def peek(self): return self.toks[self.i] if self.i<len(self.toks) else None
    def next(self): t=self.peek(); self.i+=1; return t
    def expect(self,typ):
        t=self.peek()
        if not t or t.type!=typ:
            raise SyntaxError(f"Expected {typ} near {t}")
        return self.next()

    def parse(self):
        funcs=[]
        while self.peek(): funcs.append(self.func())
        return Program(funcs)

    def func(self):
        self.expect("FUNC")
        name=self.expect("ID").value
        self.expect("LPAREN"); params=[]; 
        if self.peek() and self.peek().type=="ID":
            params.append(self.next().value)
            while self.peek() and self.peek().type=="COMMA":
                self.next(); params.append(self.expect("ID").value)
        self.expect("RPAREN")
        body=self.block()
        return FuncDecl(name,params,body)

    def block(self):
        self.expect("LBRACE"); stmts=[]
        while self.peek() and self.peek().type!="RBRACE":
            stmts.append(self.stmt())
        self.expect("RBRACE")
        return Block(stmts)

    def stmt(self):
        t=self.peek()
        if not t: return None
        if t.type=="ID":
            name=t.value
            nxt=self.toks[self.i+1] if self.i+1<len(self.toks) else None
            if nxt and nxt.type=="ASSIGN":
                self.next(); self.next()
                expr=self.expr(); self.expect("SEMI")
                return VarAssign(name,expr)
            expr=self.expr(); self.expect("SEMI"); return ExprStmt(expr)
        if t.type=="PRINT":
            self.next(); self.expect("LPAREN"); e=self.expr()
            self.expect("RPAREN"); self.expect("SEMI"); return PrintStmt(e)
        if t.type=="IF":
            self.next(); self.expect("LPAREN"); cond=self.expr(); self.expect("RPAREN")
            thenb=self.block()
            elseb=None
            if self.peek() and self.peek().type=="ELSE":
                self.next(); elseb=self.block()
            return IfStmt(cond,thenb,elseb)
        if t.type=="WHILE":
            self.next(); self.expect("LPAREN"); cond=self.expr(); self.expect("RPAREN")
            body=self.block(); return WhileStmt(cond,body)
        if t.type=="RETURN":
            self.next(); e=self.expr(); self.expect("SEMI"); return ReturnStmt(e)
        if t.type=="LBRACE": return self.block()
        expr=self.expr(); self.expect("SEMI"); return ExprStmt(expr)

    # expression parsing (precedence climbing)
    prec={"EQEQ":3,"NE":3,"LT":4,"GT":4,"LE":4,"GE":4,"PLUS":5,"MINUS":5,"TIMES":6,"DIVIDE":6}
    def expr(self,minp=0):
        left=self.atom()
        while True:
            op=self.peek()
            if not op or op.type not in self.prec: break
            p=self.prec[op.type]
            if p<minp: break
            self.next()
            right=self.expr(p+1)
            left=BinOp(op.type,left,right)
        return left

    def atom(self):
        t=self.next()
        if t.type in ("INT","FLOAT","BOOL"): return Number(t.value)
        if t.type=="STRING": return String(t.value)
        if t.type=="CHAR": return Char(t.value)
        if t.type=="ID":
            if self.peek() and self.peek().type=="LPAREN":
                self.next()
                args=[]
                if self.peek() and self.peek().type!="RPAREN":
                    args.append(self.expr())
                    while self.peek() and self.peek().type=="COMMA":
                        self.next(); args.append(self.expr())
                self.expect("RPAREN"); return FuncCall(t.value,args)
            return VarRef(t.value)
        if t.type=="LPAREN":
            e=self.expr(); self.expect("RPAREN"); return e
        raise SyntaxError(f"Unexpected {t.type}")

# pretty print AST
def print_ast(node, indent=0, prefix=""):
    sp=" "*(indent*2)
    if isinstance(node, Program):
        print(sp+"Program")
        for f in node.funcs: print_ast(f, indent+1, "└── ")
    elif isinstance(node, FuncDecl):
        print(sp+f"{prefix}Function: {node.name}")
        print_ast(node.body, indent+1)
    elif isinstance(node, Block):
        print(sp+f"{prefix}Block")
        for i,s in enumerate(node.stmts):
            mark="├── " if i<len(node.stmts)-1 else "└── "
            print_ast(s, indent+1, mark)
    elif isinstance(node, VarAssign):
        print(sp+f"{prefix}Assignment: {node.name} = ...")
    elif isinstance(node, PrintStmt):
        print(sp+f"{prefix}Print: ...")
    elif isinstance(node, IfStmt):
        print(sp+f"{prefix}If (...)")
        print_ast(node.thenb, indent+1, "├── ")
        if node.elseb:
            print_ast(node.elseb, indent+1, "└── ")
    elif isinstance(node, WhileStmt):
        print(sp+f"{prefix}While (...)")
        print_ast(node.body, indent+1, "└── ")
    elif isinstance(node, ReturnStmt):
        print(sp+f"{prefix}Return: ...")
    elif isinstance(node, ExprStmt):
        print(sp+f"{prefix}Expr: ...")
    else:
        print(sp+f"{prefix}{type(node).__name__}")

if __name__ == "__main__":
    if len(sys.argv)<2:
        print("Usage: python parser.py sample.src"); sys.exit()
    with open(sys.argv[1],'r',encoding='utf-8') as f: src=f.read()
    toks=list(tokenize(src))
    p=Parser(toks); tree=p.parse()
    print("===== PARSER (SYNTAX TREE) =====")
    print_ast(tree)
    print("===============================\n")
