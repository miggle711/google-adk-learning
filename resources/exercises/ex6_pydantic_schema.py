"""
Exercise 6: Pydantic Output Schema
==================================

Goal: Learn to use Pydantic models to get structured, validated output from agents.

This exercise teaches you how to:
1. Define Pydantic models for structured data
2. Configure agents to return data in a specific schema
3. Validate and use the structured output

KEY CONCEPTS:

1. PYDANTIC MODELS = Python classes that define data structure:
   - from pydantic import BaseModel, Field
   - Type hints ensure data validation
   - Field() adds descriptions and constraints
   - Nested models for complex structures

2. STRUCTURED OUTPUT = Agent returns data matching your schema:
   - Instead of free-form text, get validated Python objects
   - Perfect for: reports, analysis results, structured data
   - Use response_schema parameter in LlmAgent

3. WHY USE SCHEMAS:
   - Type safety: Know exactly what you'll get back
   - Validation: Pydantic validates the data automatically
   - Integration: Easy to use in other code, save to DB, etc.
   - Documentation: Schema serves as API documentation

YOUR TASK:
1. Complete the Pydantic models for code review results
2. Complete the `create_schema_based_agent` function
3. Run the agent and see structured output

Run this file to test: uv run exercises/ex6_pydantic_schema.py
"""

import os
import asyncio
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
# STEP 1: Define Pydantic Models for Structured Output
# =============================================================================

class FunctionComplexity(BaseModel):
    """Represents complexity analysis for a single function."""
    # TODO: Add fields for function complexity
    #
    # Add these fields:
    # - name: str - function name
    # - complexity: int - cyclomatic complexity score
    # - rank: str - letter grade (A-F)
    # - line_number: int - where function starts
    # - needs_refactoring: bool - True if complexity > 5
    # - recommendation: str - specific advice for this function
    
    name: str = Field(description="Name of the function")
    complexity: int = Field(description="Cyclomatic complexity score")
    rank: str = Field(description="Complexity grade (A-F)")
    line_number: int = Field(description="Line number where function starts")
    needs_refactoring: bool = Field(description="Whether this function needs refactoring")
    recommendation: str = Field(description="Specific refactoring recommendation")


class SecurityIssue(BaseModel):
    """Represents a single security vulnerability."""
    # TODO: Add fields for security issues
    #
    # Add these fields:
    # - issue_id: str - bandit test ID (e.g., "B105")
    # - severity: str - HIGH, MEDIUM, or LOW
    # - description: str - what the issue is
    # - line_number: int - where the issue is
    # - fix: str - how to fix it
    
    issue_id: str = Field(description="Bandit test ID")
    severity: str = Field(description="Issue severity: HIGH, MEDIUM, or LOW")
    description: str = Field(description="Description of the security issue")
    line_number: int = Field(description="Line number where issue occurs")
    fix: str = Field(description="Recommended fix for this issue")


class CodeReviewReport(BaseModel):
    """Complete code review report with structured data."""
    # TODO: Add fields for the complete report
    #
    # Add these fields:
    # - file_path: str - the file that was reviewed
    # - overall_quality: str - "Excellent", "Good", "Fair", or "Poor"
    # - complexity_functions: List[FunctionComplexity] - list of function analyses
    # - security_issues: List[SecurityIssue] - list of vulnerabilities
    # - summary: str - brief overall summary
    # - priority_actions: List[str] - top 3 things to fix first
    
    file_path: str = Field(description="Path to the reviewed file")
    overall_quality: str = Field(description="Overall code quality rating")
    complexity_functions: List[FunctionComplexity] = Field(
        description="Complexity analysis for each function"
    )
    security_issues: List[SecurityIssue] = Field(
        description="Security vulnerabilities found"
    )
    summary: str = Field(description="Overall summary of the code review")
    priority_actions: List[str] = Field(
        description="Top 3 priority actions to take"
    )


# =============================================================================
# TOOLS (Same as before)
# =============================================================================

def analyze_file(file_path: str) -> str:
    """
    Analyze a Python file for both complexity and security.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        JSON string with combined analysis
    """
    try:
        # Run complexity analysis
        complexity_result = subprocess.run(
            ["python", "-m", "radon", "cc", file_path, "-j"],
            capture_output=True,
            text=True,
            timeout=30
        )
        complexity_data = json.loads(complexity_result.stdout)
        
        # Run security analysis
        security_result = subprocess.run(
            ["python", "-m", "bandit", "-f", "json", file_path],
            capture_output=True,
            text=True,
            timeout=60
        )
        security_data = json.loads(security_result.stdout)
        
        return json.dumps({
            "file_path": file_path,
            "complexity": complexity_data.get(file_path, []),
            "security": security_data.get("results", [])
        })
    except Exception as e:
        return json.dumps({"error": f"Analysis failed: {str(e)}"})


# =============================================================================
# STEP 2: Create Agent with Response Schema
# =============================================================================

def create_schema_based_agent() -> LlmAgent:
    """
    Create an agent that returns structured output matching CodeReviewReport.
    
    Returns:
        An LlmAgent configured with response_schema
    """
    # TODO: Implement this function
    #
    # Create an LlmAgent with:
    # - name: "structured_code_reviewer"
    # - model: Gemini(model="gemini-2.5-flash-lite")
    # - description: Brief description
    # - instruction: Tell it to analyze code and return structured reports
    # - tools: [analyze_file]
    # - response_schema: CodeReviewReport  <-- THIS IS THE KEY PART!
    #
    # The response_schema parameter tells the agent to return data
    # matching the Pydantic model structure.
    
    return LlmAgent(
        name="structured_code_reviewer",
        model=Gemini(model="gemini-2.5-flash-lite"),
        description="Performs code review and returns structured, validated reports",
        instruction="""
        You are a Code Review Agent that provides structured analysis reports.
        
        When asked to review a file:
        1. Use the analyze_file tool to get complexity and security data
        2. Analyze each function's complexity:
           - Mark functions with complexity > 5 as needing refactoring
           - Provide specific recommendations for complex functions
        3. Analyze security issues:
           - Prioritize by severity (HIGH > MEDIUM > LOW)
           - Provide specific fixes for each issue
        4. Determine overall quality:
           - "Excellent": No security issues, all complexity < 5
           - "Good": Minor issues only (LOW severity, complexity 5-10)
           - "Fair": Some MEDIUM issues or complexity 11-20
           - "Poor": HIGH severity issues or complexity > 20
        5. Create priority_actions list with top 3 most important fixes
        
        Return your analysis in the structured format defined by the schema.
        """,
        tools=[analyze_file],
        response_schema=CodeReviewReport
    )


# =============================================================================
# STEP 3: Run and Display Structured Output
# =============================================================================

async def demo():
    """Demonstrate structured output from the agent."""
    load_dotenv()
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY not set!")
        return
    
    print("=" * 60)
    print("Exercise 6: Pydantic Output Schema")
    print("=" * 60)
    
    # Create the agent
    agent = create_schema_based_agent()
    
    if agent is None:
        print("\nERROR: create_schema_based_agent returned None")
        return
    
    print(f"\nAgent created: {agent.name}")
    print("This agent returns structured CodeReviewReport objects\n")
    
    # Create session
    session_service = InMemorySessionService()
    app_name = "exercise_6"
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
    
    # Test file
    test_file = "exercises/sample_vulnerable.py"
    print(f"Reviewing: {test_file}")
    print("-" * 60)
    
    message = types.Content(
        parts=[types.Part(text=f"Please review {test_file}")]
    )
    
    print("\n[Agent analyzing...]")
    
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=message
    ):
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if part.text:
                    # The response should be structured JSON matching our schema
                    try:
                        # Parse the structured output
                        report = CodeReviewReport.model_validate_json(part.text)
                        
                        print("\n" + "=" * 60)
                        print("STRUCTURED CODE REVIEW REPORT")
                        print("=" * 60)
                        
                        print(f"\nFile: {report.file_path}")
                        print(f"Overall Quality: {report.overall_quality}")
                        
                        print(f"\n📊 COMPLEXITY ANALYSIS ({len(report.complexity_functions)} functions)")
                        print("-" * 40)
                        for func in report.complexity_functions:
                            flag = " ⚠️ REFACTOR" if func.needs_refactoring else " ✅"
                            print(f"\n  {func.name}() - Line {func.line_number}")
                            print(f"    Complexity: {func.complexity} ({func.rank}){flag}")
                            if func.needs_refactoring:
                                print(f"    💡 {func.recommendation}")
                        
                        print(f"\n🔒 SECURITY ANALYSIS ({len(report.security_issues)} issues)")
                        print("-" * 40)
                        if report.security_issues:
                            for issue in report.security_issues:
                                marker = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(issue.severity, "⚪")
                                print(f"\n  {marker} [{issue.issue_id}] {issue.severity} - Line {issue.line_number}")
                                print(f"    Issue: {issue.description}")
                                print(f"    Fix: {issue.fix}")
                        else:
                            print("  ✅ No security issues found!")
                        
                        print(f"\n📝 SUMMARY")
                        print("-" * 40)
                        print(f"  {report.summary}")
                        
                        print(f"\n🎯 PRIORITY ACTIONS")
                        print("-" * 40)
                        for i, action in enumerate(report.priority_actions, 1):
                            print(f"  {i}. {action}")
                        
                        print("\n" + "=" * 60)
                        print("✨ This was a STRUCTURED response!")
                        print("The agent returned a validated Pydantic object,")
                        print("not just free-form text. You can now:")
                        print("  - Save to database")
                        print("  - Generate reports")
                        print("  - Integrate with other systems")
                        print("=" * 60)
                        
                    except Exception as e:
                        print(f"\nRaw response: {part.text}")
                        print(f"\nError parsing structured output: {e}")


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    asyncio.run(demo())
