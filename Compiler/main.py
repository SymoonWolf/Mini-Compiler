# main.py
# ------------------------------------------
# Main driver: runs all compiler phases
# ------------------------------------------

import sys
from lexical import tokenize, print_token_summary
from parser import Parser, print_ast
from semantic import analyze
from codegen import TACGen
from optimizer import optimize
from asmgen import tac_to_asm

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py sample.src")
        sys.exit()

    src_file = sys.argv[1]
    with open(src_file, "r", encoding="utf-8") as f:
        src = f.read()

    # Phase 1: Lexical Analysis
    toks = list(tokenize(src))
    print_token_summary(toks)

    # Phase 2: Parsing
    parser = Parser(toks)
    tree = parser.parse()
    print("===== PARSER (SYNTAX TREE) =====")
    print_ast(tree)
    print("===============================\n")

    # Phase 3: Semantic Analysis
    symtab = analyze(tree)

    # Phase 4: TAC Generation
    gen = TACGen()
    tac = gen.gen(tree)
    print("===== THREE ADDRESS CODE =====")
    for i, line in enumerate(tac, 1):
        print(f"({i}) {line}")
    print("==============================\n")

    # Phase 5: Optimization
    opt = optimize(tac)
    print("===== OPTIMIZED TAC =====")
    for i, line in enumerate(opt, 1):
        print(f"({i}) {line}")
    print("=========================\n")

    # Phase 6: Assembly Generation
    asm = tac_to_asm(opt)
    print("===== ASSEMBLY CODE =====")
    for line in asm:
        print(line)
    print("=========================\n")

if __name__ == "__main__":
    main()
