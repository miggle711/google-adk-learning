"""
FastAPI wrapper for the Academic Research Assistant.
This API exposes the multi-agent system as a REST service.
"""
import os
import asyncio
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from academic_research_assistant.agents import create_pi_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Academic Research Assistant API",
    description="Multi-agent system for automated literature reviews",
    version="1.0.0"
)

# Initialize services
session_service = InMemorySessionService()
app_name = "academic_research_assistant"

class ResearchRequest(BaseModel):
    query: str
    user_id: Optional[str] = "default_user"
    session_id: Optional[str] = None

class ResearchResponse(BaseModel):
    response: str
    session_id: str
    user_id: str

@app.post("/research", response_model=ResearchResponse)
async def conduct_research(request: ResearchRequest):
    """
    Conduct academic research on a given topic.
    
    Args:
        request: ResearchRequest containing the query and optional user/session IDs
    
    Returns:
        ResearchResponse with the final literature review and session information
    """
    if not os.getenv("GOOGLE_API_KEY"):
        raise HTTPException(status_code=500, detail="GOOGLE_API_KEY not configured")
    
    # Generate session ID if not provided
    session_id = request.session_id or f"session_{uuid.uuid4().hex[:8]}"
    user_id = request.user_id
    
    try:
        # Create session
        await session_service.create_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )
        
        # Create PI agent and runner
        pi_agent = create_pi_agent()
        runner = Runner(
            agent=pi_agent, app_name=app_name, session_service=session_service
        )
        
        # Prepare the user content
        user_content = types.Content(parts=[types.Part(text=request.query)])
        
        # Execute the agent and collect the final response
        final_response = ""
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=user_content
        ):
            if event.is_final_response() and event.content:
                for part in event.content.parts:
                    if part.text:
                        final_response = part.text
        
        return ResearchResponse(
            response=final_response,
            session_id=session_id,
            user_id=user_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring."""
    return {"status": "healthy", "service": "academic_research_assistant"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
