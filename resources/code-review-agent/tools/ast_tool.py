"""
AST analysis tool for extracting function information from Python code.
"""

import ast
import json
from pathlib import Path
from typing import Dict, Any


def analyze_ast(file_path: str) -> str:
    """
    Analyze a Python file using AST to extract function information.
    
    Args:
        file_path: Path to the Python file to analyze
        
    Returns:
        JSON string with function information including names, docstrings,
        parameters, and line numbers
    """
    try:
        # Read and parse the file
        source = Path(file_path).read_text()
        tree = ast.parse(source)
        
        functions = []
        
        # Walk the AST and find all function definitions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node)
                
                functions.append({
                    "name": node.name,
                    "line_number": node.lineno,
                    "has_docstring": docstring is not None,
                    "docstring": docstring,
                    "parameters": [arg.arg for arg in node.args.args]
                })
        
        # Calculate statistics
        total_functions = len(functions)
        with_docstrings = sum(1 for f in functions if f["has_docstring"])
        without_docstrings = total_functions - with_docstrings
        
        return json.dumps({
            "file_path": file_path,
            "total_functions": total_functions,
            "with_docstrings": with_docstrings,
            "without_docstrings": without_docstrings,
            "missing_docstrings_ratio": (
                without_docstrings / total_functions if total_functions > 0 else 0
            ),
            "functions": functions
        })
        
    except SyntaxError as e:
        return json.dumps({
            "error": f"Syntax error in file: {str(e)}",
            "file_path": file_path
        })
    except Exception as e:
        return json.dumps({
            "error": f"Failed to analyze AST: {str(e)}",
            "file_path": file_path
        })
