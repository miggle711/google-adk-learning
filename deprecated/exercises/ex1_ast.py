"""
Exercise 1: Python AST Basics
=============================

Goal: Learn to use Python's ast module to extract function information from code.

The `ast` (Abstract Syntax Tree) module lets you parse Python code and analyze
its structure programmatically. This is how we'll extract function names,
docstrings, and parameters for the Code Review Agent.

YOUR TASK:
Complete the `analyze_file` function below.

HINTS:
- Use `ast.parse(source)` to parse source code into a tree
- Use `ast.walk(tree)` to iterate over all nodes
- Check for `ast.FunctionDef` nodes (regular functions)
- Use `ast.get_docstring(node)` to get a function's docstring
- Access `node.name` for function name, `node.lineno` for line number
- Access `node.args.args` for parameters (each has `.arg` for name)

Run this file to test: python exercises/ex1_ast.py
"""

import ast
from pathlib import Path


def analyze_file(file_path: str) -> dict:
    """
    Analyze a Python file and extract function information.

    Args:
        file_path: Path to the Python file to analyze

    Returns:
        A dictionary with:
        - "total_functions": int - total number of functions found
        - "with_docstrings": int - functions that have docstrings
        - "without_docstrings": int - functions missing docstrings
        - "functions": list of dicts, each containing:
            - "name": function name
            - "line": line number
            - "has_docstring": bool
            - "docstring": the docstring text or None
            - "parameters": list of parameter names
    """
    # TODO: Implement this function
    #
    # Step 1: Read the file contents
    # source = Path(file_path).read_text()
    #
    # Step 2: Parse into AST
    # tree = ast.parse(source)
    #
    # Step 3: Walk the tree and find FunctionDef nodes
    # for node in ast.walk(tree):
    #     if isinstance(node, ast.FunctionDef):
    #         # Extract info from node
    #
    # Step 4: Build and return the result dictionary

    ast_tree = ast.parse(Path(file_path).read_text())

    result = {
        "total_functions": 0,
        "with_docstrings": 0,
        "without_docstrings": 0,
        "functions": []
    }

    for node in ast.walk(ast_tree):
        if isinstance(node, ast.FunctionDef):
            result["total_functions"] += 1
            docstring = ast.get_docstring(node)
            has_docstring = docstring is not None
            if has_docstring:
                result["with_docstrings"] += 1
            else:
                result["without_docstrings"] += 1

            # Extract parameter names
            param_names = [arg.arg for arg in node.args.args]

            func_info = {
                "name": node.name,
                "line": node.lineno,
                "has_docstring": has_docstring,
                "docstring": docstring,
                "parameters": param_names
            }
            result["functions"].append(func_info)

    return result


# =============================================================================
# TEST CODE - Run this file to test your implementation
# =============================================================================

if __name__ == "__main__":
    # Test file path - analyze the academic research assistant tools
    test_file = "academic_research_assistant/tools.py"

    print("=" * 60)
    print("Exercise 1: AST Analysis")
    print("=" * 60)
    print(f"\nAnalyzing: {test_file}\n")

    result = analyze_file(test_file)

    if result is None:
        print("ERROR: analyze_file returned None")
        print("Hint: Remove 'pass' and implement the function!")
    else:
        print(f"Total functions found: {result.get('total_functions', 'N/A')}")
        print(f"With docstrings: {result.get('with_docstrings', 'N/A')}")
        print(f"Without docstrings: {result.get('without_docstrings', 'N/A')}")

        print("\n" + "-" * 40)
        print("Function Details:")
        print("-" * 40)

        for func in result.get("functions", []):
            status = "YES" if func.get("has_docstring") else "NO"
            params = ", ".join(func.get("parameters", []))
            print(f"\n  {func.get('name', '?')}({params})")
            print(f"    Line: {func.get('line', '?')}")
            print(f"    Has docstring: {status}")
            if func.get("docstring"):
                # Show first 80 chars of docstring
                preview = func["docstring"][:80].replace("\n", " ")
                print(f"    Docstring: {preview}...")

    print("\n" + "=" * 60)
    print("Expected output for tools.py:")
    print("- Should find: search_arxiv, search_semantic_scholar, get_pdf_text_from_url")
    print("- All should have docstrings")
    print("=" * 60)
