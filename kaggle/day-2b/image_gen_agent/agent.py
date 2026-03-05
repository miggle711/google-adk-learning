from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools.function_tool import FunctionTool
from google.adk.apps.app import App, ResumabilityConfig
from .tools import generate_images  
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)

image_gen_agent = LlmAgent(
    name="image_gen_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""You are an image generation assistant.

    When users request images:
    1. Use generate_images with the prompt and number of images
    2. If status is 'pending', inform user that approval is required
    3. Report the final status (approved/rejected) and show images if generated
    """,
    tools =[FunctionTool(func=generate_images)]
)

image_gen_app = App(
    name="image_gen_app",
    root_agent=image_gen_agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
    )

session_service = InMemorySessionService()

image_gen_runner = Runner(
    app=image_gen_app,
    session_service=session_service,
)

