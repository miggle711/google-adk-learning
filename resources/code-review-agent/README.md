# Code Review Agent

A production-ready code review agent built with Google ADK that analyzes Python code for complexity, security vulnerabilities, and code quality.

## Features

- **🔍 Comprehensive Analysis**: Combines AST analysis, complexity metrics (Radon), and security scanning (Bandit)
- **🤖 Multi-Agent Architecture**: Specialized agents for complexity and security, coordinated by a master agent
- **📊 Structured Output**: Returns validated Pydantic models for easy integration
- **🎯 Actionable Recommendations**: Provides specific, prioritized fixes
- **⚡ Multiple Interfaces**: CLI, interactive mode, and programmatic API

## Installation

```bash
# Install dependencies (from project root)
uv sync

# Set up environment
cp exercises/.env code-review-agent/.env
# Add your GOOGLE_API_KEY to the .env file
```

## Usage

### CLI Mode

Review a single file:
```bash
uv run python -m code-review-agent.main review exercises/sample_vulnerable.py
```

Review with JSON output:
```bash
uv run python -m code-review-agent.main review exercises/ex1_ast.py --format json
```

Review with Markdown output:
```bash
uv run python -m code-review-agent.main review exercises/ex2_radon.py --format markdown
```

### Interactive Mode

```bash
uv run python -m code-review-agent.main interactive
```

Then use commands:
```
>>> review exercises/sample_vulnerable.py
>>> review academic_research_assistant/tools.py
>>> exit
```

### Programmatic Usage

```python
import asyncio
from code_review_agent import create_comprehensive_agent
from code_review_agent.schemas import FileReviewReport
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

async def review_code(file_path: str) -> FileReviewReport:
    agent = create_comprehensive_agent()
    
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="my_app",
        user_id="user_1",
        session_id="session_1"
    )
    
    runner = Runner(agent=agent, app_name="my_app", session_service=session_service)
    
    message = types.Content(parts=[types.Part(text=f"Review {file_path}")])
    
    async for event in runner.run_async(user_id="user_1", session_id="session_1", new_message=message):
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if part.text:
                    return FileReviewReport.model_validate_json(part.text)

# Usage
report = asyncio.run(review_code("myfile.py"))
print(f"Quality Grade: {report.quality_grade}")
print(f"Security Score: {report.security_score}")
```

## Project Structure

```
code-review-agent/
├── __init__.py         # Package exports
├── agents.py           # Agent definitions
├── config.py           # Configuration and constants
├── schemas.py          # Pydantic models
├── main.py             # CLI entry point
├── tools/              # Analysis tools
│   ├── __init__.py
│   ├── ast_tool.py     # AST analysis
│   ├── complexity_tool.py  # Radon complexity
│   ├── security_tool.py    # Bandit security
│   └── combined_tool.py    # Orchestrator
└── README.md           # This file
```

## Architecture

### Agents

1. **Complexity Agent** - Analyzes cyclomatic complexity using Radon
2. **Security Agent** - Scans for vulnerabilities using Bandit
3. **Coordinator Agent** - Delegates to specialists using AgentTool
4. **Comprehensive Agent** - Single agent with all tools and structured output (recommended)

### Tools

- `analyze_ast()` - Extract function info (names, docstrings, parameters)
- `analyze_complexity()` - Measure cyclomatic complexity
- `analyze_security()` - Scan for security issues
- `comprehensive_code_review()` - Combine all analyses

### Output Schema

```python
class FileReviewReport(BaseModel):
    file_path: str
    total_functions: int
    functions_needing_attention: int
    average_complexity: float
    security_score: int  # 0-100
    quality_grade: str  # A-F
    functions: List[FunctionInfo]
    security_issues: List[SecurityIssue]
    summary: str
    top_priorities: List[str]
```

## Configuration

Edit `config.py` to customize:

- **Model**: Change `MODEL_NAME` to use different Gemini models
- **Thresholds**: Adjust complexity thresholds (LOW=5, MEDIUM=10, HIGH=20)
- **Scoring**: Modify security score deductions
- **Patterns**: Add file patterns to include/exclude

## Quality Grading

- **A**: Excellent - No security issues, low complexity, well-documented
- **B**: Good - Minor issues, moderate complexity
- **C**: Fair - Some issues, higher complexity
- **D**: Poor - Serious security issues or very high complexity
- **F**: Critical - Multiple critical issues

## Examples

See the `exercises/` directory for example usage:
- `ex5_multi_agent.py` - Multi-agent pattern
- `ex6_pydantic_schema.py` - Structured output
- `ex7_combined_review.py` - Comprehensive review

## Development

Run tests on sample files:
```bash
uv run python -m code-review-agent.main review exercises/sample_vulnerable.py
uv run python -m code-review-agent.main review academic_research_assistant/tools.py
```

## License

See LICENSE file in project root.
