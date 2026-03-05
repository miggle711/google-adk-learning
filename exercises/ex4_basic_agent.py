"""
Exercise 4: Basic ADK Agent with a Tool
=======================================

Goal: Create your first ADK agent with a tool it can use.

This exercise teaches the core ADK pattern:
1. Create a TOOL (a Python function the agent can call)
2. Create an AGENT (LlmAgent with the tool)
3. Create a RUNNER to execute conversations
4. CHAT with the agent

KEY CONCEPTS:

1. TOOL = A Python function with:
   - Type hints (required!)
   - A docstring (becomes the tool description)
   - Returns a string (usually JSON)

2. AGENT = LlmAgent with:
   - name: identifier
   - model: which LLM to use
   - instruction: system prompt
   - tools: list of functions

3. RUNNER + SESSION = How you actually chat:
   - InMemorySessionService stores conversation history
   - Runner connects agent to session
   - runner.run_async() sends messages and gets responses

YOUR TASK:
1. Complete the `read_file` tool function
2. Complete the `create_file_reader_agent` function
3. Run the chat loop and ask questions about files

Run this file to test: python exercises/ex4_basic_agent.py
"""

import os
import asyncio
import json
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv


# =============================================================================
# STEP 1: Create a Tool
# =============================================================================

def read_file(file_path: str) -> str:
    """
    Read the contents of a file and return it.

    Args:
        file_path: The path to the file to read.

    Returns:
        JSON string with the file contents or an error message.
    """
    # TODO: Implement this tool
    #
    # 1. Check if file exists using Path(file_path).exists()
    # 2. If not, return json.dumps({"error": "File not found: ..."})
    # 3. Read the file contents: Path(file_path).read_text()
    # 4. Return json.dumps({"file_path": ..., "content": ...})
    #
    # Remember: Tools should NEVER raise exceptions!
    # Always return an error message as JSON instead.

    if not Path(file_path).exists():
        return json.dumps({"error": f"File not found: {file_path}"})
    try:
        content = Path(file_path).read_text()
        return json.dumps({"file_path": file_path, "content": content})
    except Exception as e:
        return json.dumps({"error": f"Error reading file: {str(e)}"})


# =============================================================================
# STEP 2: Create an Agent
# =============================================================================


def create_file_reader_agent() -> LlmAgent:
    """
    Create an LlmAgent that can read files using the read_file tool.

    Returns:
        An instance of LlmAgent configured with the read_file tool.
    """
    return LlmAgent(
        name = "file_reader",
        model = Gemini(model="gemini-2.5-flash-lite"),
        description = "An agent that can read files on the system using the read_file tool.",
        instruction = """
        You are a File Reader Agent. Your goal is to read files on the system when asked by the user. Use the read_file tool to read files. Always return the file contents in your response.""",
        tools = [read_file]
    )



# =============================================================================
# STEP 3: Run the Agent (Chat Loop)
# =============================================================================

async def chat():
    """Main chat loop to interact with the agent."""
    load_dotenv()

    if not os.getenv("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY not set!")
        print("Create a .env file with: GOOGLE_API_KEY=your-key-here")
        return

    print("=" * 60)
    print("Exercise 4: Basic ADK Agent")
    print("=" * 60)

    # Create the agent
    agent = create_file_reader_agent()

    if agent is None:
        print("\nERROR: create_file_reader_agent returned None")
        print("Hint: Implement the function and return an LlmAgent!")
        return

    print(f"\nAgent created: {agent.name}")

    # Create session service and runner
    session_service = InMemorySessionService()
    app_name = "exercise_4"
    user_id = "user_1"
    session_id = "session_1"

    # Create a session
    await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )

    # Create the runner
    runner = Runner(
        agent=agent,
        app_name=app_name,
        session_service=session_service
    )

    print("\nAgent is ready! Try asking:")
    print("  - What functions are in academic_research_assistant/tools.py?")
    print("  - Read exercises/ex1_ast.py and explain what it does")
    print("  - What's in the requirements.txt?")
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

            # Send message to agent
            message = types.Content(parts=[types.Part(text=user_input)])

            print("\n[Agent thinking...]")

            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=message
            ):
                if event.is_final_response() and event.content:
                    print("-" * 40)
                    for part in event.content.parts:
                        if part.text:
                            print(f"\nAgent: {part.text}")

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
