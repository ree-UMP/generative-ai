import os
import sys
import json
import ast
from pathlib import Path

def parse_python_file(path: Path):
    """
    Parse a Python file and extract:
    - functions
    - classes
    - simple call relationships (who calls what)
    """
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(text, filename=str(path))
    except Exception as e:
        print(f"[WARN] Failed to parse {path.name}: {e}")
        return {"functions": [], "classes": [], "calls": []}

    funcs = []
    classes = []
    calls = []
    parent_stack = []

    class Visitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            funcs.append(node.name)
            parent_stack.append(node.name)
            self.generic_visit(node)
            parent_stack.pop()

        def visit_AsyncFunctionDef(self, node):
            funcs.append(node.name)
            parent_stack.append(node.name)
            self.generic_visit(node)
            parent_stack.pop()

        def visit_ClassDef(self, node):
            classes.append(node.name)
            parent_stack.append(node.name)
            self.generic_visit(node)
            parent_stack.pop()

        def visit_Call(self, node):
            # find simple function/method call names
            if isinstance(node.func, ast.Name):
                callee = node.func.id
            elif isinstance(node.func, ast.Attribute):
                callee = node.func.attr
            else:
                callee = None

            caller = parent_stack[-1] if parent_stack else "<module>"
            if callee:
                calls.append((caller, callee))
            self.generic_visit(node)

    Visitor().visit(tree)
    return {"functions": sorted(set(funcs)),
            "classes": sorted(set(classes)),
            "calls": calls}

def build_ccg(repo_path: Path):
    """Build a Code Context Graph for the entire repository."""
    ccg = {"nodes": {}, "edges": []}

    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                fpath = Path(root) / file
                rel = fpath.relative_to(repo_path).as_posix()
                parsed = parse_python_file(fpath)
                ccg["nodes"][rel] = {
                    "functions": parsed["functions"],
                    "classes": parsed["classes"]
                }

                # Add call relationships
                for caller, callee in parsed["calls"]:
                    ccg["edges"].append({
                        "from": f"{rel}::{caller}",
                        "to": callee
                    })

    return ccg

def main():
    if len(sys.argv) < 2:
        print("Usage: python BE/code_analyzer.py <repo_relative_path>")
        sys.exit(1)

    repo_rel = sys.argv[1]
    repo_path = Path(repo_rel)
    if not repo_path.exists():
        print(f"Error: path {repo_path} does not exist.")
        sys.exit(2)

    print(f"[code_analyzer] Analyzing Python files in {repo_path} ...")
    ccg = build_ccg(repo_path)

    # Save JSON output
    outputs_dir = Path.cwd() / "outputs" / repo_path.name
    outputs_dir.mkdir(parents=True, exist_ok=True)
    out_path = outputs_dir / "ccg.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(ccg, f, indent=2)

    print(f"[code_analyzer] ✅ CCG written to {out_path.resolve()}")

if __name__ == "__main__":
    main()
 
