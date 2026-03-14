"""
Complexity analysis tool using Radon.
"""

import json
import subprocess
from ..config import config


def analyze_complexity(file_path: str) -> str:
    """
    Analyze code complexity using Radon.
    
    Args:
        file_path: Path to the Python file to analyze
        
    Returns:
        JSON string with complexity metrics for each function
    """
    try:
        # Run radon to get cyclomatic complexity
        result = subprocess.run(
            ["python", "-m", "radon", "cc", file_path, "-j"],
            capture_output=True,
            text=True,
            timeout=config.RADON_TIMEOUT
        )
        
        # Parse the JSON output
        data = json.loads(result.stdout)
        functions_complexity = data.get(file_path, [])
        
        if not functions_complexity:
            return json.dumps({
                "file_path": file_path,
                "total_functions": 0,
                "average_complexity": 0,
                "functions": []
            })
        
        # Calculate statistics
        total_functions = len(functions_complexity)
        avg_complexity = sum(f["complexity"] for f in functions_complexity) / total_functions
        
        # Count functions by complexity level
        high_complexity = sum(
            1 for f in functions_complexity 
            if f["complexity"] > config.COMPLEXITY_THRESHOLD_MEDIUM
        )
        
        return json.dumps({
            "file_path": file_path,
            "total_functions": total_functions,
            "average_complexity": round(avg_complexity, 2),
            "high_complexity_count": high_complexity,
            "functions": [
                {
                    "name": f["name"],
                    "complexity": f["complexity"],
                    "rank": f["rank"],
                    "line_number": f["lineno"],
                    "end_line": f.get("endline"),
                    "needs_refactoring": f["complexity"] > config.COMPLEXITY_THRESHOLD_LOW
                }
                for f in functions_complexity
            ]
        })
        
    except subprocess.TimeoutExpired:
        return json.dumps({
            "error": f"Radon analysis timed out after {config.RADON_TIMEOUT}s",
            "file_path": file_path
        })
    except json.JSONDecodeError as e:
        return json.dumps({
            "error": f"Failed to parse Radon output: {str(e)}",
            "file_path": file_path
        })
    except Exception as e:
        return json.dumps({
            "error": f"Complexity analysis failed: {str(e)}",
            "file_path": file_path
        })
