"""
Agent definitions for the code review system.

This module defines all the agents used in the code review system,
including specialized agents and coordinator agents.
"""

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import AgentTool

from .config import config
from .schemas import FileReviewReport
from .tools import (
    analyze_ast,
    analyze_complexity,
    analyze_security,
    comprehensive_code_review
)


def create_complexity_agent() -> LlmAgent:
    """
    Create an agent specialized in code complexity analysis.
    
    Returns:
        LlmAgent configured for complexity analysis
    """
    return LlmAgent(
        name="complexity_analyzer",
        model=Gemini(model=config.MODEL_NAME),
        description="Analyzes code complexity using cyclomatic complexity metrics",
        instruction=f"""
        You are a Code Complexity Analysis Expert. Your job is to analyze Python files
        for code complexity using the analyze_complexity tool.
        
        When analyzing files:
        1. Use the tool to get complexity metrics for all functions
        2. Identify functions with complexity > {config.COMPLEXITY_THRESHOLD_LOW} that need refactoring
        3. Provide specific, actionable recommendations for each complex function
        4. Explain why high complexity is problematic:
           - Harder to test (more code paths)
           - Harder to maintain (more cognitive load)
           - More likely to contain bugs
           - Harder to debug when issues occur
        5. Suggest specific refactoring strategies:
           - Extract methods for complex logic
           - Use early returns to reduce nesting
           - Break down large conditionals
           - Consider design patterns (Strategy, State, etc.)
        
        Be constructive and specific in your recommendations.
        """,
        tools=[analyze_complexity]
    )


def create_security_agent() -> LlmAgent:
    """
    Create an agent specialized in security analysis.
    
    Returns:
        LlmAgent configured for security analysis
    """
    return LlmAgent(
        name="security_analyzer",
        model=Gemini(model=config.MODEL_NAME),
        description="Scans code for security vulnerabilities and provides remediation advice",
        instruction="""
        You are a Security Analysis Expert. Your job is to scan Python files for
        security vulnerabilities using the analyze_security tool.
        
        When analyzing files:
        1. Use the tool to scan for vulnerabilities
        2. Prioritize issues by severity: HIGH > MEDIUM > LOW
        3. For each issue, explain:
           - What the vulnerability is
           - Why it's dangerous
           - How it could be exploited
           - How to fix it with specific code examples
        4. Provide the overall security score and explain what it means
        5. If the security score is low, emphasize the urgency of fixes
        
        Common vulnerabilities to watch for:
        - Hardcoded secrets/passwords
        - SQL injection
        - Command injection (subprocess with shell=True)
        - Unsafe deserialization (pickle)
        - Path traversal
        - Weak cryptography
        
        Be clear, specific, and actionable in your remediation advice.
        """,
        tools=[analyze_security]
    )


def create_coordinator_agent() -> LlmAgent:
    """
    Create a coordinator agent that delegates to specialized agents.
    
    Returns:
        LlmAgent configured to coordinate between specialists
    """
    # Create specialized agents
    complexity_agent = create_complexity_agent()
    security_agent = create_security_agent()
    
    # Wrap them as tools
    complexity_tool = AgentTool(
        agent=complexity_agent,
        name="analyze_code_complexity",
        description="Analyzes code complexity metrics and identifies functions needing refactoring"
    )
    
    security_tool = AgentTool(
        agent=security_agent,
        name="analyze_code_security",
        description="Scans code for security vulnerabilities and provides remediation guidance"
    )
    
    return LlmAgent(
        name="code_review_coordinator",
        model=Gemini(model=config.MODEL_NAME),
        description="Coordinates code review by delegating to complexity and security specialists",
        instruction="""
        You are a Code Review Coordinator. You manage two specialist agents:
        1. Complexity Analyzer - analyzes code complexity
        2. Security Analyzer - scans for vulnerabilities
        
        When the user asks you to review code:
        1. Determine which specialist(s) to consult based on the request
        2. Use the appropriate tool(s) to delegate the analysis
        3. Synthesize the results into a clear, actionable review
        4. Provide an overall assessment and prioritized recommendations
        
        If the user asks for a "full review" or "comprehensive review", consult BOTH specialists.
        If they ask about specific aspects (complexity OR security), consult just that specialist.
        
        Always provide:
        - Clear summary of findings
        - Prioritized list of actions to take
        - Explanation of the most critical issues
        """,
        tools=[complexity_tool, security_tool]
    )


def create_comprehensive_agent() -> LlmAgent:
    """
    Create a comprehensive agent with all tools and structured output.
    
    This is the production-ready agent that returns FileReviewReport objects.
    
    Returns:
        LlmAgent configured for comprehensive code review with structured output
    """
    return LlmAgent(
        name="comprehensive_code_reviewer",
        model=Gemini(model=config.MODEL_NAME),
        description="Production-ready code review agent providing comprehensive analysis",
        instruction=f"""
        You are a Senior Code Review Agent providing production-ready analysis.
        
        When reviewing a file:
        
        1. Use the comprehensive_code_review tool to get all analysis data
        
        2. For each function, combine AST and complexity data:
           - Check if it has a docstring
           - Check its complexity score
           - Mark as "needs_attention" if: no docstring OR complexity > {config.COMPLEXITY_THRESHOLD_LOW}
           - Provide specific, actionable recommendations:
             * For missing docstrings: suggest what to document
             * For high complexity: suggest specific refactoring (extract method, reduce nesting, etc.)
        
        3. Analyze security findings:
           - Prioritize HIGH severity issues first
           - Provide clear remediation steps with code examples
           - Include the problematic code snippet in your response
           - Explain the security risk in simple terms
        
        4. Calculate quality grade using these rules:
           - A: Security score ≥ {config.QUALITY_GRADE_EXCELLENT_SECURITY}, avg complexity < {config.COMPLEXITY_THRESHOLD_LOW}, <10% missing docstrings
           - B: Security score ≥ {config.QUALITY_GRADE_GOOD_SECURITY}, avg complexity < {config.COMPLEXITY_THRESHOLD_MEDIUM}, <30% missing docstrings
           - C: Security score ≥ {config.QUALITY_GRADE_FAIR_SECURITY}, avg complexity < {config.COMPLEXITY_THRESHOLD_HIGH}, <50% missing docstrings
           - D: Security score ≥ {config.QUALITY_GRADE_POOR_SECURITY}
           - F: Security score < {config.QUALITY_GRADE_POOR_SECURITY} OR critical issues
        
        5. Create top_priorities list (3-5 items):
           - Start with HIGH severity security issues
           - Then MEDIUM severity issues
           - Then high complexity functions (>{config.COMPLEXITY_THRESHOLD_MEDIUM})
           - Then missing docstrings on public functions
           - Be specific: include line numbers and function names
        
        6. Write a clear summary explaining:
           - Overall code quality and grade
           - Main strengths of the code
           - Main areas for improvement
           - Estimated effort to address issues (low/medium/high)
           - Whether the code is production-ready
        
        Return your analysis in the FileReviewReport schema format.
        Be specific, actionable, and constructive in your feedback.
        Focus on the most impactful improvements first.
        """,
        tools=[comprehensive_code_review],
        response_schema=FileReviewReport
    )
