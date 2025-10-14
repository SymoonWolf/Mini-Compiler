# asmgen.py
# ------------------------------------------
# Converts TAC into simplified assembly code
# ------------------------------------------

def tac_to_asm(tac_lines):
    asm = []
    for line in tac_lines:
        if line.startswith("label"):
            asm.append(line.replace("label", "").strip() + ":")
        elif line.startswith("PRINT"):
            asm.append("OUT " + line.split("PRINT")[1].strip())
        elif line.startswith("IFZ"):
            parts = line.split()
            asm.append(f"CMPZ {parts[1]}")
            asm.append(f"JZ {parts[3]}")
        elif line.startswith("IF"):
            parts = line.split()
            asm.append(f"CMP {parts[1]}")
            asm.append(f"JNZ {parts[3]}")
        elif line.startswith("GOTO"):
            asm.append("JMP " + line.split()[1])
        elif line.startswith("RETURN"):
            asm.append("RET " + line.split()[1])
        elif ":" in line:
            asm.append(line)
        elif "=" in line:
            asm.append("MOV " + line)
    return asm


if __name__ == "__main__":
    import sys
    from lexical import tokenize
    from parser import Parser
    from codegen import TACGen
    from optimizer import optimize

    if len(sys.argv) < 2:
        print("Usage: python asmgen.py sample.src")
        sys.exit()

    src = open(sys.argv[1]).read()
    toks = list(tokenize(src))
    tree = Parser(toks).parse()
    g = TACGen()
    tac = g.gen(tree)
    opt = optimize(tac)
    asm = tac_to_asm(opt)

    print("===== ASSEMBLY CODE =====")
    for line in asm:
        print(line)
    print("=========================\n")
