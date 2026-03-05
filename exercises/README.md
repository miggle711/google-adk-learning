# Google ADK Learning Exercises

A progressive series of exercises to master the Google Agent Development Kit (ADK).

## 📚 Exercise Overview

### Foundation Exercises (1-3): Code Analysis Tools

These exercises teach you to work with Python code analysis tools that will be used in later agent exercises.

- **Exercise 1: Python AST Basics** (`ex1_ast.py`)
  - Learn to parse Python code and extract function information
  - Key skill: Using Python's `ast` module
  - Run: `uv run exercises/ex1_ast.py`

- **Exercise 2: Radon Complexity Analysis** (`ex2_radon.py`)
  - Measure cyclomatic complexity of Python code
  - Key skill: Running external tools via subprocess
  - Run: `uv run exercises/ex2_radon.py`

- **Exercise 3: Bandit Security Scanning** (`ex3_bandit.py`)
  - Detect security vulnerabilities in Python code
  - Key skill: Static security analysis
  - Run: `uv run exercises/ex3_bandit.py`

### ADK Fundamentals (4-7): Building Agents

These exercises teach you core ADK concepts for building intelligent agents.

- **Exercise 4: Basic ADK Agent** (`ex4_basic_agent.py`) ⭐ START HERE
  - Create your first agent with a simple tool
  - Key concepts: Tools, Agents, Runners, Sessions
  - Run: `uv run exercises/ex4_basic_agent.py`

- **Exercise 5: Multi-Agent System** (`ex5_multi_agent.py`)
  - Build specialized agents that delegate to each other
  - Key concepts: AgentTool, coordinator pattern, multi-agent orchestration
  - Run: `uv run exercises/ex5_multi_agent.py`

- **Exercise 6: Pydantic Output Schema** (`ex6_pydantic_schema.py`)
  - Get structured, validated output from agents
  - Key concepts: Pydantic models, response_schema, type safety
  - Run: `uv run exercises/ex6_pydantic_schema.py`

- **Exercise 7: Combined Review Tool** (`ex7_combined_review.py`)
  - Build a production-ready code review agent
  - Key concepts: Combining all previous concepts, production patterns
  - Run: `uv run exercises/ex7_combined_review.py`

## 🎯 Recommended Learning Path

1. **Complete Exercises 1-3** (if you haven't already)
   - These teach foundational code analysis skills
   - You'll use these tools in later exercises

2. **Exercise 4: Basic Agent** ⭐
   - Your introduction to ADK
   - Learn the core agent pattern
   - Interactive chat interface

3. **Exercise 5: Multi-Agent System**
   - Learn to build specialized agents
   - Understand delegation and coordination
   - See how agents can work together

4. **Exercise 6: Pydantic Schemas**
   - Get structured output instead of free text
   - Essential for production systems
   - Type-safe agent responses

5. **Exercise 7: Production Agent**
   - Combine everything you've learned
   - Build a real code review system
   - Production-ready patterns

## 🚀 After Completing Exercises

Once you've finished all exercises, explore the complete agent implementations:

- **Academic Research Assistant** (`academic_research_assistant/`)
  - Multi-tool agent for searching papers and extracting PDFs
  - Advanced API integrations

- **Code Review Agent** (`code-review-agent/`)
  - Full implementation combining exercises 1-7
  - Production-ready code review system

- **Simple Weather Agent** (`simple-weather-agent/`)
  - Basic API integration example

## 💡 Tips

- **Use `uv run`** to run exercises (handles virtual environment automatically)
- **Read the docstrings** - each exercise has detailed explanations
- **Complete TODO sections** - hands-on practice is key
- **Experiment** - try different prompts and see how agents respond
- **Check the code** - read the implementations to understand patterns

## 🔧 Setup

Make sure you have:
1. Python 3.12+ installed
2. Dependencies installed: `uv sync`
3. Google API key in `.env` file:
   ```
   GOOGLE_API_KEY=your-key-here
   ```

## 📖 Additional Resources

- [Google ADK Documentation](https://github.com/google/adk)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- Project proposals: `PROJECT_PROPOSALS.md`

---

**Ready to start?** Run Exercise 4:
```bash
uv run exercises/ex4_basic_agent.py
```
