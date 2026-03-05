
import os
import asyncio
import uuid
import logging
from academic_research_assistant.agents import create_pi_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv

# Optional: Configure logging to see tool calls and orchestration steps
logging.basicConfig(level=logging.INFO)

async def run_chat():
    """
    Main chat loop for the multi-agent Academic Research Assistant.
    """
    load_dotenv()
    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError("GOOGLE_API_KEY environment variable not set.")

    print("--- Academic Research Assistant (Multi-Agent) ---")
    print("Initialising the PI Agent and the research team...")
    
    # Create the agents and services
    pi_agent = create_pi_agent()
    session_service = InMemorySessionService()
    app_name = "academic_research_assistant"
    user_id = "user_1"
    session_id = f"session_{uuid.uuid4().hex[:8]}"

    # Create the session
    await session_service.create_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )
    
    # Create the runner
    runner = Runner(
        agent=pi_agent, app_name=app_name, session_service=session_service
    )
    
    print("\nSystem is ready. Type your research topic or 'exit' to quit.")
    print("-" * 50)

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit']:
                print("Ending research session.")
                break
            
            if not user_input.strip():
                continue

            print("\n[PI Agent is coordinating the team...]")
            
            # Prepare the user content
            test_content = types.Content(parts=[types.Part(text=user_input)])
            
            # Execute the runner loop
            async for event in runner.run_async(
                user_id=user_id, session_id=session_id, new_message=test_content
            ):
                # Print intermediate reasoning/logs if they are available
                # In ADK, events can represent tool use, model responses, etc.
                if event.is_final_response() and event.content:
                    print("-" * 20)
                    for part in event.content.parts:
                        if part.text:
                            print(f"\nAssistant: {part.text}")
                
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == '__main__':
    asyncio.run(run_chat())
