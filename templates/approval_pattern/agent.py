"""
Template for an agent with approval workflow capability.

HOW TO USE:
1. Update the agent name and instruction
2. Add your tools to the tools list
3. Customize the model if needed
"""

from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools.function_tool import FunctionTool
from google.adk.apps.app import App, ResumabilityConfig
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from .tools import expensive_operation


# =============================================================================
# OPTIONAL: Retry configuration for API calls
# =============================================================================
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)


# =============================================================================
# CUSTOMIZE: Your agent definition
# =============================================================================
approval_agent = LlmAgent(
    name="approval_agent",  # CUSTOMIZE: Agent name
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""You are an assistant that helps with operations requiring approval.

    When users request operations:
    1. Use the appropriate tool with the given parameters
    2. If status is 'pending', inform user that approval is required
    3. Report the final status (approved/rejected) and show results
    """,  # CUSTOMIZE: Agent instructions
    tools=[FunctionTool(func=expensive_operation)]  # CUSTOMIZE: Your tools
)


# =============================================================================
# REQUIRED: App with resumability enabled (DO NOT CHANGE)
# =============================================================================
approval_app = App(
    name="approval_app",  # CUSTOMIZE: App name
    root_agent=approval_agent,
    resumability_config=ResumabilityConfig(is_resumable=True),  # REQUIRED for approval workflow
)


# =============================================================================
# REQUIRED: Session service and runner
# =============================================================================
session_service = InMemorySessionService()

approval_runner = Runner(
    app=approval_app,
    session_service=session_service,
)
