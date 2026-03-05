
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools.agent_tool import AgentTool
from google.genai import types

# Configure Model Retry on errors - following Kaggle pattern
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# Model configuration
DEFAULT_MODEL_NAME = "gemini-2.5-flash-lite"  

def get_model():
    """Returns the configured Gemini model."""
    return Gemini(model=DEFAULT_MODEL_NAME, retry_options=retry_config)

def create_researcher_agent() -> LlmAgent:
    """Creates the Researcher agent specialized in finding and reading papers."""
    from academic_research_assistant.tools import search_arxiv, get_pdf_text_from_url
    
    return LlmAgent(
        name="researcher",
        model=get_model(),
        description="A specialist in searching and reading academic literature.",
        instruction="""
        You are a Researcher. Your goal is to find relevant academic papers and extract key information from them.
        1. Use `search_arxiv` to find papers on a topic (arXiv has no rate limits and is very reliable).
        2. Use `get_pdf_text_from_url` to read full-text content when necessary.
        3. Summarize the findings clearly for the Lit Reviewer.
        """,
        tools=[search_arxiv, get_pdf_text_from_url]
    )

def create_lit_review_agent() -> LlmAgent:
    """Creates the Literature Reviewer agent specialized in academic writing."""
    return LlmAgent(
        name="lit_reviewer",
        model=get_model(),
        description="An expert academic writer who synthesizes research into reviews.",
        instruction="""
        You are a Literature Reviewer. Your goal is to write a high-quality academic literature review.
        1. Synthesize the findings provided by the Researcher.
        2. Organize the review logically with themes, major findings, and gaps.
        3. Maintain a formal, academic tone.
        """
    )

from pydantic import BaseModel, Field
from typing import List

class CritiqueOutput(BaseModel):
    clarity_score: int = Field(description="Score for clarity from 1 to 10")
    rigor_score: int = Field(description="Score for academic rigor from 1 to 10")
    missing_areas: List[str] = Field(description="List of specific areas or themes that are missing")
    suggestions: List[str] = Field(description="Specific suggestions for improvement")
    overall_feedback: str = Field(description="A concise summary of the critique")

def create_critique_agent() -> LlmAgent:
    """Creates the Critique agent specialized in peer review."""
    return LlmAgent(
        name="critique_agent",
        model=get_model(),
        description="A rigorous peer reviewer who evaluates academic drafts.",
        instruction="""
        You are a Peer Reviewer. Your goal is to provide critical feedback on literature review drafts.
        1. Evaluate the draft for clarity, depth, and academic rigor.
        2. Suggest specific improvements or missing areas.
        3. Be constructive but demanding.

        You MUST provide your feedback in the specified JSON format.
        """,
        output_schema=CritiqueOutput
    )

def create_pi_agent() -> LlmAgent:
    """Creates the PI (Principal Investigator) agent which orchestrates the team."""
    
    # Instantiate sub-agents and wrap them as tools
    researcher_tool = AgentTool(agent=create_researcher_agent())
    lit_reviewer_tool = AgentTool(agent=create_lit_review_agent())
    critique_tool = AgentTool(agent=create_critique_agent())
    
    return LlmAgent(
        name="pi_agent",
        model=get_model(),
        description="The orchestrator of the academic research team.",
        instruction="""
        You are the Principal Investigator (PI). You manage a team of agents to conduct research.
        Your team consists of:
        - `researcher`: Finds and summarizes academic papers.
        - `lit_reviewer`: Writes the literature review draft.
        - `critique_agent`: Provides feedback on the draft.

        Workflow:
        1. Ask the `researcher` to find and summarize papers on the user's topic.
        2. If the `researcher` reports a rate limit (429) or other errors, inform the user clearly. Do not get stuck in a retry loop if the error persists.
        3. Pass those summaries to the `lit_reviewer` to create a first draft.
        4. Pass that draft to the `critique_agent` for review.
        5. If major improvements are needed, ask the `lit_reviewer` to revise.
        6. Present the final, polished review to the user.

        Be a decisive leader and ensure the highest academic standards.
        """,
        tools=[researcher_tool, lit_reviewer_tool, critique_tool]
    )
