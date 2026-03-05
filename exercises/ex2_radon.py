"""
Exercise 2: Radon Complexity Analysis
=====================================

Goal: Learn to use radon via subprocess to measure code complexity.

Radon measures "cyclomatic complexity" - how many independent paths exist
through your code. More if/else/loops = higher complexity = harder to test.

COMPLEXITY GRADES:
- A (1-5):   Simple, easy to test
- B (6-10):  Moderate complexity
- C (11-20): Complex, consider refactoring
- D (21-30): Very complex, should refactor
- F (31+):   Untestable, needs major refactoring

RADON JSON OUTPUT EXAMPLE:
{
    "file.py": [
        {
            "type": "function",
            "name": "my_function",
            "complexity": 14,
            "rank": "C",
            "lineno": 10,
            "endline": 50
        }
    ]
}

YOUR TASK:
Complete the `get_complex_functions` function below.

HINTS:
- Use subprocess.run() with capture_output=True, text=True
- Command: ["python", "-m", "radon", "cc", file_path, "-j"]
- Parse JSON with json.loads(result.stdout)
- Filter for complexity > threshold

Run this file to test: python exercises/ex2_radon.py
"""

import subprocess
import json


def get_complex_functions(file_path: str, threshold: int = 5) -> dict:
    """
    Analyze a Python file and return complexity metrics.

    Args:
        file_path: Path to the Python file to analyze
        threshold: Complexity threshold (default 5, functions above this are flagged)

    Returns:
        A dictionary with:
        - "file_path": the analyzed file
        - "total_functions": int - total functions analyzed
        - "average_complexity": float - average complexity score
        - "high_complexity_count": int - functions above threshold
        - "functions": list of dicts, each containing:
            - "name": function name
            - "complexity": int score
            - "rank": letter grade (A-F)
            - "line": line number
            - "needs_refactoring": bool (True if complexity > threshold)
    """
    # TODO: Implement this function
    #
    # Step 1: Run radon via subprocess
    # result = subprocess.run(
    #     ["python", "-m", "radon", "cc", file_path, "-j"],
    #     capture_output=True,
    #     text=True,
    #     timeout=30
    # )
    #
    # Step 2: Parse the JSON output
    # data = json.loads(result.stdout)
    #
    # Step 3: Extract function info from the data
    # The data is a dict where keys are file paths
    # Each value is a list of function complexity info
    #
    # Step 4: Calculate statistics and return result

    try:
        result = subprocess.run(
            ["python", "-m", "radon", "cc", file_path, "-j"],
            capture_output=True,
            text=True,
            timeout=30
        )
        data = json.loads(result.stdout)

        functions_info = data.get(file_path, [])
        total_functions = len(functions_info)
        average_complexity = sum(func["complexity"] for func in functions_info) / total_functions if total_functions > 0 else 0
        high_complexity_count = sum(1 for func in functions_info if func["complexity"] > threshold)

        functions = []
        for func in functions_info:
            functions.append({
                "name": func["name"],
                "complexity": func["complexity"],
                "rank": func["rank"],
                "line": func["lineno"],
                "needs_refactoring": func["complexity"] > threshold
            })

        return {
            "file_path": file_path,
            "total_functions": total_functions,
            "average_complexity": average_complexity,
            "high_complexity_count": high_complexity_count,
            "functions": functions
        }
    except subprocess.TimeoutExpired:
        print(f"ERROR: Radon analysis timed out for {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"ERROR: Failed to parse Radon output for {file_path}")
        print("Raw output:", result.stdout)
        return None
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")
        return None




# =============================================================================
# TEST CODE - Run this file to test your implementation
# =============================================================================

if __name__ == "__main__":
    test_file = "academic_research_assistant/tools.py"

    print("=" * 60)
    print("Exercise 2: Radon Complexity Analysis")
    print("=" * 60)
    print(f"\nAnalyzing: {test_file}\n")

    result = get_complex_functions(test_file, threshold=5)

    if result is None:
        print("ERROR: get_complex_functions returned None")
        print("Hint: Remove 'pass' and implement the function!")
    else:
        print(f"Total functions: {result.get('total_functions', 'N/A')}")
        print(f"Average complexity: {result.get('average_complexity', 'N/A')}")
        print(f"High complexity (>5): {result.get('high_complexity_count', 'N/A')}")

        print("\n" + "-" * 40)
        print("Function Complexity:")
        print("-" * 40)

        for func in result.get("functions", []):
            flag = " << REFACTOR" if func.get("needs_refactoring") else ""
            print(
                f"  {func.get('name', '?'):30} "
                f"Complexity: {func.get('complexity', '?'):2} "
                f"({func.get('rank', '?')}){flag}"
            )

    print("\n" + "=" * 60)
    print("Expected output for tools.py:")
    print("- search_arxiv: complexity ~5 (A)")
    print("- get_pdf_text_from_url: complexity ~6 (B)")
    print("- search_semantic_scholar: complexity ~14 (C) << needs refactoring")
    print("=" * 60)
