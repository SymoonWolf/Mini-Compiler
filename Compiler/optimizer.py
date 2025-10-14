# optimizer.py
# ------------------------------------------
# Simple optimizer for TAC (constant folding, dead code removal)
# ------------------------------------------

import re

def optimize(tac_lines):
    optimized = []
    consts = {}

    for line in tac_lines:
        m = re.match(r"(T\d+)\s*=\s*([0-9.]+)\s*([\+\-\*/])\s*([0-9.]+)", line)
        if m:
            # Constant folding: compute constants
            t, a, op, b = m.groups()
            val = eval(f"{a}{op}{b}")
            optimized.append(f"{t} = {val}")
            consts[t] = str(val)
            continue

        # Replace known constants
        for c, v in consts.items():
            if re.search(rf"\b{c}\b", line):
                line = re.sub(rf"\b{c}\b", v, line)

        optimized.append(line)

    # Dead code elimination (remove temp results never used)
    used = set()
    for l in optimized:
        for t in re.findall(r"\bT\d+\b", l):
            used.add(t)
    final = [l for l in optimized if not re.match(r"(T\d+)\s*=", l) or re.match(r"(T\d+)\s*=", l).group(1) in used]
    return final


if __name__ == "__main__":
    import sys
    from lexical import tokenize
    from parser import Parser
    from codegen import TACGen

    if len(sys.argv) < 2:
        print("Usage: python optimizer.py sample.src")
        sys.exit()

    src = open(sys.argv[1]).read()
    toks = list(tokenize(src))
    tree = Parser(toks).parse()
    g = TACGen()
    tac = g.gen(tree)

    print("===== OPTIMIZATION =====")
    print("Before:")
    for i, line in enumerate(tac, 1):
        print(f"({i}) {line}")

    opt = optimize(tac)
    print("\nAfter:")
    for i, line in enumerate(opt, 1):
        print(f"({i}) {line}")

    print("========================\n")
