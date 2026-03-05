"""
Exercise 7: Combined Review Tool - Putting It All Together
==========================================================

Goal: Build a production-ready code review agent combining all concepts.

This exercise combines everything you've learned:
- Exercise 1-3: AST, Radon, Bandit tools
- Exercise 4: Basic agent with tools
- Exercise 5: Multi-agent coordination
- Exercise 6: Pydantic structured output

You'll create a complete code review system that:
1. Analyzes multiple files
2. Combines multiple analysis tools
3. Returns structured reports
4. Provides actionable recommendations

KEY CONCEPTS:

1. COMBINED TOOL = One tool that orchestrates multiple analyses:
   - Runs AST, complexity, and security scans
   - Combines results into comprehensive report
   - More efficient than calling tools separately

2. BATCH PROCESSING = Analyze multiple files:
   - Accept directory paths
   - Process all Python files
   - Aggregate results

3. PRODUCTION PATTERNS:
   - Error handling for each analysis step
   - Timeouts to prevent hanging
   - Clear, actionable output
   - Prioritized recommendations

YOUR TASK:
1. Complete the `comprehensive_code_review` tool
2. Complete the `create_production_review_agent` function
3. Test on real code

Run this file to test: uv run exercises/ex7_combined_review.py
"""

import os
import asyncio
import ast
import json
import subprocess
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class FunctionInfo(BaseModel):
    """Information about a single function."""
    name: str
    line_number: int
    has_docstring: bool
    complexity: int
    complexity_rank: str
    parameters: List[str]
    needs_attention: bool = Field(
        description="True if missing docstring OR complexity > 5"
    )
    recommendation: str


class SecurityFinding(BaseModel):
    """A security vulnerability finding."""
    issue_id: str
    severity: str
    confidence: str
    description: str
    line_number: int
    code_snippet: str
    remediation: str


class FileReviewReport(BaseModel):
    """Complete review report for a single file."""
    file_path: str
    total_functions: int
    functions_needing_attention: int
    average_complexity: float
    security_score: int
    quality_grade: str = Field(
        description="A (excellent) to F (poor)"
    )
    functions: List[FunctionInfo]
    security_findings: List[SecurityFinding]
    summary: str
    top_priorities: List[str] = Field(
        description="Top 3-5 most important actions"
    )


# =============================================================================
# STEP 1: Create Combined Analysis Tool
# =============================================================================

def comprehensive_code_review(file_path: str) -> str:
    """
    Perform comprehensive code review combining AST, complexity, and security analysis.
    
    Args:
        file_path: Path to the Python file to review
        
    Returns:
        JSON string with complete analysis data
    """
    # TODO: Implement this comprehensive tool
    #
    # This tool should:
    # 1. Run AST analysis (from ex1)
    # 2. Run complexity analysis (from ex2)
    # 3. Run security analysis (from ex3)
    # 4. Combine all results into one JSON structure
    #
    # Return structure:
    # {
    #     "file_path": str,
    #     "ast_analysis": {...},      # Function info from AST
    #     "complexity_analysis": {...}, # Radon results
    #     "security_analysis": {...}   # Bandit results
    # }
    
    try:
        result = {
            "file_path": file_path,
            "ast_analysis": {},
            "complexity_analysis": {},
            "security_analysis": {}
        }
        
        # 1. AST Analysis
        try:
            source = Path(file_path).read_text()
            tree = ast.parse(source)
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        "name": node.name,
                        "line": node.lineno,
                        "has_docstring": ast.get_docstring(node) is not None,
                        "docstring": ast.get_docstring(node),
                        "parameters": [arg.arg for arg in node.args.args]
                    })
            
            result["ast_analysis"] = {
                "total_functions": len(functions),
                "with_docstrings": sum(1 for f in functions if f["has_docstring"]),
                "without_docstrings": sum(1 for f in functions if not f["has_docstring"]),
                "functions": functions
            }
        except Exception as e:
            result["ast_analysis"] = {"error": str(e)}
        
        # 2. Complexity Analysis
        try:
            complexity_result = subprocess.run(
                ["python", "-m", "radon", "cc", file_path, "-j"],
                capture_output=True,
                text=True,
                timeout=30
            )
            complexity_data = json.loads(complexity_result.stdout)
            functions_complexity = complexity_data.get(file_path, [])
            
            avg_complexity = (
                sum(f["complexity"] for f in functions_complexity) / len(functions_complexity)
                if functions_complexity else 0
            )
            
            result["complexity_analysis"] = {
                "functions": functions_complexity,
                "average_complexity": round(avg_complexity, 2),
                "high_complexity_count": sum(1 for f in functions_complexity if f["complexity"] > 5)
            }
        except Exception as e:
            result["complexity_analysis"] = {"error": str(e)}
        
        # 3. Security Analysis
        try:
            security_result = subprocess.run(
                ["python", "-m", "bandit", "-f", "json", file_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            security_data = json.loads(security_result.stdout)
            issues = security_data.get("results", [])
            
            severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
            for issue in issues:
                sev = issue.get("issue_severity", "LOW")
                severity_counts[sev] = severity_counts.get(sev, 0) + 1
            
            security_score = max(
                0,
                100 - severity_counts["HIGH"] * 25 - 
                severity_counts["MEDIUM"] * 10 - 
                severity_counts["LOW"] * 5
            )
            
            result["security_analysis"] = {
                "total_issues": len(issues),
                "severity_counts": severity_counts,
                "security_score": security_score,
                "issues": issues
            }
        except Exception as e:
            result["security_analysis"] = {"error": str(e)}
        
        return json.dumps(result)
        
    except Exception as e:
        return json.dumps({"error": f"Comprehensive review failed: {str(e)}"})


# =============================================================================
# STEP 2: Create Production-Ready Agent
# =============================================================================

def create_production_review_agent() -> LlmAgent:
    """
    Create a production-ready code review agent with structured output.
    
    Returns:
        An LlmAgent configured for comprehensive code review
    """
    # TODO: Implement this function
    #
    # Create an LlmAgent with:
    # - name: "production_code_reviewer"
    # - model: Gemini(model="gemini-2.5-flash-lite")
    # - description: Production-ready code review agent
    # - instruction: Detailed instructions for comprehensive review
    # - tools: [comprehensive_code_review]
    # - response_schema: FileReviewReport
    
    return LlmAgent(
        name="production_code_reviewer",
        model=Gemini(model="gemini-2.5-flash-lite"),
        description="Production-ready code review agent providing comprehensive analysis",
        instruction="""
        You are a Senior Code Review Agent providing production-ready analysis.
        
        When reviewing a file:
        
        1. Use the comprehensive_code_review tool to get all analysis data
        
        2. For each function, combine AST and complexity data:
           - Check if it has a docstring
           - Check its complexity score
           - Mark as "needs_attention" if: no docstring OR complexity > 5
           - Provide specific, actionable recommendations
        
        3. Analyze security findings:
           - Prioritize HIGH severity issues
           - Provide clear remediation steps for each issue
           - Include code snippets showing the problem
        
        4. Calculate quality grade:
           - A: No security issues, all functions documented, avg complexity < 5
           - B: Minor issues (LOW severity, some missing docs, complexity 5-10)
           - C: Moderate issues (MEDIUM severity, many missing docs, complexity 11-15)
           - D: Serious issues (HIGH severity OR complexity 16-20)
           - F: Critical issues (multiple HIGH severity OR complexity > 20)
        
        5. Create top_priorities list:
           - Start with HIGH severity security issues
           - Then MEDIUM severity issues
           - Then high complexity functions (>10)
           - Then missing docstrings
           - Limit to 3-5 most important items
        
        6. Write a clear summary explaining:
           - Overall code quality
           - Main strengths
           - Main areas for improvement
           - Estimated effort to address issues
        
        Return your analysis in the FileReviewReport schema format.
        Be specific, actionable, and constructive in your feedback.
        """,
        tools=[comprehensive_code_review],
        response_schema=FileReviewReport
    )


# =============================================================================
# STEP 3: Demo and Testing
# =============================================================================

async def demo():
    """Demonstrate the production code review agent."""
    load_dotenv()
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY not set!")
        return
    
    print("=" * 70)
    print("Exercise 7: Production Code Review Agent")
    print("=" * 70)
    
    agent = create_production_review_agent()
    
    if agent is None:
        print("\nERROR: create_production_review_agent returned None")
        return
    
    print(f"\nAgent created: {agent.name}")
    
    # Create session
    session_service = InMemorySessionService()
    app_name = "exercise_7"
    user_id = "user_1"
    session_id = "session_1"
    
    await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )
    
    runner = Runner(
        agent=agent,
        app_name=app_name,
        session_service=session_service
    )
    
    # Test files
    test_files = [
        "exercises/sample_vulnerable.py",
        "academic_research_assistant/tools.py"
    ]
    
    for test_file in test_files:
        if not Path(test_file).exists():
            print(f"\nSkipping {test_file} (not found)")
            continue
        
        print("\n" + "=" * 70)
        print(f"REVIEWING: {test_file}")
        print("=" * 70)
        
        message = types.Content(
            parts=[types.Part(text=f"Please perform a comprehensive code review of {test_file}")]
        )
        
        print("\n[Analyzing...]")
        
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message
        ):
            if event.is_final_response() and event.content:
                for part in event.content.parts:
                    if part.text:
                        try:
                            report = FileReviewReport.model_validate_json(part.text)
                            
                            # Display the report
                            print("\n" + "🎯 CODE REVIEW REPORT ".center(70, "="))
                            print(f"\n📁 File: {report.file_path}")
                            print(f"🏆 Quality Grade: {report.quality_grade}")
                            print(f"🔒 Security Score: {report.security_score}/100")
                            print(f"📊 Functions: {report.total_functions} total, {report.functions_needing_attention} need attention")
                            print(f"📈 Average Complexity: {report.average_complexity:.2f}")
                            
                            if report.security_findings:
                                print(f"\n🚨 SECURITY FINDINGS ({len(report.security_findings)})")
                                print("-" * 70)
                                for finding in report.security_findings:
                                    marker = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(finding.severity, "⚪")
                                    print(f"\n{marker} [{finding.issue_id}] {finding.severity} (Confidence: {finding.confidence})")
                                    print(f"   Line {finding.line_number}: {finding.description}")
                                    print(f"   Fix: {finding.remediation}")
                            
                            print(f"\n⚙️  FUNCTION ANALYSIS")
                            print("-" * 70)
                            for func in report.functions:
                                if func.needs_attention:
                                    print(f"\n⚠️  {func.name}() - Line {func.line_number}")
                                    print(f"   Complexity: {func.complexity} ({func.complexity_rank})")
                                    print(f"   Docstring: {'✅' if func.has_docstring else '❌ Missing'}")
                                    print(f"   💡 {func.recommendation}")
                            
                            print(f"\n📝 SUMMARY")
                            print("-" * 70)
                            print(f"{report.summary}")
                            
                            print(f"\n🎯 TOP PRIORITIES")
                            print("-" * 70)
                            for i, priority in enumerate(report.top_priorities, 1):
                                print(f"{i}. {priority}")
                            
                            print("\n" + "=" * 70)
                            
                        except Exception as e:
                            print(f"\nError parsing report: {e}")
                            print(f"Raw response: {part.text[:500]}...")


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    asyncio.run(demo())
