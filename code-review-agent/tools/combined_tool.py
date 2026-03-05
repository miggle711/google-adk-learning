"""
Combined tool that orchestrates all code analysis tools.
"""

import json
from .ast_tool import analyze_ast
from .complexity_tool import analyze_complexity
from .security_tool import analyze_security


def comprehensive_code_review(file_path: str) -> str:
    """
    Perform comprehensive code review combining AST, complexity, and security analysis.
    
    This tool orchestrates all three analysis tools and combines their results
    into a single comprehensive report.
    
    Args:
        file_path: Path to the Python file to review
        
    Returns:
        JSON string with complete analysis data from all tools
    """
    try:
        # Run all three analyses
        ast_result = analyze_ast(file_path)
        complexity_result = analyze_complexity(file_path)
        security_result = analyze_security(file_path)
        
        # Parse results
        ast_data = json.loads(ast_result)
        complexity_data = json.loads(complexity_result)
        security_data = json.loads(security_result)
        
        # Check for errors in any analysis
        errors = []
        if "error" in ast_data:
            errors.append(f"AST: {ast_data['error']}")
        if "error" in complexity_data:
            errors.append(f"Complexity: {complexity_data['error']}")
        if "error" in security_data:
            errors.append(f"Security: {security_data['error']}")
        
        # Combine all results
        combined = {
            "file_path": file_path,
            "ast_analysis": ast_data,
            "complexity_analysis": complexity_data,
            "security_analysis": security_data,
        }
        
        if errors:
            combined["errors"] = errors
        
        return json.dumps(combined)
        
    except Exception as e:
        return json.dumps({
            "error": f"Comprehensive review failed: {str(e)}",
            "file_path": file_path
        })
