"""
Template workflow for handling the approval pattern.

These helper functions are GENERIC and can be used with any agent
that uses the approval pattern. You typically don't need to modify them.

Key concepts:
    - Session ID: Identifier for the conversation (the "book")
    - Invocation ID: Identifier for a paused execution (the "bookmark")
    - adk_request_confirmation: Special function call name used by ADK for approvals
"""

import uuid
from google.genai import types
from .agent import approval_runner, session_service


# =============================================================================
# GENERIC: Check if events contain an approval request (DO NOT MODIFY)
# =============================================================================
def check_for_approval(events) -> dict | None:
    """Check if events contain an approval request.

    Event structure:
        Event
        ├── content: Content object (the actual message/action)
        │   ├── role: "user" | "model" | "function"
        │   └── parts: list of Part objects
        │       ├── Part with text (agent's response)
        │       ├── Part with function_call (tool invocation)
        │       └── Part with function_response (tool result)
        ├── invocation_id: string (the "bookmark" for this execution)
        └── ... other metadata

    Args:
        events: List of events from the agent runner.

    Returns:
        dict with approval_id and invocation_id, or None if no approval needed.
    """
    for event in events:
        if event.content and event.content.parts:
            for part in event.content.parts:
                if (
                    part.function_call
                    and part.function_call.name == "adk_request_confirmation"
                ):
                    return {
                        "approval_id": part.function_call.id,
                        "invocation_id": event.invocation_id,
                    }
    return None


# =============================================================================
# GENERIC: Create approval response message (DO NOT MODIFY)
# =============================================================================
def create_approval_response(approval_info: dict, approved: bool) -> types.Content:
    """Create approval response message to send back to the agent.

    Args:
        approval_info: Dict containing approval_id and invocation_id.
        approved: Whether the user approved (True) or rejected (False).

    Returns:
        Content object to send as new_message when resuming.
    """
    confirmation_response = types.FunctionResponse(
        id=approval_info["approval_id"],
        name="adk_request_confirmation",
        response={"confirmed": approved},
    )
    return types.Content(
        role="user",
        parts=[types.Part(function_response=confirmation_response)]
    )


# =============================================================================
# CUSTOMIZE: Your workflow implementation
# =============================================================================
async def run_approval_workflow(
    query: str,
    auto_approve: bool = False,  # Default to False for safety
    user_id: str = "default_user"
) -> dict:
    """Run a workflow that may require approval.

    Args:
        query: The user's request.
        auto_approve: If True, automatically approve. If False, reject.
                      In production, you'd prompt the user here.
        user_id: Identifier for the user.

    Returns:
        dict with status and events from the workflow.
    """
    # Generate unique session ID (the "book")
    session_id = f"session_{uuid.uuid4().hex[:8]}"

    # Create session to store conversation history and paused state
    await session_service.create_session(
        app_name="approval_app",  # CUSTOMIZE: Must match your App name
        user_id=user_id,
        session_id=session_id
    )

    # Wrap query in Content object
    query_content = types.Content(
        role="user",
        parts=[types.Part(text=query)]
    )

    # Collect events from first run
    events = []
    async for event in approval_runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=query_content
    ):
        events.append(event)

    # Check if approval is needed
    approval_info = check_for_approval(events)

    if not approval_info:
        # No approval needed - return results directly
        return {
            "status": "completed",
            "events": events,
            "needed_approval": False
        }

    # Approval was requested - resume with approval decision
    # In production, you would:
    #   1. Show the user the approval request (hint from payload)
    #   2. Wait for their decision
    #   3. Set approved = user's choice

    resume_events = []
    async for event in approval_runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=create_approval_response(approval_info, auto_approve),
        invocation_id=approval_info["invocation_id"]  # Resume from bookmark
    ):
        resume_events.append(event)

    return {
        "status": "approved" if auto_approve else "rejected",
        "events": resume_events,
        "needed_approval": True
    }


# =============================================================================
# CUSTOMIZE: Helper to extract results from events
# =============================================================================
def extract_results(events) -> list[dict]:
    """Extract relevant results from events.

    Customize this to extract the data you need from your tool responses.
    """
    results = []
    for event in events:
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    results.append({"type": "text", "content": part.text})
                if part.function_response:
                    results.append({
                        "type": "function_response",
                        "content": part.function_response.response
                    })
    return results
