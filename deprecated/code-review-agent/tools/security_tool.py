"""
Security analysis tool using Bandit.
"""

import json
import subprocess
from ..config import config


def analyze_security(file_path: str) -> str:
    """
    Scan for security vulnerabilities using Bandit.
    
    Args:
        file_path: Path to the Python file to scan
        
    Returns:
        JSON string with security issues and overall security score
    """
    try:
        # Run bandit security scanner
        result = subprocess.run(
            ["python", "-m", "bandit", "-f", "json", file_path],
            capture_output=True,
            text=True,
            timeout=config.BANDIT_TIMEOUT
        )
        
        # Parse the JSON output
        # Note: Bandit may return non-zero exit code even on success if issues found
        data = json.loads(result.stdout)
        issues = data.get("results", [])
        
        # Count issues by severity
        severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for issue in issues:
            sev = issue.get("issue_severity", "LOW")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        # Calculate security score (100 = perfect, 0 = terrible)
        security_score = max(
            0,
            100 - (
                severity_counts["HIGH"] * config.SECURITY_SCORE_DEDUCTION_HIGH +
                severity_counts["MEDIUM"] * config.SECURITY_SCORE_DEDUCTION_MEDIUM +
                severity_counts["LOW"] * config.SECURITY_SCORE_DEDUCTION_LOW
            )
        )
        
        return json.dumps({
            "file_path": file_path,
            "total_issues": len(issues),
            "severity_counts": severity_counts,
            "security_score": security_score,
            "issues": [
                {
                    "issue_id": issue.get("test_id"),
                    "test_name": issue.get("test_name"),
                    "severity": issue.get("issue_severity"),
                    "confidence": issue.get("issue_confidence"),
                    "description": issue.get("issue_text"),
                    "line_number": issue.get("line_number"),
                    "code_snippet": issue.get("code", "").strip(),
                    "more_info": issue.get("more_info")
                }
                for issue in issues
            ]
        })
        
    except subprocess.TimeoutExpired:
        return json.dumps({
            "error": f"Bandit scan timed out after {config.BANDIT_TIMEOUT}s",
            "file_path": file_path
        })
    except json.JSONDecodeError as e:
        return json.dumps({
            "error": f"Failed to parse Bandit output: {str(e)}",
            "file_path": file_path
        })
    except Exception as e:
        return json.dumps({
            "error": f"Security analysis failed: {str(e)}",
            "file_path": file_path
        })
