"""
Main CLI entry point for the code review agent.

Usage:
    python -m code-review-agent.main review <file_path>
    python -m code-review-agent.main interactive
"""

import os
import asyncio
import json
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .agents import create_comprehensive_agent, create_coordinator_agent
from .config import config
from .schemas import FileReviewReport


async def review_file(file_path: str, output_format: str = "terminal") -> Optional[FileReviewReport]:
    """
    Review a single file and display results.
    
    Args:
        file_path: Path to the Python file to review
        output_format: Output format - "terminal", "json", or "markdown"
        
    Returns:
        FileReviewReport object if successful, None otherwise
    """
    load_dotenv()
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY not set!")
        print("Create a .env file with: GOOGLE_API_KEY=your-key-here")
        return None
    
    # Validate file exists
    if not Path(file_path).exists():
        print(f"ERROR: File not found: {file_path}")
        return None
    
    # Create agent
    agent = create_comprehensive_agent()
    
    # Create session
    session_service = InMemorySessionService()
    session_id = "review_session"
    
    await session_service.create_session(
        app_name=config.APP_NAME,
        user_id=config.DEFAULT_USER_ID,
        session_id=session_id
    )
    
    # Create runner
    runner = Runner(
        agent=agent,
        app_name=config.APP_NAME,
        session_service=session_service
    )
    
    print(f"\n{'='*70}")
    print(f"Reviewing: {file_path}")
    print(f"{'='*70}\n")
    print("[Analyzing...]")
    
    # Run review
    message = types.Content(
        parts=[types.Part(text=f"Please perform a comprehensive code review of {file_path}")]
    )
    
    report = None
    
    async for event in runner.run_async(
        user_id=config.DEFAULT_USER_ID,
        session_id=session_id,
        new_message=message
    ):
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if part.text:
                    try:
                        report = FileReviewReport.model_validate_json(part.text)
                        
                        if output_format == "json":
                            print(json.dumps(report.model_dump(), indent=2))
                        elif output_format == "markdown":
                            print_markdown_report(report)
                        else:
                            print_terminal_report(report)
                        
                    except Exception as e:
                        print(f"Error parsing report: {e}")
                        print(f"Raw response: {part.text[:500]}...")
    
    return report


def print_terminal_report(report: FileReviewReport):
    """Print report in terminal-friendly format."""
    print(f"\n{'🎯 CODE REVIEW REPORT':^70}")
    print("=" * 70)
    print(f"\n📁 File: {report.file_path}")
    print(f"🏆 Quality Grade: {report.quality_grade}")
    print(f"🔒 Security Score: {report.security_score}/100")
    print(f"📊 Functions: {report.total_functions} total, {report.functions_needing_attention} need attention")
    print(f"📈 Average Complexity: {report.average_complexity:.2f}")
    
    if report.security_issues:
        print(f"\n{'🚨 SECURITY FINDINGS':^70}")
        print("-" * 70)
        for issue in report.security_issues:
            marker = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(issue.severity, "⚪")
            print(f"\n{marker} [{issue.issue_id}] {issue.severity} (Confidence: {issue.confidence})")
            print(f"   Line {issue.line_number}: {issue.description}")
            print(f"   Fix: {issue.remediation}")
    else:
        print("\n✅ No security issues found!")
    
    if report.functions_needing_attention > 0:
        print(f"\n{'⚙️  FUNCTIONS NEEDING ATTENTION':^70}")
        print("-" * 70)
        for func in report.functions:
            if func.needs_attention:
                print(f"\n⚠️  {func.name}() - Line {func.line_number}")
                print(f"   Complexity: {func.complexity} ({func.complexity_rank})")
                print(f"   Docstring: {'✅' if func.has_docstring else '❌ Missing'}")
                print(f"   💡 {func.recommendation}")
    
    print(f"\n{'📝 SUMMARY':^70}")
    print("-" * 70)
    print(f"{report.summary}")
    
    print(f"\n{'🎯 TOP PRIORITIES':^70}")
    print("-" * 70)
    for i, priority in enumerate(report.top_priorities, 1):
        print(f"{i}. {priority}")
    
    print("\n" + "=" * 70)


def print_markdown_report(report: FileReviewReport):
    """Print report in markdown format."""
    print(f"# Code Review Report\n")
    print(f"**File:** `{report.file_path}`  ")
    print(f"**Quality Grade:** {report.quality_grade}  ")
    print(f"**Security Score:** {report.security_score}/100  ")
    print(f"**Functions:** {report.total_functions} total, {report.functions_needing_attention} need attention  ")
    print(f"**Average Complexity:** {report.average_complexity:.2f}\n")
    
    if report.security_issues:
        print("## 🚨 Security Findings\n")
        for issue in report.security_issues:
            print(f"### [{issue.issue_id}] {issue.severity} - Line {issue.line_number}\n")
            print(f"**Description:** {issue.description}  ")
            print(f"**Confidence:** {issue.confidence}  ")
            print(f"**Fix:** {issue.remediation}\n")
    
    if report.functions_needing_attention > 0:
        print("## ⚙️ Functions Needing Attention\n")
        for func in report.functions:
            if func.needs_attention:
                print(f"### `{func.name}()` - Line {func.line_number}\n")
                print(f"- **Complexity:** {func.complexity} ({func.complexity_rank})")
                print(f"- **Docstring:** {'✅ Yes' if func.has_docstring else '❌ Missing'}")
                print(f"- **Recommendation:** {func.recommendation}\n")
    
    print("## 📝 Summary\n")
    print(f"{report.summary}\n")
    
    print("## 🎯 Top Priorities\n")
    for i, priority in enumerate(report.top_priorities, 1):
        print(f"{i}. {priority}")


async def interactive_mode():
    """Run in interactive mode for multiple reviews."""
    load_dotenv()
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY not set!")
        return
    
    print("=" * 70)
    print("Code Review Agent - Interactive Mode")
    print("=" * 70)
    print("\nCommands:")
    print("  review <file_path>  - Review a file")
    print("  exit                - Exit interactive mode")
    print()
    
    while True:
        try:
            user_input = input(">>> ").strip()
            
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            if user_input.startswith("review "):
                file_path = user_input[7:].strip()
                await review_file(file_path)
            else:
                print("Unknown command. Use 'review <file_path>' or 'exit'")
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


async def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m code-review-agent.main review <file_path> [--format json|markdown|terminal]")
        print("  python -m code-review-agent.main interactive")
        return
    
    command = sys.argv[1]
    
    if command == "interactive":
        await interactive_mode()
    elif command == "review":
        if len(sys.argv) < 3:
            print("ERROR: Please specify a file path")
            return
        
        file_path = sys.argv[2]
        output_format = "terminal"
        
        if len(sys.argv) > 3 and sys.argv[3] == "--format":
            if len(sys.argv) > 4:
                output_format = sys.argv[4]
        
        await review_file(file_path, output_format)
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    asyncio.run(main())
