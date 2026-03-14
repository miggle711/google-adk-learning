"""
Exercise 3: Bandit Security Scanning
====================================

Goal: Learn to use bandit via subprocess to detect security vulnerabilities.

Bandit is a static analysis tool that finds common security issues in Python:
- Hardcoded passwords/secrets
- SQL injection
- Shell injection (subprocess with shell=True)
- Unsafe deserialization (pickle)
- And many more...

BANDIT JSON OUTPUT STRUCTURE:
{
    "results": [
        {
            "test_id": "B105",           # Issue ID
            "test_name": "hardcoded_password_string",
            "issue_severity": "LOW",     # LOW, MEDIUM, HIGH
            "issue_confidence": "MEDIUM", # LOW, MEDIUM, HIGH
            "issue_text": "Possible hardcoded password",
            "line_number": 10,
            "code": "password = 'secret'",
            "more_info": "https://..."
        }
    ],
    "metrics": { ... }
}

YOUR TASK:
Complete the `scan_for_vulnerabilities` function below.

HINTS:
- Command: ["python", "-m", "bandit", "-f", "json", file_path]
- The key data is in result["results"]
- Each issue has: test_id, issue_severity, issue_text, line_number

Run this file to test: python exercises/ex3_bandit.py
"""

import subprocess
import json


def scan_for_vulnerabilities(file_path: str) -> dict:
    """
    Scan a Python file for security vulnerabilities using bandit.

    Args:
        file_path: Path to the Python file to scan

    Returns:
        A dictionary with:
        - "file_path": the scanned file
        - "total_issues": int - total vulnerabilities found
        - "severity_counts": dict with counts for HIGH, MEDIUM, LOW
        - "security_score": int 0-100 (100 = no issues, deduct points per issue)
        - "issues": list of dicts, each containing:
            - "id": test ID (e.g., "B105")
            - "name": test name
            - "severity": HIGH, MEDIUM, or LOW
            - "confidence": HIGH, MEDIUM, or LOW
            - "description": what the issue is
            - "line": line number
            - "code": the problematic code snippet
    """
    # TODO: Implement this function
    #
    # Step 1: Run bandit via subprocess
    # result = subprocess.run(
    #     ["python", "-m", "bandit", "-f", "json", file_path],
    #     capture_output=True,
    #     text=True,
    #     timeout=60
    # )
    #
    # Step 2: Parse the JSON output
    # Note: bandit may return non-zero exit code even on success (if issues found)
    # So check if stdout has valid JSON, not just returncode
    #
    # Step 3: Extract issues from results["results"]
    #
    # Step 4: Calculate security score:
    #   Start at 100, deduct: HIGH=-25, MEDIUM=-10, LOW=-5
    #   Minimum score is 0

    try:
        result = subprocess.run(
            ["python", "-m", "bandit", "-f", "json", file_path],
            capture_output=True,
            text=True,
            timeout=60
        )
        data = json.loads(result.stdout)
        issues = []
        severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for issue in data.get("results", []):
            sev = issue.get("issue_severity", "LOW")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
            issues.append({
                "id": issue.get("test_id", "?"),
                "name": issue.get("test_name", "?"),
                "severity": sev,
                "confidence": issue.get("issue_confidence", "?"),
                "description": issue.get("issue_text", "?"),
                "line": issue.get("line_number", "?"),
                "code": issue.get("code", "").strip()
            })
        total_issues = len(issues)
        security_score = max(0, 100 - severity_counts["HIGH"] * 25 - severity_counts["MEDIUM"] * 10 - severity_counts["LOW"] * 5)
        return {
            "file_path": file_path,
            "total_issues": total_issues,
            "severity_counts": severity_counts,
            "security_score": security_score,
            "issues": issues
        }
    except json.JSONDecodeError:
        print(f"ERROR: Failed to parse bandit output for {file_path}")
        print("Bandit output was:")
        print(result.stdout)
        return None
    except subprocess.TimeoutExpired:
        print(f"ERROR: Bandit scan timed out for {file_path}")
        return None
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while scanning {file_path}")
        print(str(e))
        return None


# =============================================================================
# TEST CODE - Run this file to test your implementation
# =============================================================================

if __name__ == "__main__":
    # Test on the intentionally vulnerable file
    test_file = "exercises/sample_vulnerable.py"

    print("=" * 60)
    print("Exercise 3: Bandit Security Scan")
    print("=" * 60)
    print(f"\nScanning: {test_file}\n")

    result = scan_for_vulnerabilities(test_file)

    if result is None:
        print("ERROR: scan_for_vulnerabilities returned None")
        print("Hint: Remove 'pass' and implement the function!")
    else:
        print(f"Total issues found: {result.get('total_issues', 'N/A')}")
        print(f"Security score: {result.get('security_score', 'N/A')}/100")

        counts = result.get("severity_counts", {})
        print(f"\nSeverity breakdown:")
        print(f"  HIGH:   {counts.get('HIGH', 0)}")
        print(f"  MEDIUM: {counts.get('MEDIUM', 0)}")
        print(f"  LOW:    {counts.get('LOW', 0)}")

        print("\n" + "-" * 40)
        print("Security Issues Found:")
        print("-" * 40)

        for issue in result.get("issues", []):
            sev = issue.get("severity", "?")
            marker = {"HIGH": "!!!", "MEDIUM": "!!", "LOW": "!"}.get(sev, "")
            print(f"\n  [{issue.get('id', '?')}] {sev} {marker}")
            print(f"    Line {issue.get('line', '?')}: {issue.get('description', '?')}")
            if issue.get("code"):
                code_preview = issue["code"].strip()[:60]
                print(f"    Code: {code_preview}")

    print("\n" + "=" * 60)
    print("Expected issues in sample_vulnerable.py:")
    print("- B105: Hardcoded password")
    print("- B301: Pickle usage")
    print("- B602: subprocess with shell=True (HIGH severity)")
    print("- B608: SQL injection")
    print("=" * 60)
