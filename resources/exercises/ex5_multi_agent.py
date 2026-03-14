"""
Exercise 5: Multi-Agent System with AgentTool
==============================================

Goal: Learn to create a multi-agent system where one agent can delegate to another.

This exercise teaches advanced ADK patterns:
1. Creating specialized agents for different tasks
2. Using AgentTool to let one agent call another agent
3. Orchestrating multiple agents with a coordinator

KEY CONCEPTS:

1. SPECIALIZED AGENTS = Agents focused on specific tasks:
   - Each agent has its own tools and expertise
   - Better than one "do everything" agent
   - More maintainable and testable

2. AGENT TOOL = Wraps an agent so another agent can use it:
   - from google.adk.tools import AgentTool
   - AgentTool(agent=my_agent, name="tool_name")
   - The coordinator agent can now "call" the specialized agent

3. COORDINATOR PATTERN = One agent orchestrates others:
   - Receives user request
   - Decides which specialist to delegate to
   - Combines results if needed

YOUR TASK:
1. Complete the `create_complexity_analyzer_agent` function
2. Complete the `create_security_analyzer_agent` function
3. Complete the `create_coordinator_agent` function
4. Run the multi-agent system

Run this file to test: uv run exercises/ex5_multi_agent.py
"""

import os
import asyncio
import json
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import AgentTool
from google.genai import types
from dotenv import load_dotenv

# Import the tools from previous exercises
import subprocess


# =============================================================================
# TOOLS (Reusing from previous exercises)
# =============================================================================

def analyze_complexity(file_path: str) -> str:
    """
    Analyze code complexity using radon.
    
    Args:
        file_path: Path to the Python file to analyze
        
    Returns:
        JSON string with complexity analysis results
    """
    try:
        result = subprocess.run(
            ["python", "-m", "radon", "cc", file_path, "-j"],
            capture_output=True,
            text=True,
            timeout=30
        )
        data = json.loads(result.stdout)
        functions_info = data.get(file_path, [])
        
        if not functions_info:
            return json.dumps({"error": "No functions found or file not analyzed"})
        
        total = len(functions_info)
        avg_complexity = sum(f["complexity"] for f in functions_info) / total if total > 0 else 0
        high_complexity = sum(1 for f in functions_info if f["complexity"] > 5)
        
        return json.dumps({
            "file_path": file_path,
            "total_functions": total,
            "average_complexity": round(avg_complexity, 2),
            "high_complexity_count": high_complexity,
            "functions": [
                {
                    "name": f["name"],
                    "complexity": f["complexity"],
                    "rank": f["rank"],
                    "line": f["lineno"]
                }
                for f in functions_info
            ]
        })
    except Exception as e:
        return json.dumps({"error": f"Failed to analyze complexity: {str(e)}"})


def analyze_security(file_path: str) -> str:
    """
    Scan for security vulnerabilities using bandit.
    
    Args:
        file_path: Path to the Python file to scan
        
    Returns:
        JSON string with security scan results
    """
    try:
        result = subprocess.run(
            ["python", "-m", "bandit", "-f", "json", file_path],
            capture_output=True,
            text=True,
            timeout=60
        )
        data = json.loads(result.stdout)
        issues = data.get("results", [])
        
        severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for issue in issues:
            sev = issue.get("issue_severity", "LOW")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        security_score = max(0, 100 - severity_counts["HIGH"] * 25 - 
                           severity_counts["MEDIUM"] * 10 - severity_counts["LOW"] * 5)
        
        return json.dumps({
            "file_path": file_path,
            "total_issues": len(issues),
            "security_score": security_score,
            "severity_counts": severity_counts,
            "issues": [
                {
                    "id": i.get("test_id"),
                    "severity": i.get("issue_severity"),
                    "description": i.get("issue_text"),
                    "line": i.get("line_number")
                }
                for i in issues
            ]
        })
    except Exception as e:
        return json.dumps({"error": f"Failed to analyze security: {str(e)}"})


# =============================================================================
# STEP 1: Create Specialized Agents
# =============================================================================

def create_complexity_analyzer_agent() -> LlmAgent:
    """
    Create an agent specialized in analyzing code complexity.
    
    Returns:
        An LlmAgent configured with the analyze_complexity tool
    """
    # TODO: Implement this function
    # 
    # Create an LlmAgent with:
    # - name: "complexity_analyzer"
    # - model: Gemini(model="gemini-2.5-flash-lite")
    # - description: Brief description of what this agent does
    # - instruction: Tell the agent it's a complexity analysis expert
    # - tools: [analyze_complexity]
    
    return LlmAgent(
        name="complexity_analyzer",
        model=Gemini(model="gemini-2.5-flash-lite"),
        description="Analyzes code complexity using cyclomatic complexity metrics",
        instruction="""
        You are a Code Complexity Analysis Expert. Your job is to analyze Python files
        for code complexity using the analyze_complexity tool. 
        
        When analyzing files:
        1. Use the tool to get complexity metrics
        2. Identify functions with high complexity (>5)
        3. Provide specific recommendations for refactoring complex functions
        4. Explain why high complexity is problematic (harder to test, maintain, debug)
        """,
        tools=[analyze_complexity]
    )


def create_security_analyzer_agent() -> LlmAgent:
    """
    Create an agent specialized in security analysis.
    
    Returns:
        An LlmAgent configured with the analyze_security tool
    """
    # TODO: Implement this function
    #
    # Create an LlmAgent with:
    # - name: "security_analyzer"
    # - model: Gemini(model="gemini-2.5-flash-lite")
    # - description: Brief description of what this agent does
    # - instruction: Tell the agent it's a security analysis expert
    # - tools: [analyze_security]
    
    return LlmAgent(
        name="security_analyzer",
        model=Gemini(model="gemini-2.5-flash-lite"),
        description="Scans code for security vulnerabilities and provides remediation advice",
        instruction="""
        You are a Security Analysis Expert. Your job is to scan Python files for
        security vulnerabilities using the analyze_security tool.
        
        When analyzing files:
        1. Use the tool to scan for vulnerabilities
        2. Prioritize issues by severity (HIGH > MEDIUM > LOW)
        3. Explain each vulnerability in simple terms
        4. Provide specific code fixes for each issue
        5. Calculate and report the overall security score
        """,
        tools=[analyze_security]
    )


# =============================================================================
# STEP 2: Create Coordinator Agent with AgentTool
# =============================================================================

def create_coordinator_agent(
    complexity_agent: LlmAgent,
    security_agent: LlmAgent
) -> LlmAgent:
    """
    Create a coordinator agent that can delegate to specialized agents.
    
    Args:
        complexity_agent: The complexity analysis specialist
        security_agent: The security analysis specialist
        
    Returns:
        An LlmAgent configured with AgentTools for both specialists
    """
    # TODO: Implement this function
    #
    # 1. Create AgentTools for each specialist:
    #    complexity_tool = AgentTool(
    #        agent=complexity_agent,
    #        name="analyze_code_complexity",
    #        description="Analyzes code complexity and identifies complex functions"
    #    )
    #
    # 2. Create the coordinator LlmAgent with:
    #    - name: "code_review_coordinator"
    #    - model: Gemini(model="gemini-2.5-flash-lite")
    #    - instruction: Tell it to coordinate between specialists
    #    - tools: [complexity_tool, security_tool]
    
    complexity_tool = AgentTool(
        agent=complexity_agent,
        name="analyze_code_complexity",
        description="Analyzes code complexity metrics and identifies functions that need refactoring"
    )
    
    security_tool = AgentTool(
        agent=security_agent,
        name="analyze_code_security",
        description="Scans code for security vulnerabilities and provides remediation guidance"
    )
    
    return LlmAgent(
        name="code_review_coordinator",
        model=Gemini(model="gemini-2.5-flash-lite"),
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
        
        If the user asks for a "full review", consult BOTH specialists.
        If they ask about specific aspects (complexity OR security), consult just that specialist.
        """,
        tools=[complexity_tool, security_tool]
    )


# =============================================================================
# STEP 3: Run the Multi-Agent System
# =============================================================================

async def chat():
    """Main chat loop to interact with the multi-agent system."""
    load_dotenv()
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY not set!")
        print("Create a .env file with: GOOGLE_API_KEY=your-key-here")
        return
    
    print("=" * 60)
    print("Exercise 5: Multi-Agent System")
    print("=" * 60)
    
    # Create specialized agents
    print("\nCreating specialized agents...")
    complexity_agent = create_complexity_analyzer_agent()
    security_agent = create_security_analyzer_agent()
    
    # Create coordinator agent
    print("Creating coordinator agent...")
    coordinator = create_coordinator_agent(complexity_agent, security_agent)
    
    if coordinator is None:
        print("\nERROR: create_coordinator_agent returned None")
        return
    
    print(f"\nCoordinator created: {coordinator.name}")
    
    # Create session service and runner
    session_service = InMemorySessionService()
    app_name = "exercise_5"
    user_id = "user_1"
    session_id = "session_1"
    
    await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )
    
    runner = Runner(
        agent=coordinator,
        app_name=app_name,
        session_service=session_service
    )
    
    print("\nMulti-agent system is ready! Try asking:")
    print("  - Analyze the complexity of exercises/ex1_ast.py")
    print("  - Check exercises/sample_vulnerable.py for security issues")
    print("  - Do a full code review of exercises/ex2_radon.py")
    print("\nType 'exit' to quit.\n")
    print("-" * 60)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            message = types.Content(parts=[types.Part(text=user_input)])
            
            print("\n[Coordinator thinking...]")
            
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=message
            ):
                if event.is_final_response() and event.content:
                    print("-" * 40)
                    for part in event.content.parts:
                        if part.text:
                            print(f"\nCoordinator: {part.text}")
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    asyncio.run(chat())
