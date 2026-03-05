
import os
import asyncio
import uuid
import logging
from academic_research_assistant.agents import create_pi_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv

# Enable INFO logging for ADK to see internal tool execution
logging.basicConfig(level=logging.INFO)

async def test_multi_agent_flow():
    load_dotenv()
    if not os.getenv("GOOGLE_API_KEY"):
        print("Skipping test: GOOGLE_API_KEY not set.")
        return

    print("\n--- Testing Multi-Agent Orchestration (Debug Mode) ---")
    pi_agent = create_pi_agent()
    session_service = InMemorySessionService()
    app_name = "test_app"
    user_id = "test_user"
    session_id = f"test_session_{uuid.uuid4().hex[:8]}"
    
    await session_service.create_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )
    
    runner = Runner(
        agent=pi_agent, app_name=app_name, session_service=session_service
    )
    
    test_query = "What are the key benefits of using Gemini 1.5 for long context research?"
    test_content = types.Content(parts=[types.Part(text=test_query)])
    
    print(f"Query: {test_query}")
    
    try:
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=test_content
        ):
            print(f"\n[EVENT] Type: {type(event).__name__}")
            if hasattr(event, 'content') and event.content:
                for part in event.content.parts:
                    if part.text:
                        print(f"  [Text]: {part.text}")
                    if part.thought:
                        print(f"  [Thought]: {part.thought}")
                    if hasattr(part, 'function_call') and part.function_call:
                        print(f"  [Function Call]: {part.function_call.name}")
            if event.is_final_response():
                print("  (Final Response for this iteration)")
        
        print("\n--- Test Complete ---")
    except Exception as e:
        print(f"Test failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(test_multi_agent_flow())
