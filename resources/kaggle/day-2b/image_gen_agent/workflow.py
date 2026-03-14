import uuid
from google.genai import types
from .agent import image_gen_runner, session_service, image_gen_app

def check_for_approval(events):
    """Check if events contain an approval request.

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
        dict with approval details or None
    """
    for event in events: # iterate through all events
        if event.content and event.content.parts: # check if event has content
            for part in event.content.parts: # iterate through content parts
                if (
                    part.function_call
                    and part.function_call.name == "adk_request_confirmation" # check for approval request
                ):
                    return {
                        "approval_id": part.function_call.id, # identifier for the approval request
                        "invocation_id": event.invocation_id, # identifies the "bookmark" to resume from
                    }
    # if no approval request found
    return None


def create_approval_response(approval_info, approved):
    """Create approval response message."""
    confirmation_response = types.FunctionResponse(
        id=approval_info["approval_id"],
        name="adk_request_confirmation",
        response={"confirmed": approved},
    )
    return types.Content(
        role="user", parts=[types.Part(function_response=confirmation_response)]
    )


async def run_image_gen_workflow(query: str, auto_approve: bool = True):
    """
    Docstring for run_image_gen_workflow
    
    Args:
        - 
    """
    print(f"\n{'='*60}")
    print(f"User > {query}\n")

    # Generate unique session ID (identifier for the conversation)
        # Analogy:
        #  Session ID = the book (your whole conversation)
        # Invocation ID = the bookmark (exact page where you paused)
    session_id = f"order_{uuid.uuid4().hex[:8]}"

    # Create a session
        # Stores history of the conversation
        # stores paused state when waiting for user approval
    await session_service.create_session(
        app_name="image_gen_app", 
        user_id="test_user", 
        session_id=session_id
    )

    # Wrap the user query in a Content object
    query_content = types.Content(
        role="user",
        parts=[types.Part(text=query)]
    )

    # Store all events from the runner
    events = []

    # runs the agent and collects events
        # It's asynchronous because the agent might need to wait for user approval
    async for event in image_gen_runner.run_async(
        user_id="test_user", 
        session_id=session_id, 
        new_message=query_content
    ):
        events.append(event)

    # Check if approval is needed from the collected events
    approval_info = check_for_approval(events)

    # if the events indicate that approval is needed
    if not approval_info:
        # Single image generation - no approval needed
        print_image_gen_workflow_result(events)
    else:
        print("Approval requested for bulk image generation.")
        print(f"Auto-approve is set to {auto_approve}.")

        resume_events = []
        # resume the agent with the approval response
        async for event in image_gen_runner.run_async(
            user_id="test_user",
            session_id=session_id,
            new_message=create_approval_response(approval_info, auto_approve),
            invocation_id=approval_info["invocation_id"]
        ):
            resume_events.append(event)
        # Print the final result after approval
        print_image_gen_workflow_result(resume_events)



def print_image_gen_workflow_result(events):
    """Prints the final result of the image generation workflow."""
    for event in events: # iterate through all events
        if event.content and event.content.parts: # check if event has content
            for part in event.content.parts: # iterate through content parts
                if part.text: # print agent's response text
                    print(f"Agent > {part.text}\n")
                if part.function_response: # print tool function response
                    response = part.function_response.response
                    status = response.get("status")
                    images = response.get("images", [])
                    print(f"Image Generation Status: {status}")
                    if images:
                        print("Generated Images:")
                        for idx, img_url in enumerate(images, start=1):
                            print(f"  Image {idx}: {img_url}")
                    else:
                        print("No images generated.")





